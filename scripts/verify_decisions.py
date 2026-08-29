#!/usr/bin/env python3
"""verify_decisions.py —— 决策语料账本链式 hash 校验（IR-0006 W1-D1 / ADR-0103 决策 6）

决策语料 = archive 仓 decisions/ledger.jsonl，append-only（只增不改——纠错追加
erratum 行，INV-03）。每条记录：情境→选项→决策→理由→后果 + 链式 hash
（hash = sha256(去掉 hash 字段的 canonical JSON)；prev_hash 链首为 null）。

本脚本为机械判定锚点（INV-01：无 LLM、fail-closed）：
  - 文件缺失/空 = 红（fail-closed，无"默认绿"）
  - 任一行 JSON 畸形 = 红
  - seq 不连续 / prev_hash 断链 / hash 重算不符 = 红（链断=红）
  - 必填字段（ts/context/options/decision/rationale/consequences）缺失 = 红
退出码：0=绿，1=判定红（链断/篡改），2=基础设施红（文件不可读）。
用法：python3 scripts/verify_decisions.py [--ledger decisions/ledger.jsonl]
"""
import hashlib
import json
import sys

REQUIRED = ["ts", "context", "options", "decision", "rationale", "consequences"]


def content_hash(rec: dict) -> str:
    body = {k: v for k, v in rec.items() if k != "hash"}
    canon = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def main() -> int:
    ledger = "decisions/ledger.jsonl"
    if "--ledger" in sys.argv:
        ledger = sys.argv[sys.argv.index("--ledger") + 1]
    errs = []
    try:
        with open(ledger, encoding="utf-8") as f:
            lines = [ln for ln in (l.strip() for l in f) if ln]
    except FileNotFoundError:
        print(f"FATAL 账本缺失: {ledger}（fail-closed：决策语料不得缺席）")
        return 2
    except OSError as e:
        print(f"FATAL 账本不可读: {e}")
        return 2
    if not lines:
        print("FATAL 账本为空（fail-closed：语料开始累积后不得清零）")
        return 2

    prev = None
    for i, ln in enumerate(lines, 1):
        try:
            rec = json.loads(ln)
        except json.JSONDecodeError as e:
            errs.append(f"第 {i} 行 JSON 畸形: {e}")
            break
        for k in REQUIRED:
            if k not in rec or rec[k] in (None, "", [], {}):
                errs.append(f"第 {i} 行必填字段缺失/空: {k}")
        if rec.get("seq") != i:
            errs.append(f"第 {i} 行 seq={rec.get('seq')} 不连续")
        if rec.get("prev_hash") != prev:
            errs.append(f"第 {i} 行 prev_hash 断链（期望 {prev}）")
        if rec.get("hash") != content_hash(rec):
            errs.append(f"第 {i} 行 hash 重算不符（篡改或损坏）")
        prev = rec.get("hash")

    if errs:
        for e in errs:
            print("ERR", e)
        print(f"verify_decisions: {len(errs)} 项失败——链完整性断裂")
        return 1
    print(f"OK    决策语料链完整（{len(lines)} 条，链头 {lines[-1][:0] or ''}"
          f"…hash 尾={prev[-12:] if prev else 'n/a'}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
