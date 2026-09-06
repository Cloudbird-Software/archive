#!/usr/bin/env python3
"""verify_fractures.py —— 断裂登记簿 hash 链校验（IR-0009 卡 A7；INV-03 同款，链断=红）。
用法: python scripts/verify_fractures.py [LEDGER.jsonl]   # 默认 fractures/LEDGER.jsonl
exit 0=全绿; exit 1=链断/字段缺失（fail-closed）。"""
import hashlib, json, sys

GENESIS = "0" * 64

def canon(d):
    return json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def main(path="fractures/LEDGER.jsonl"):
    prev = GENESIS
    n = 0
    errors = []
    for i, line in enumerate(open(path, encoding="utf-8")):
        line = line.strip()
        if not line:
            continue
        n += 1
        try:
            e = json.loads(line)
        except Exception as ex:
            errors.append(f"line {i+1}: JSON 解析失败 {ex}")
            continue
        got_hash = e.get("hash")
        body = {k: v for k, v in e.items() if k != "hash"}
        expect = hashlib.sha256(canon(body).encode("utf-8")).hexdigest()
        if e.get("prev_hash") != prev:
            errors.append(f"line {i+1}: prev_hash 断链（期望 {prev[:12]}…，实际 {str(e.get('prev_hash'))[:12]}…）")
        if got_hash != expect:
            errors.append(f"line {i+1}: hash 不匹配（条目被篡改或 hash 计算口径漂移）")
        prev = got_hash
    if errors:
        for m in errors:
            print("FAIL", m)
        print(f"verify: {n} 行，{len(errors)} 错误 —— 链断（fail-closed）")
        return 1
    print(f"verify: {n} 行全部通过，链头={prev[:16]}…")
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))
