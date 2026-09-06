#!/usr/bin/env python3
"""neg-scan.py —— 复活钩子（半自动 v1）：遍历 active 条目，trigger_events 命中→候选清单。
用法: python neg-scan.py --events model_switch,provider_change
输出: 候选清单（stdout）+ 候选数（供 evidence 落行）。零候选也输出"零候选"行（缺席即记录）。"""
import sys, glob
import yaml

def main(argv):
    evs = set()
    for a in argv:
        if a == "--events": continue
        evs |= set(a.split(","))
    cands = []
    for f in sorted(glob.glob("neg-results/NEG-*.yaml")):
        e = yaml.safe_load(open(f, encoding="utf-8"))
        if e.get("status") != "active": continue
        te = set((e.get("expiry_condition") or {}).get("trigger_events") or [])
        if te & evs:
            cands.append((e["id"], e["title"], sorted(te & evs), (e.get("expiry_condition") or {}).get("predicates")))
    print(f"neg-scan: 事件={sorted(evs)}，候选={len(cands)}")
    for cid, title, hit, preds in cands:
        print(f"  CANDIDATE {cid}: {title}（命中: {hit}；谓词待人工评估: {preds}）")
    if not cands:
        print("  零候选")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
