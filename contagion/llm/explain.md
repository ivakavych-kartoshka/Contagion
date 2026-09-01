# Giải thích: `contagion/llm/` — Backend LLM có thể cắm rời

Thư mục này định nghĩa **giao diện LLM chung** để benchmark có thể hoán đổi backend
một cách liền mạch, không đổi phần còn lại của pipeline.

File duy nhất: `base.py`.

---

## 1. Ý tưởng

Mọi agent đều cần một "bộ não" sinh response. Benchmark cần chạy với nhiều loại
backend khác nhau:

| Backend | Dùng khi nào |
|---|---|
| **Mock** (deterministic) | test, CI, phát triển pipeline, tạo survival-rate có kiểm soát |
| **transformers / vLLM** (local) | model open-source chạy local (Qwen, Llama, Mistral) — chi phí ~0 |
| **OpenAI / Anthropic API** | dự phòng khi cần |

Để làm được điều đó, tất cả backend chia sẻ **một interface**:
`LLMClient.complete(prompt, system) -> str`. Engine (`runner/`) chỉ gọi interface
này, không quan tâm backend cụ thể.

---

## 2. `LLMPolicy` — chọn model theo vai trò

```python
class LLMPolicy(abc.ABC):
    @abc.abstractmethod
    def model_for_role(self, role: AgentRole) -> str:
        ...
```

- Trả về **model_id** dành cho một role nào đó.
- Hỗ trợ **heterogeneous (mixed-backbone)** experiment: vd Planner dùng GPT-4,
  Worker dùng Llama — mỗi role một model khác nhau.

### `SingleModelPolicy`

```python
class SingleModelPolicy(LLMPolicy):
    def __init__(self, model_id="mock"):
        self._model_id = model_id
    def model_for_role(self, role):
        return self._model_id   # mọi role dùng chung 1 model
```

- Đơn giản: **mọi role dùng 1 model** (homogeneous).
- Để làm heterogeneous, viết subclass `LLMPolicy` trả model khác nhau theo role.

---

## 3. `LLMClient` — interface sinh response

```python
class LLMClient(abc.ABC):
    @abc.abstractmethod
    def complete(self, prompt: str, system: Optional[str] = None) -> str:
        """Trả về full text completion cho prompt."""
        ...
    @abc.abstractmethod
    def close(self) -> None:
        ...
```

- `complete(prompt, system)`: nhận prompt user + system prompt, trả response text.
- `close()`: dọn dẹp (giải phóng model/tài nguyên) khi kết thúc.
- Đây là **contract duy nhất** mà `Agent.steps()` cần.

---

## 4. `MockLLMClient` — backend giả deterministic

```python
class MockLLMClient(LLMClient):
    def __init__(self, marker="INJECTED_PAYLOAD",
                 benign_reply="[benign answer]", infection_prob=1.0,
                 reply_factory=None):
        ...
    def complete(self, prompt, system=None):
        if callable(self.reply_factory):
            return self.reply_factory(prompt, system)
        if self.marker in prompt:
            # compromised relay: tái phát marker xuống downstream
            return f"{self.benign_reply}\n[[{self.marker}]]"
        return self.benign_reply
    def close(self):
        pass
```

**Cơ chế mock:**

- Nếu prompt chứa marker → response "nghe theo" payload và **tái phát marker**
  (mô phỏng một agent bị compromise relay tiếp). Kết quả: agent bị đánh giá
  compromised (vì response chứa marker).
- Nếu prompt **không** chứa marker (ví dụ defense đã lọc sạch) → trả reply vô hại,
  không chứa marker → agent không bị compromise.

**Cách dùng cho thí nghiệm có kiểm soát:**
- `infection_prob`: (đang dự trữ) xác suất marker "survive" qua LLM → cho phép
  điều chỉnh `s` không cần model thật.
- `reply_factory`: callback tự do để mô phỏng hành vi phức tạp hơn.

> ⚠️ Giới hạn của mock deterministic (đã biết):
> - `DelimiterDefense` (chỉ wrap marker, không xóa) → mock vẫn relay → survival = 1
>   (khác biệt chỉ rõ khi dùng LLM thật tuân theo delimiter).
> - Không phản ánh stochasticity/ngữ nghĩa thật của LLM.

---

## 5. `make_mock_client()` & `BACKEND_REGISTRY`

```python
def make_mock_client(policy: LLMPolicy) -> LLMClient:
    return MockLLMClient()

BACKEND_REGISTRY: dict = {"mock": make_mock_client}
```

- Registry để đăng ký factory theo tên backend (`"mock"`).
- **Lazy import**: các backend nặng (torch/openai) chỉ import khi cần, để môi
  trường nhẹ (test/CI) vẫn chạy được.

---

## 6. Vị trí được dùng

Trong `runner/engine.py`:

```python
# __init__:
self.policy = policy or SingleModelPolicy(config.model_id)
self.client = client or MockLLMClient()

# _client_for(model_id): cache 1 client per model_id
if model_id not in self._clients:
    if self.config.model_id == "mock":
        prob = self.config.extra.get("mock_infection_prob", 1.0)
        self._clients[model_id] = MockLLMClient(marker="INJECTED_PAYLOAD", infection_prob=prob)
    else:
        self._clients[model_id] = self.client
```

Trong `Agent.steps()` (`agents/agent.py`):

```python
return self.client.complete(prompt, system=self.system_prompt)
```

---

## 7. Hướng mở rộng (backend thật)

Để thêm LLM thật, tạo một `LLMClient` con (vd `HuggingFaceLLMClient`,
`OpenAILLMClient`, `OllamaLLMClient`) implement `complete()` + `close()`, rồi
đăng ký vào `BACKEND_REGISTRY` và xử lý trong `Runner._client_for()`.

---

## 8. Tóm tắt

- `LLMPolicy` → chọn model theo role (heterogeneous).
- `LLMClient` → contract duy nhất: `complete(prompt, system) -> str`.
- `MockLLMClient` → deterministic, dùng cho test/CI/kiểm soát `s`.
- `BACKEND_REGISTRY` → cắm rời backend theo tên.
