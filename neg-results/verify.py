#!/usr/bin/env python3
"""verify.py —— 负结果库台账链校验（链断=红）。"""
import hashlib, json, sys

def main(path="neg-results/LEDGER.jsonl"):
    prev = "0" * 64; errs = []; n = 0
    for i, line in enumerate(open(path, encoding="utf-8")):
        line = line.strip()
        if not line: continue
        n += 1
        e = json.loads(line)
        exp = hashlib.sha256(json.dumps({k: v for k, v in e.items() if k != "hash"},
                                        ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if e.get("prev_hash") != prev: errs.append(f"line {i+1}: prev 断链")
        if e.get("hash") != exp: errs.append(f"line {i+1}: hash 不匹配")
        prev = e["hash"]
    if errs:
        [print("FAIL", m) for m in errs]; return 1
    print(f"neg-ledger verify: {n} 行全绿，链头={prev[:16]}…")
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))
