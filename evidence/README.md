# evidence/ —— 统一证据账本·判定层载体（IR-0006 W1-B1 / ADR-0103）

> schema：`.github` 仓 `standards/evidence/record.schema.yaml`（`cloudbird/evidence-standard/record@1`）

## 布局

```
evidence/
  ledger.jsonl          # 判定层账本（append-only + 链式 hash，INV-03）
  checkpoints/
    YYYY-MM.json        # 月度锚点（BEH-02）：当月链头 hash + 记录数
```

## 纪律

- **唯一写入路径**：`scripts/write_evidence.py`（手改 ledger.jsonl=链断，CI 复算必红）。
  payload 内联 >4096 字节拒写（AC-3a）；`subject.tenant`/`subject.card` 必填（AC-3c/AC-4）。
- **独立复算**：`scripts/verify_evidence.py`（INV-01 机械锚点，不信任写入器自报）——
  seq/prev_hash/hash 复算、必填字段、4KB 复检、checkpoint 对账；任一断裂=红（AC-3b）。
- **append-only**：行内禁改；纠错追加 `action: evidence-erratum` 事件指向被纠 seq。
- **checkpoint 前进性**：月内滚动前移（落记录的同一 PR 内执行 `--checkpoint`），
  不可回拨；跨月新月文件自然开链。
- 大数据走轨迹层 `payload_ref`（sha256+store+retention，W1-B3 协议），git 侧零本体。

## 写入示例

```bash
python3 scripts/write_evidence.py --event ev.json        # 追加判定记录
python3 scripts/write_evidence.py --checkpoint           # 刷新当月锚点（同一 PR 内）
python3 scripts/verify_evidence.py                       # 独立复算（CI 同款）
```
