#!/usr/bin/env python3
"""write_evidence.py —— 统一证据账本·判定层唯一合法写入器（IR-0006 W1-B1 / ADR-0103）

判定层 = evidence/ledger.jsonl（append-only，INV-03；纠错追加 erratum 事件，
行内禁改）。记录 schema = .github 仓 standards/evidence/record.schema.yaml v1
（cloudbird/evidence-standard/record@1）。

写入执法（fail-closed，逐项拒写）：
  - payload 内联上限 4096 字节（UTF-8 编码长度）——超限拒写（INV-06 / AC-3a）
  - subject.tenant 必填（宪法 §14a / AC-3c）
  - subject.card 必填（三源统一查询 join key，AC-4）
  - kind ∈ {gate, cost, approval, decision}（BEH-01）
  - actor.identity / actor.role 必填；LLM 判定 model 非 null 时必填字符串
  - 事件输入不得自带 seq/prev_hash/hash（链字段由本写入器独占计算）
链式 hash：hash = sha256(去掉 hash 字段的 canonical JSON)；prev_hash 续接
当前链尾（首条 null）。

用法：
  python3 scripts/write_evidence.py --event ev.json [--ledger evidence/ledger.jsonl]
  python3 scripts/write_evidence.py --checkpoint [--ledger evidence/ledger.jsonl]
      [--checkpoints evidence/checkpoints]
      （--checkpoint：写当月 checkpoint <dir>/YYYY-MM.json：
        当月链头 hash + 记录数，BEH-02 月度锚点；已存在则覆盖前先校验旧值
        与链一致——checkpoint 只能前进）
退出码：0=写入成功，1=事件非法（拒写），2=基础设施错误（账本不可读）。
"""
import datetime
import hashlib
import json
import os
import re
import sys

PAYLOAD_LIMIT = 4096
KINDS = {"gate", "cost", "approval", "decision"}
ROLES = {"owner", "agent", "bot", "human"}
CHAIN_FIELDS = {"seq", "prev_hash", "hash"}


def content_hash(rec: dict) -> str:
    body = {k: v for k, v in rec.items() if k != "hash"}
    canon = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def now_utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_ledger(path: str):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [ln for ln in (l.strip() for l in f) if ln]


def validate_event(ev: dict) -> None:
    """事件字段执法（拒绝前于写盘——非法输入零副作用）。"""
    bad = CHAIN_FIELDS & set(ev)
    if bad:
        raise ValueError(f"链字段 {sorted(bad)} 由写入器独占计算，事件不得自带")
    if ev.get("kind") not in KINDS:
        raise ValueError(f"kind 非法: {ev.get('kind')!r}（合法值 {sorted(KINDS)}）")
    if not str(ev.get("action") or "").strip():
        raise ValueError("action 必填（事件名）")
    if not str(ev.get("verdict") or "").strip():
        raise ValueError("verdict 必填（判定结论）")
    subject = ev.get("subject")
    if not isinstance(subject, dict):
        raise ValueError("subject 必填（对象）")
    if not str(subject.get("tenant") or "").strip():
        raise ValueError("subject.tenant 必填（宪法 §14a 多租户计量分离，AC-3c）")
    card = str(subject.get("card") or "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[0-9]+", card):
        raise ValueError("subject.card 必填且形如 owner/repo#issue（AC-4 join key）")
    actor = ev.get("actor")
    if not isinstance(actor, dict):
        raise ValueError("actor 必填（对象）")
    if not str(actor.get("identity") or "").strip():
        raise ValueError("actor.identity 必填")
    if actor.get("role") not in ROLES:
        raise ValueError(f"actor.role 非法: {actor.get('role')!r}")
    model = actor.get("model", None)
    if model is not None and not str(model).strip():
        raise ValueError("actor.model 非 null 时须为非空字符串（gen_ai.request.model）")
    payload = ev.get("payload", None)
    if payload is not None:
        if not isinstance(payload, str):
            raise ValueError("payload 须为字符串或 null")
        if len(payload.encode("utf-8")) > PAYLOAD_LIMIT:
            raise ValueError(
                f"payload 内联 {len(payload.encode('utf-8'))} 字节 > 上限 {PAYLOAD_LIMIT}"
                "（INV-06/AC-3a：超限拒写——大数据走轨迹层 payload_ref）"
            )
    ref = ev.get("payload_ref", None)
    if ref is not None:
        if not isinstance(ref, dict) or "sha256" not in ref or "store" not in ref:
            raise ValueError("payload_ref 须含 sha256+store（W1-B3 轨迹层指针）")
        if not ref.get("sha256") or not str(ref["sha256"]).strip():
            raise ValueError("payload_ref.sha256 必填")
        if not str(ref.get("store") or "").strip():
            raise ValueError("payload_ref.store 必填")


def write_event(ev: dict, ledger: str) -> dict:
    validate_event(ev)
    lines = read_ledger(ledger)
    rec = dict(ev)
    rec["seq"] = len(lines) + 1
    rec["prev_hash"] = json.loads(lines[-1])["hash"] if lines else None
    rec["hash"] = content_hash(rec)
    # 注：null 字段（如首条 prev_hash / 非 LLM 判定 model）按 schema 保留显式 null
    os.makedirs(os.path.dirname(ledger) or ".", exist_ok=True)
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
    return rec


def write_checkpoint(ledger: str, checkpoints_dir: str) -> str:
    """月度 checkpoint（BEH-02）：当月链头 hash + 记录数。只可前进：
    已存在的当月 checkpoint 若与账本现状不符=红（不可回拨）。"""
    lines = read_ledger(ledger)
    if not lines:
        print("FATAL 账本为空——无 checkpoint 可写（fail-closed）", file=sys.stderr)
        return ""
    month = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m")
    head = json.loads(lines[-1])
    os.makedirs(checkpoints_dir, exist_ok=True)
    path = os.path.join(checkpoints_dir, f"{month}.json")
    cur = {"month": month, "head_hash": head["hash"], "count": head["seq"], "generated_at": now_utc()}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
        old_count = old.get("count")
        if not isinstance(old_count, int) or old_count > cur["count"]:
            raise ValueError(f"checkpoint 不可回拨: 旧 count={old_count} 新 count={cur['count']}")
        if old_count == cur["count"] and old.get("head_hash") != cur["head_hash"]:
            raise ValueError("checkpoint 同位不同链头（篡改迹象——fail-closed）")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cur, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return path


def main() -> int:
    ledger = "evidence/ledger.jsonl"
    if "--ledger" in sys.argv:
        ledger = sys.argv[sys.argv.index("--ledger") + 1]
    ckpt_dir = "evidence/checkpoints"
    if "--checkpoints" in sys.argv:
        ckpt_dir = sys.argv[sys.argv.index("--checkpoints") + 1]
    try:
        if "--checkpoint" in sys.argv:
            path = write_checkpoint(ledger, ckpt_dir)
            if not path:
                return 2
            print(f"OK    checkpoint 落盘: {path}")
            return 0
        if "--event" not in sys.argv:
            print("用法: write_evidence.py --event ev.json | --checkpoint [--ledger …]", file=sys.stderr)
            return 2
        ev_path = sys.argv[sys.argv.index("--event") + 1]
        with open(ev_path, encoding="utf-8") as f:
            ev = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL 事件文件不可读: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"FATAL {e}", file=sys.stderr)
        return 2
    try:
        rec = write_event(ev, ledger)
    except ValueError as e:
        print(f"REJECT 拒写: {e}", file=sys.stderr)
        return 1
    print(f"OK    判定记录 #{rec['seq']} 已追加（hash 尾={rec['hash'][-12:]}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
