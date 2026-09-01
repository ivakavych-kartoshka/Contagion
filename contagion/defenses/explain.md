# Giải thích: `contagion/defenses/` — Cơ chế phòng vệ tại trust boundary

Thư mục này định nghĩa các **defense mechanism** áp dụng tại mỗi *trust boundary*
(giữa hai agent). Mỗi defense biến đổi nội dung upstream không tin cậy trước khi
nó được ghép vào prompt của agent nhận.

File duy nhất: `mechanisms.py`.

---

## 1. Ý tưởng chính

Mỗi *hop* giữa hai agent là một trust boundary. Defense là "hàng rào" tại điểm đó:

```
upstream untrusted content
        │
        ▼
defense.sanitize(content)  →  (safe_content, detected_flag)
        │
        ▼
safe_content được ghép vào prompt của agent nhận
```

Mục tiêu: làm giảm **per-hop survival rate `s`** (xác suất payload sống sót qua
hop) xuống dưới **epidemic threshold** (`R0 < 1`).

**Quan trọng:** defense *placement* (agent nào được harden) do runner/config quyết
định — file này chỉ cung cấp "công cụ", không quyết định vị trí.

---

## 2. Giao diện chung

```python
class Defense(abc.ABC):
    type: DefenseType
    @abc.abstractmethod
    def sanitize(self, untrusted: str) -> Tuple[str, bool]:
        """Return (sanitized_content, detected_flg)."""
```

Mọi defense trả về **2 giá trị**:
1. `sanitized_content`: nội dung sau khi xử lý (an toàn hơn).
2. `detected_flg`: có phát hiện payload trong nội dung hay không.

`Agent.steps()` dùng giá trị thứ nhất (nội dung đã làm sạch), còn runner có thể
dùng `detected_flg` cho các thống kê về phát hiện.

---

## 3. `NoDefense` — không phòng vệ (baseline)

```python
def sanitize(self, untrusted):
    return untrusted, False     # giữ nguyên, không phát hiện gì
```

Baseline: mọi thứ đi qua nguyên vẹn → đây là "no defense" dùng để so sánh.

---

## 4. `ParaphraseDefense` — diễn đạt lại

```python
def sanitize(self, untrusted):
    detected = self.marker in untrusted
    if not detected:
        return untrusted, False
    stripped = untrusted.replace(self.marker, "")   # bỏ marker (giả định mất ý đồ)
    return stripped, True
```

- Ý tưởng: nội dung upstream được đánh dấu là không tin cậy và yêu cầu LLM
  *diễn đạt lại* (paraphrase), làm giảm khả năng điều khiển của attacker.
- Tham số `retention` (mặc định 0.3) biểu diễn xác suất ý đồ tấn công **sống sót**
  sau paraphrase (mô hình hóa mức độ hiệu quả).
- Trong mock: `paraphrase` được mô phỏng bằng cách **bỏ marker** khỏi content
  (nội dung mất "chìa khóa" → response không còn marker → không bị đánh giá compromise).
- Với LLM thật: đây sẽ là một lời gọi `llm.paraphrase(content)` thực sự.

---

## 5. `DelimiterDefense` — cô lập bằng delimiter / structured input

```python
def sanitize(self, untrusted):
    detected = self.marker in untrusted
    wrapped = f"<untrusted>\n{untrusted}\n</untrusted>"
    return wrapped, detected
```

- Nội dung untrusted bị nhốt trong block tường minh:
  ```
  <untrusted>
  ... content ...
  </untrusted>
  ```
- Ý tưởng: LLM được (hy vọng) nhận diện đây là **dữ liệu**, không phải lệnh
  → giảm `content_freedom` của field.
- Liên hệ **InjecAgent**: content-freedom thấp hơn → attack success thấp hơn.
- ⚠️ Lưu ý: với mock hiện tại, marker vẫn còn nguyên trong block → mock vẫn relay
  (survival = 1). Khác biệt thực sự xuất hiện khi dùng LLM thật tuân theo delimiter.

---

## 6. `DetectionDefense` — bộ phát hiện dạng rule (gate)

```python
def sanitize(self, untrusted):
    detected = self.marker in untrusted
    if detected and self.block:
        return "[BLOCKED — untrusted content dropped]", True
    return untrusted, detected
```

- Nếu phát hiện marker và `block=True` → thay toàn bộ bằng chuỗi BLOCKED.
- Đóng vai trò *phát hiện + chặn* (rule-based detector).

---

## 7. `HopIsolationDefense` — cô lập hop (drop toàn bộ)

```python
def sanitize(self, untrusted):
    return "", self.marker in untrusted
```

- **Loại bỏ hoàn toàn** nội dung upstream không tin cậy tại boundary.
- Đây là defense mạnh nhất về cắt lan truyền, nhưng đồng thời **mất tiện ích**
  (agent không nhận được thông tin upstream → giảm utility). Thích hợp để so sánh
  utility-vs-security.

---

## 8. `DEFENSE_REGISTRY` & `build_defense()` — factory

```python
DEFENSE_REGISTRY = {
    DefenseType.NONE:          lambda **kw: NoDefense(),
    DefenseType.PARAPHRASE:    lambda **kw: ParaphraseDefense(**kw),
    DefenseType.DELIMITER:     lambda **kw: DelimiterDefense(**kw),
    DefenseType.DETECTION:     lambda **kw: DetectionDefense(**kw),
    DefenseType.HOP_ISOLATION: lambda **kw: HopIsolationDefense(**kw),
}

def build_defense(typ: DefenseType, **kwargs) -> Defense:
    return DEFENSE_REGISTRY[typ](**kwargs)
```

- Map `DefenseType` → hàm tạo instance.
- Runner gọi `build_defense(config.defense)` để gán defense cho từng agent.

---

## 9. Vị trí được dùng

Trong `runner/engine.py`:

```python
# _build_agents():
defense = build_defense(self.config.defense)
agents[aid] = make_agent(aid, role, defense, client, ...)

# Trong Agent.steps() (agents/agent.py):
safe, detected = self.defense.sanitize(msg.to_untrusted_field())
```

---

## 10. Liên hệ nghiên cứu

- Defense-placement study: benchmark đánh giá **agent nào cần được harden** để đạt
  hiệu quả cao nhất (so sánh `s` giảm khi đặt defense ở các vị trí khác nhau).
- Mục tiêu: hạ `R0_effective < 1` (subcritical) với chi phí thấp nhất.
- **Caveat**: giảm lan truyền (defense) không đảm bảo "network secure" — chỉ là
  đưa về trạng thái subcritical (proof obligation).
