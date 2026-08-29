#!/usr/bin/env python3
"""verify_evidence.py —— 统一证据账本·判定层独立复算（IR-0006 W1-B1 / ADR-0103）

机械判定锚点（INV-01：无 LLM、fail-closed——不信任写入器自报数字）：
  - 账本缺失/空 = 红（判定层不得缺席）
  - 任一行 JSON 畸形 / seq 不连续 / prev_hash 断链 / hash 重算不符 = 红（链断=红，AC-3b）
  - 必填字段缺失（subject.tenant / subject.card / kind 域 / actor 四元） = 红
  - payload 内联 >4096 字节 = 红（写入器漏执法也要被复算抓住，AC-3a）
  - checkpoint 与链不符 = 红（BEH-02：每个已存 checkpoint 的 count 位记录 hash
    必须等于其 head_hash；count 必须单调不减——月内滚动前移、不可回拨）
退出码：0=绿，1=判定红（链断/篡改/执法缺口），2=基础设施红（文件不可读）。
用法：python3 scripts/verify_evidence.py [--ledger evidence/ledger.jsonl]
"""
import hashlib
import json
import sys

PAYLOAD_LIMIT = 4096
KINDS = {"gate", "cost", "approval", "decision"}
ROLES = {"owner", "agent", "bot", "human"}
REQUIRED = ["seq", "ts", "kind", "action", "verdict", "subject", "actor", "prev_hash", "hash"]


def content_hash(rec: dict) -> str:
    body = {k: v for k, v in rec.items() if k != "hash"}
    canon = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def check_record(i: int, rec: dict, prev) -> list:
    errs = []
    for k in REQUIRED:
        if k not in rec:
            errs.append(f"第 {i} 行必填字段缺失: {k}")
    if errs:
        return errs
    if rec["seq"] != i:
        errs.append(f"第 {i} 行 seq={rec['seq']} 不连续")
    if rec["prev_hash"] != prev:
        errs.append(f"第 {i} 行 prev_hash 断链（期望 {prev}）")
    if rec["hash"] != content_hash(rec):
        errs.append(f"第 {i} 行 hash 重算不符（篡改或损坏）")
    if rec["kind"] not in KINDS:
        errs.append(f"第 {i} 行 kind 非法: {rec['kind']!r}")
    subject = rec["subject"]
    if not isinstance(subject, dict):
        errs.append(f"第 {i} 行 subject 非对象")
    else:
        if not str(subject.get("tenant") or "").strip():
            errs.append(f"第 {i} 行 subject.tenant 缺失/空（宪法 §14a / AC-3c）")
        if not str(subject.get("card") or "").strip():
            errs.append(f"第 {i} 行 subject.card 缺失/空（AC-4 join key）")
    actor = rec["actor"]
    if not isinstance(actor, dict):
        errs.append(f"第 {i} 行 actor 非对象")
    else:
        if not str(actor.get("identity") or "").strip():
            errs.append(f"第 {i} 行 actor.identity 缺失/空")
        if actor.get("role") not in ROLES:
            errs.append(f"第 {i} 行 actor.role 非法: {actor.get('role')!r}")
    payload = rec.get("payload", None)
    if payload is not None:
        if not isinstance(payload, str):
            errs.append(f"第 {i} 行 payload 非字符串")
        elif len(payload.encode("utf-8")) > PAYLOAD_LIMIT:
            errs.append(f"第 {i} 行 payload {len(payload.encode('utf-8'))} 字节 > {PAYLOAD_LIMIT}（AC-3a）")
    return errs


def main() -> int:
    argv = sys.argv
    ledger = "evidence/ledger.jsonl"
    if "--ledger" in argv:
        ledger = argv[argv.index("--ledger") + 1]
    ckpt_dir = "evidence/checkpoints"
    if "--checkpoints" in argv:
        ckpt_dir = argv[argv.index("--checkpoints") + 1]

    try:
        with open(ledger, encoding="utf-8") as f:
            lines = [ln for ln in (l.strip() for l in f) if ln]
    except FileNotFoundError:
        print(f"FATAL 账本缺失: {ledger}（fail-closed：判定层不得缺席）")
        return 2
    except OSError as e:
        print(f"FATAL 账本不可读: {e}")
        return 2
    if not lines:
        print("FATAL 账本为空（fail-closed：开始累积后不得清零）")
        return 2

    recs, errs = [], []
    for i, ln in enumerate(lines, 1):
        try:
            recs.append(json.loads(ln))
        except json.JSONDecodeError as e:
            errs.append(f"第 {i} 行 JSON 畸形: {e}")
            recs.append(None)
    prev = None
    for i, rec in enumerate(recs, 1):
        if rec is None:
            prev = None
            continue
        errs.extend(check_record(i, rec, prev))
        prev = rec.get("hash")

    # ---- checkpoint 对账（BEH-02）----
    import glob
    import os
    ckpts = sorted(glob.glob(os.path.join(ckpt_dir, "*.json")))
    last_count = 0
    for path in ckpts:
        try:
            with open(path, encoding="utf-8") as f:
                ck = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            errs.append(f"checkpoint {path} 不可读: {e}")
            continue
        c = ck.get("count")
        h = ck.get("head_hash")
        if not isinstance(c, int) or c < 1 or c > len(recs):
            errs.append(f"checkpoint {path} count 非法: {c}（链长 {len(recs)}）")
            continue
        if c < last_count:
            errs.append(f"checkpoint {path} count 回拨: {c} < 前值 {last_count}")
        last_count = max(last_count, c)
        at = recs[c - 1]
        if at is None:
            errs.append(f"checkpoint {path} 指向损坏行 #{c}")
        elif at.get("seq") != c or at.get("hash") != h:
            errs.append(f"checkpoint {path} 与链不符: #{c} hash={h}（链断=红，AC-3b）")

    if errs:
        for e in errs:
            print("ERR", e)
        print(f"verify_evidence: {len(errs)} 项失败——判定层完整性断裂")
        return 1
    print(f"OK    证据账本链完整（{len(recs)} 条，链尾 hash={prev[-12:]}，"
          f"checkpoint×{len(ckpts)} 对账一致）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
