#!/usr/bin/env python3
"""new_entry.py —— 负结果登记（fail-closed）。用法: python new_entry.py <entry.yaml>"""
import hashlib, json, sys, datetime
import yaml

REQUIRED = ["id", "title", "conclusion", "reason", "capability_version", "environment_conditions",
            "expiry_condition", "evidence", "status", "registered_at"]
TRIGGERS = {"model_switch", "provider_change", "workload_change", "environment_change"}

def main(path):
    e = yaml.safe_load(open(path, encoding="utf-8"))
    for k in REQUIRED:
        if not e.get(k):
            print(f"FAIL 缺必填字段: {k}"); return 1
    ec = e["expiry_condition"]
    if not ec.get("trigger_events") or not set(ec["trigger_events"]) <= TRIGGERS:
        print(f"FAIL trigger_events 非法（须 ⊆ {sorted(TRIGGERS)}）"); return 1
    if not ec.get("predicates"):
        print("FAIL predicates ≥1"); return 1
    if not e["evidence"]:
        print("FAIL evidence ≥1"); return 1
    ledger = "neg-results/LEDGER.jsonl"
    try:
        lines = [l for l in open(ledger, encoding="utf-8") if l.strip()]
        prev = json.loads(lines[-1])["hash"]
        seq = json.loads(lines[-1])["seq"] + 1
    except FileNotFoundError:
        prev = "0" * 64; seq = 1
    rec = {"seq": seq, "file": path.replace("\\", "/"), "registered_at": e["registered_at"],
           "prev_hash": prev}
    body = json.dumps({"entry": {k: e[k] for k in e if k not in ("prev_hash",)}, "rec": rec},
                      ensure_ascii=False, sort_keys=True)
    rec["entry_hash"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    hh = hashlib.sha256(json.dumps(rec, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    rec["hash"] = hh
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    print("APPENDED", rec["seq"], rec["entry_hash"][:12])
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
