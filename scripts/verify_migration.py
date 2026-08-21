#!/usr/bin/env python3
"""verify_migration.py —— ADR 归档迁移保真校验（W1-C1 / ADR-0053 / .github#164）。

三向 sha256 闭环（AC-1"逐条 diff 校验"的机器形态）：
  (a) INDEX 每个 entry 的 archive_path 在本地 adr/ 存在且 sha256 == content_sha256；
  (b) adr/ 下无 INDEX 未登记的文件（防孤儿正本/半迁移）；
  (c) INDEX.source_commit 处 agent-registry 的源文件 sha256 == content_sha256
      （经 GitHub API contents?ref=source_commit 拉源 blob——保真闭环：
       archive 正本 ↔ 索引声明 ↔ 迁移时源 commit 三方一致）。

全部断言通过 exit 0；任一失败 exit 1（fail-closed：拉取失败≠通过）。

运行位置：archive 仓 CI（.github/workflows/verify.yml，PR+push+weekly）。
本地预验（against staging，零网络）：
  python verify_migration.py --index-file <INDEX.yaml> --adr-dir <staging>/adr \
      --source-repo <agent-registry 克隆>          # (c) 经 git show 校验
  python verify_migration.py --index-file <INDEX.yaml> --adr-dir <staging>/adr \
      --skip-source                                 # 跳过 (c)（仅本地冒烟）

CI 默认形态：
  python verify_migration.py [--index-ref main]
      # INDEX 取 raw.githubusercontent.com（agent-registry 公开仓），
      # (c) 经 api.github.com contents?ref=<source_commit>。

自检：python -m py_compile verify_migration.py
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ORG = "Cloudbird-Software"
REGISTRY = "agent-registry"
ARCHIVE_RAW = f"https://raw.githubusercontent.com/{ORG}/{REGISTRY}"
API = "https://api.github.com"

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"OK    {msg}")


def parse_index(text: str) -> dict:
    """解析 INDEX.yaml。优先 PyYAML（CI 安装）；无依赖时按生成器固定格式降级解析
    （键值缩进结构稳定——migrate_adrs.py 是唯一写者，格式漂移在 (a) 断言中暴露）。"""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ImportError:
        pass
    data: dict = {"entries": []}
    cur: dict = {}
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m_top = re.match(r"^(\w[\w.]*):\s*(.*)$", raw)
        m_ent = re.match(r"^\s+-\s+(\w[\w.]*):\s*(.*)$", raw)
        m_kv = re.match(r"^\s+(\w[\w.]*):\s*(.*)$", raw)
        if m_ent:
            if cur:
                data["entries"].append(cur)
            cur = {m_ent.group(1): _scalar(m_ent.group(2))}
        elif m_kv and cur is not None:
            cur[m_kv.group(1)] = _scalar(m_kv.group(2))
        elif m_top:
            if cur:
                data["entries"].append(cur)
                cur = {}
            data[m_top.group(1)] = _scalar(m_top.group(2))
    if cur:
        data["entries"].append(cur)
    return data


def _scalar(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_url(url: str, token: str | None) -> bytes:
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "cloudbird-verify-migration")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main() -> int:
    ap = argparse.ArgumentParser(description="ADR 归档迁移保真校验（ADR-0053）")
    ap.add_argument("--index-ref", default="main",
                    help="INDEX 的 agent-registry ref（默认 main；也可传完整 SHA）")
    ap.add_argument("--index-file", default=None,
                    help="本地 INDEX.yaml 路径（覆盖 --index-ref 的网络拉取）")
    ap.add_argument("--adr-dir", default=None,
                    help="本地 adr/ 目录（默认：脚本所在仓根的 adr/）")
    ap.add_argument("--source-repo", default=None,
                    help="本地 agent-registry 克隆路径——(c) 经 git show 校验（离线）")
    ap.add_argument("--skip-source", action="store_true",
                    help="跳过断言 (c)（仅本地冒烟；CI 禁用）")
    args = ap.parse_args()

    here = Path(__file__).resolve().parent
    adr_dir = Path(args.adr_dir) if args.adr_dir else here.parent / "adr"
    import os
    token = os.environ.get("GITHUB_TOKEN") or None

    # ── INDEX 获取（fail-closed：拉取失败即失败）──
    if args.index_file:
        text = Path(args.index_file).read_text(encoding="utf-8")
        ok(f"INDEX 来源：本地 {args.index_file}")
    else:
        url = f"{ARCHIVE_RAW}/{args.index_ref}/decisions/INDEX.yaml"
        try:
            text = fetch_url(url, token).decode("utf-8")
            ok(f"INDEX 来源：{url}")
        except Exception as e:  # noqa: BLE001——fail-closed 汇总
            err(f"INDEX.yaml 拉取失败（{url}）: {e}——fail-closed")
            print(f"\nverify_migration: {len(errors)} 项失败")
            return 1
    index = parse_index(text)
    entries = index.get("entries") or []
    source_commit = str(index.get("source_commit") or "").strip()
    if not entries:
        err("INDEX.entries 为空——迁移未发生或索引损坏")
    if not source_commit:
        err("INDEX.source_commit 缺失——(c) 源保真闭环不可执行")
    if not adr_dir.is_dir():
        err(f"adr/ 目录不存在: {adr_dir}")

    # ── (a) INDEX entry → 本地 adr/ 正本：存在且 sha256 一致 ──
    seen: set[str] = set()
    for e in entries:
        f = str(e.get("file") or "")
        p = str(e.get("archive_path") or "")
        want = str(e.get("content_sha256") or "")
        if not f or not p or not want:
            err(f"entry 字段缺失（file/archive_path/content_sha256）: {e}")
            continue
        if not p == f"adr/{f}":
            err(f"{f}: archive_path={p!r} 与约定 adr/<file> 不符")
            continue
        path = adr_dir / f
        if not path.is_file():
            err(f"{f}: archive 正本缺失（{path}）")
            seen.add(f)
            continue
        got = sha256_bytes(path.read_bytes())
        if got != want:
            err(f"{f}: archive 正本 sha256 不符（want={want[:16]}… got={got[:16]}…）——正本被改动或索引过期")
        seen.add(f)
    ok(f"(a) INDEX entries={len(entries)} 逐一校验 archive_path 存在性+sha256（失败项见上）")

    # ── (b) adr/ 无未登记文件 ──
    on_disk = {p.name for p in adr_dir.iterdir() if p.is_file()}
    orphans = sorted(on_disk - seen)
    if orphans:
        err(f"adr/ 存在 INDEX 未登记文件: {orphans}——半迁移或索引漂移")
    else:
        ok(f"(b) adr/ 共 {len(on_disk)} 文件全部已登记（零孤儿）")

    # ── (c) 源 commit 处 agent-registry 源文件 sha256 == content_sha256 ──
    if args.skip_source:
        ok("(c) 跳过（--skip-source，仅本地冒烟）")
    elif args.source_repo:
        repo = Path(args.source_repo)
        for e in entries:
            f, want = str(e.get("file") or ""), str(e.get("content_sha256") or "")
            if not f:
                continue
            proc = subprocess.run(
                ["git", "-C", str(repo), "show", f"{source_commit}:decisions/{f}"],
                capture_output=True,
            )
            if proc.returncode != 0:
                err(f"{f}: git show {source_commit[:12]}:decisions/{f} 失败——源 commit 无此文件？")
            elif sha256_bytes(proc.stdout) != want:
                err(f"{f}: 源 commit blob sha256 与 INDEX 不符——迁移后源被改动？")
        ok(f"(c) 源保真闭环（经本地 git，source_commit={source_commit[:12]}…）")
    else:
        for e in entries:
            f, want = str(e.get("file") or ""), str(e.get("content_sha256") or "")
            if not f:
                continue
            url = (f"{API}/repos/{ORG}/{REGISTRY}/contents/decisions/{f}"
                   f"?ref={source_commit}")
            try:
                blob = json.loads(fetch_url(url, token).decode("utf-8"))
                src = base64.b64decode(blob.get("content") or "")
            except Exception as ex:  # noqa: BLE001
                err(f"{f}: 源 blob 拉取失败（{url}）: {ex}——fail-closed")
                continue
            if sha256_bytes(src) != want:
                err(f"{f}: source_commit={source_commit[:12]}… 处源文件 sha256 与 INDEX 不符")
        ok(f"(c) 源保真闭环（经 GitHub API，source_commit={source_commit[:12]}…）")

    if errors:
        print(f"\nverify_migration: {len(errors)} 项失败——保真闭环断裂")
        return 1
    print("\nverify_migration: 全部通过（(a) 正本一致 (b) 零孤儿 (c) 源保真）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
