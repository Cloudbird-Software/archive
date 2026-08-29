#!/usr/bin/env python3
"""test_evidence.py —— 证据账本写入执法/链复算的判定实测（IR-0006 W1-B1 卡 #406 AC）

逐条对应卡 AC（负向实测=攻击者视角：构造非法输入，断言系统拒收/标红）：
  - AC-3a：payload >4096 字节拒写（write 返回 1）+ 复算侧抓漏（verify 标红）
  - AC-3b：注入断链（篡改行/断 prev_hash/断 seq）→ verify 必红；
            checkpoint 篡改 → verify 必红；checkpoint 回拨 → 写入器拒写
  - AC-3c：tenant 缺失拒写；写入器漏执法时复算侧仍标红
运行：python3 scripts/test_evidence.py（unittest，零第三方依赖）
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
WRITE = os.path.join(HERE, "write_evidence.py")
VERIFY = os.path.join(HERE, "verify_evidence.py")

BASE_EVENT = {
    "ts": "2026-08-29T00:00:00Z",
    "kind": "gate",
    "action": "gate.merge-verdict",
    "verdict": "pass",
    "subject": {"card": "Cloudbird-Software/.github#406", "tenant": "cloudbird-internal"},
    "actor": {"identity": "cloudbrid-agent", "role": "bot", "model": None},
    "payload": "gate 全绿",
}


def run(script: str, *args: str):
    return subprocess.run([sys.executable, script, *args], capture_output=True, text=True)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = os.path.join(self.tmp.name, "ledger.jsonl")
        self.ckpt = os.path.join(self.tmp.name, "checkpoints")

    def tearDown(self):
        self.tmp.cleanup()

    def ev(self, path: str, **overrides):
        ev = json.loads(json.dumps(BASE_EVENT))
        ev.update(overrides)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ev, f)
        return path

    def write_n(self, n: int):
        for _ in range(n):
            p = os.path.join(self.tmp.name, "ev.json")
            r = run(WRITE, "--event", self.ev(p), "--ledger", self.ledger)
            assert r.returncode == 0, r.stderr
        return r

    # ---- 正向：写+验闭环 ----
    def test_write_ok_and_verify_green(self):
        r = self.write_n(3)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run(VERIFY, "--ledger", self.ledger, "--checkpoints", self.ckpt)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    # ---- AC-3a：4KB 超限拒写（负向）----
    def test_payload_over_limit_rejected(self):
        p = self.ev(os.path.join(self.tmp.name, "ev.json"), payload="x" * 4097)
        r = run(WRITE, "--event", p, "--ledger", self.ledger)
        self.assertEqual(r.returncode, 1, "超限 payload 必须拒写（AC-3a）")
        self.assertIn("4096", r.stderr)
        self.assertFalse(os.path.exists(self.ledger), "拒写=零副作用（账本不得落盘）")

    def test_payload_at_limit_accepted(self):
        p = self.ev(os.path.join(self.tmp.name, "ev.json"), payload="x" * 4096)
        r = run(WRITE, "--event", p, "--ledger", self.ledger)
        self.assertEqual(r.returncode, 0, "恰在上限=合法边界")

    # ---- AC-3c：tenant 缺失拒写（负向）----
    def test_tenant_missing_rejected(self):
        p = self.ev(os.path.join(self.tmp.name, "ev.json"),
                    subject={"card": "Cloudbird-Software/.github#406"})
        r = run(WRITE, "--event", p, "--ledger", self.ledger)
        self.assertEqual(r.returncode, 1, "tenant 缺失必须拒写（AC-3c）")
        self.assertIn("tenant", r.stderr)

    # ---- 执法面联动：写入器漏执法，复算侧兜底 ----
    def test_oversize_payload_caught_by_verifier(self):
        self.write_n(1)
        with open(self.ledger, encoding="utf-8") as f:
            rec = json.loads(f.read().splitlines()[0])
        rec["payload"] = "y" * 5000  # 模拟绕过写入器的注入
        rec2 = json.loads(json.dumps(rec)); rec2.pop("hash")
        import hashlib
        canon = json.dumps(rec2, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        rec["hash"] = hashlib.sha256(canon.encode()).hexdigest()  # 重算合法 hash 的超限行
        with open(self.ledger, "w", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
        r = run(VERIFY, "--ledger", self.ledger, "--checkpoints", self.ckpt)
        self.assertEqual(r.returncode, 1, "复算必须抓住超限 payload（执法兜底）")

    # ---- AC-3b：断链/篡改 → verify 必红（负向）----
    def tamper_line(self, mutate):
        self.write_n(3)
        with open(self.ledger, encoding="utf-8") as f:
            lines = f.read().splitlines()
        rec = json.loads(lines[1])
        mutate(rec)
        lines[1] = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
        with open(self.ledger, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return run(VERIFY, "--ledger", self.ledger, "--checkpoints", self.ckpt)

    def test_tampered_payload_detected(self):
        r = self.tamper_line(lambda rec: rec.update(payload="被篡改"))
        self.assertEqual(r.returncode, 1, "行内篡改必须标红（append-only INV-03）")

    def test_broken_prev_hash_detected(self):
        r = self.tamper_line(lambda rec: rec.update(prev_hash="0" * 64))
        self.assertEqual(r.returncode, 1, "断链必须标红（AC-3b）")

    def test_broken_seq_detected(self):
        r = self.tamper_line(lambda rec: rec.update(seq=99))
        self.assertEqual(r.returncode, 1, "seq 断号必须标红")

    def test_deleted_middle_record_detected(self):
        self.write_n(3)
        with open(self.ledger, encoding="utf-8") as f:
            lines = f.read().splitlines()
        with open(self.ledger, "w", encoding="utf-8") as f:
            f.write("\n".join([lines[0], lines[2]]) + "\n")  # 删中间行=断链
        r = run(VERIFY, "--ledger", self.ledger, "--checkpoints", self.ckpt)
        self.assertEqual(r.returncode, 1, "删行=断链必须标红（AC-3b）")

    # ---- AC-3b：checkpoint 面（负向）----
    def test_checkpoint_tamper_detected(self):
        self.write_n(3)
        run(WRITE, "--checkpoint", "--ledger", self.ledger, "--checkpoints", self.ckpt)
        import glob
        ck = sorted(glob.glob(os.path.join(self.ckpt, "*.json")))[0]
        with open(ck, encoding="utf-8") as f:
            data = json.load(f)
        data["head_hash"] = "f" * 64  # 篡改链头
        with open(ck, "w", encoding="utf-8") as f:
            json.dump(data, f)
        r = run(VERIFY, "--ledger", self.ledger, "--checkpoints", self.ckpt)
        self.assertEqual(r.returncode, 1, "checkpoint 篡改必须标红（AC-3b）")

    def test_checkpoint_rollback_rejected(self):
        self.write_n(3)
        r = run(WRITE, "--checkpoint", "--ledger", self.ledger, "--checkpoints", self.ckpt)
        self.assertEqual(r.returncode, 0, r.stderr)
        # 模拟回拨：账本被删行（链缩短），再写 checkpoint = 新 count < 旧 count
        with open(self.ledger, encoding="utf-8") as f:
            lines = f.read().splitlines()
        with open(self.ledger, "w", encoding="utf-8") as f:
            f.write(lines[0] + "\n")
        r = run(WRITE, "--checkpoint", "--ledger", self.ledger, "--checkpoints", self.ckpt)
        self.assertEqual(r.returncode, 2, "链缩短后重写 checkpoint 必须拒写（不可回拨）")

    def test_chain_fields_rejected_in_event(self):
        p = self.ev(os.path.join(self.tmp.name, "ev.json"), seq=1)
        r = run(WRITE, "--event", p, "--ledger", self.ledger)
        self.assertEqual(r.returncode, 1, "链字段必须由写入器独占")


if __name__ == "__main__":
    unittest.main(verbosity=2)
