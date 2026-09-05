# Giải thích: `contagion/topology/graph.py` — Topology Graph Generator

File này định nghĩa **cấu trúc mạng lưới các agent**: một directed graph (đồ thị
có hướng) biểu diễn cách các agent giao tiếp với nhau. Đây là nơi quyết định
*lây lan có thể đi xa đến đâu* trong một topology nhất định.

---

## 1. Graph là gì trong mô hình Contagion?

Một **topology graph** là:

- **NODE** = một Agent (gắn role: Planner, Worker, Reviewer, ...)
- **EDGE** = một *trust boundary*: message đi từ `src` → `dst`
  - Mỗi edge tương ứng với **MỘT communication hop**
  - Và mỗi hop là **một cơ hội để injection lan truyền**

```
   +---agent_0---+---agent_1---+---agent_2---+    (CHAIN)
       Planner       Worker        Reviewer
```

Mỗi cạnh hướng `A → B` mang nghĩa: khi A bị compromise, message từ A có thể
infect B. Xác suất xảy ra = **per-hop survival rate `s`**.

---

## 2. Vì sao topology quan trọng?

Topology quyết định 3 thứ ảnh hưởng trực tiếp đến **reproduction number R0**:

1. **out_degree** của mỗi agent → `R0 ≈ out_degree × s`
2. **số trust boundary (edges)** → tổng số hop propagation có thể xảy ra
3. **cấu trúc fan-out / fan-in** → xác định vai trò *super-spreader*

Các topology được nghiên cứu:

| Topology | Cấu trúc | Điểm đặc biệt về lây lan |
|---|---|---|
| **Chain** | Linear `0 → 1 → 2 → ...` | Baseline; `P_E2E = ∏ s_i` |
| **Star** | Center + leaves, fan-in | Nhiều nguồn nhiễm đổ vào center |
| **Tree** | Balanced binary | Branching 2 → nếu `s > 0.5` thì `R0 > 1` |
| Mesh / Debate | *(scope mở rộng)* | Phức tạp hơn, chưa implement |

---

## 3. Cấu trúc file

| Phần | Mô tả |
|---|---|
| `class Connection` | Loại kết nối: FORWARD / BROADCAST / FAN_IN |
| `class Edge` | Một cạnh có hướng `src → dst` (= 1 trust boundary = 1 hop) |
| `class AgentGraph` | Đồ thị: nodes + edges + roles + parents |
| `AgentGraph.successors()` | Agent nào nhận message từ agent X |
| `AgentGraph.degree()` | Out-degree của agent |
| `build_graph()` | Factory: tạo graph theo topology + số agents |
| `_chain()`, `_star()`, `_tree()` | Hàm dựng topology cụ thể |

---

## 4. `Connection` — loại kết nối

```python
FORWARD   : A → B            # 1-1  (chain, tree)
BROADCAST : A → {B, C, D}   # 1-N  (fanout cao — broadcaster)
FAN_IN    : {A, B, C} → X   # N-1  (star center gom nhiều nguồn)
```

Loại kết nối ảnh hưởng tới khả năng lan:

- `BROADCAST`: một compromised agent có thể infect **nhiều** agent cùng lúc
  → khuếch đại propagation (super-spreader).
- `FAN_IN`: nhiều nguồn nhiễm đổ vào center → center có xác suất bị infect cao.

---

## 5. `Edge` — một trust boundary

```python
@dataclass
class Edge:
    src : str        # sender agent id
    dst : str        # receiver agent id
    conn: Connection  # FORWARD / BROADCAST / FAN_IN
```

**Mỗi Edge = MỘT hop.** Trong benchmark:

- Nếu `src` bị compromise, message qua edge này có thể infect `dst` với xác suất `s`.
- Mỗi edge được đo riêng bằng **controlled per-edge protocol** (metric.md §1):
  `run_per_edge_protocol()` ép C_src = 1 rồi judge dst qua `per_edge_trials` lần
  (→ `EdgeTrial`); `ŝ_edge = k/N`.
- Trong **natural runs**, edge chỉ sinh `HopOutcome` khi một message agent→agent
  thực sự được xử lý (metric.md §2).

---

## 6. `AgentGraph` — đồ thị

```python
@dataclass
class AgentGraph:
    topology: TopologyType
    nodes : List[str]                     # ["agent_0", "agent_1", ...]
    edges : List[Edge]                    # các trust boundary
    roles : Dict[str, AgentRole]          # agent_id → role
    parents: Dict[str, List[str]]         # agent_id → [các parent ids]
```

### `successors(agent_id)`

```python
def successors(self, agent_id):   # agent nào nhận message từ agent_id
    return [e.dst for e in self.edges if e.src == agent_id]
```

- Chain `0→1→2→3`: `successors("agent_0") = ["agent_1"]`, `successors("agent_3") = []`.
- Đây là danh sách **downstream neighbors** — nơi compromised agent sẽ forward payload.

### `degree(agent_id)` / out_degree

```python
def degree(self, agent_id):
    return len(self.successors(agent_id))
```

= số agent downstream. Runner dùng nó set `out_degree` cho mỗi `Agent`
(ảnh hưởng tính R0).

### `add_edge()`

```python
def add_edge(self, src, dst, conn=FORWARD):
    self.edges.append(Edge(src, dst, conn))
    self.parents.setdefault(dst, []).append(src)
```

Mỗi lần gọi tạo thêm **một trust boundary** (thêm 1 "con đường" cho injection lan).

---

## 7. `build_graph()` — factory

```python
def build_graph(topology: TopologyType, n: int, seed: int = 0) -> AgentGraph:
    if topology == CHAIN: return _chain(n)
    if topology == STAR:  return _star(n)
    if topology == TREE:  return _tree(n)
    raise ValueError(...)   # mesh/debate chưa hỗ trợ
```

- `n` = số agents (3–50 trong scope; thực tế nghiên cứu 1 tháng: 3–10).
- `seed` dự trữ cho việc random topology (hiện tại các topology là deterministic).

---

## 8. `_role_cycle()` — phân bổ vai trò tuần hoàn

```python
roles = [PLANNER, WORKER, REVIEWER, AGGREGATOR]
# agent_0=Planner, agent_1=Worker, agent_2=Reviewer, agent_3=Aggregator, agent_4=Planner ...
```

Dùng để gán role tuần hoàn cho các agent khi dựng chain/tree, đảm bảo mạng có
nhiều loại vai trò (không phải toàn Worker), giúp quan sát ảnh hưởng của role.

---

## 9. `_chain(n)` — topology Chain

```python
def _chain(n):
    # agent_0 → agent_1 → agent_2 → ... → agent_{n-1}
    for i in range(n):
        out_degree = 1 if i < n-1 else 0   # agent cuối không có successor
        g.add_node(f"agent_{i}", next(r), out_degree)
    for i in range(n-1):
        g.add_edge(f"agent_{i}", f"agent_{i+1}")
```

- Mỗi agent (trừ cuối) có `out_degree = 1`.
- Là topology **đơn giản nhất**, dùng làm baseline.
- Xác suất đi từ đầu đến cuối chuỗi (lý thuyết, giả định Markov):

```
P_E2E = ∏_{i=0}^{n-2} s_i      (metric.md §2: ASR trên chain)
```

Empirical ASR được đo trên các natural run (entry compromised by construction).
Ví dụ mock (s ≈ 1.0): `ASR ≈ 1.0` → injection đi hết chuỗi.

---

## 10. `_star(n)` — topology Star

```python
def _star(n):
    g.add_node("agent_0", AGGREGATOR, out_degree=n-1)   # center
    for i in range(1, n):
        g.add_node(f"agent_{i}", WORKER, out_degree=0)   # leaves
    for i in range(1, n):
        g.add_edge(f"agent_{i}", "agent_0", FAN_IN)      # leaves → center
```

- Cấu trúc:
```
    [Worker_1]
    /
[Worker_2] → [Aggregator]      (center "agent_0")
    \
    [Worker_3]
```
- Center (Aggregator) nhận fan-in từ **tất cả** leaves → nếu nhiều leaf bị infect,
  center có xác suất bị infect rất cao.
- Lưu ý: hiện tại center `out_degree = n-1` được set trong `add_node` nhưng thực
  tế center **không có successor** (chỉ nhận, không gửi) → propagation chỉ dừng ở
  center. (Đây là một điểm có thể tinh chỉnh nếu muốn star lan rộng hơn.)

---

## 11. `_tree(n)` — topology Tree (balanced binary)

```python
def _tree(n):
    for i in range(n):
        g.add_node(f"agent_{i}", next(r), out_degree=0)
    for i in range(1, n):
        parent = (i-1) // 2     # công thức cây nhị phân
        g.add_edge(f"agent_{parent}", f"agent_{i}")
```

- Mỗi node cha `p` có 2 con: `2p+1` và `2p+2`.
- **Branching factor = 2** → mỗi compromised agent infect thêm tối đa 2 agent:

```
R0 lý thuyết ≈ 2 × s
```

→ Nếu `s > 0.5` thì `R0 > 1` → **supercritical spread** (lây lan bùng nổ).
Đây chính là topology cho phép so sánh hành vi *trên/ dưới epidemic threshold*.

---

## 12. Mối liên hệ với R0 / epidemic threshold

| Topology | out_degree (điển hình) | R0 lý thuyết | Ngưỡng epidemic |
|---|---|---|---|
| Chain | 1 | `1 × s` | `s = 1` là biên (không bùng nổ) |
| Tree | 2 | `2 × s` | `s = 0.5` → nếu `s > 0.5` thì `R0 > 1` |
| Star | 1 (mặc định tại leaves) | phụ thuộc entry point | — |

> Lưu ý: `R0` lý thuyết = `d × s` với `d` là *average out-degree* trên toàn mạng
> (metric.md §3.3 / §5). Trên mạng **hữu hạn**, node biên (out-degree 0) làm
> `d = #edges / #nodes < branching` — vd chain n agents có `d = (n-1)/n`. Benchmark
> báo `R̂0` kèm consistency check `d · s̄` (xem `benchmark/runner.py` →
> `r0_ds_check`), đúng khuyến nghị metric.md §5.

Điều này cho phép benchmark trả lời **RQ2**: topology ảnh hưởng thế nào đến khả
năng lan truyền, và **vị trí nào khuếch đại** (super-spreader).

---

## 13. Cách dùng trong Runner

Trong `runner/engine.py`:

- **Natural runs** (`Runner.run_trial()`): entry compromised by construction rồi
  `Runner._forward()` gửi response của compromised agent tới `graph.successors(aid)`.
- **Controlled per-edge protocol** (`Runner.run_per_edge_protocol()`): với mỗi
  `edge` của graph, ép C_src=1 và judge dst qua `per_edge_trials` lần (metric.md §1).

```python
graph = build_graph(config.topology, config.num_agents, seed=...)
agents = self._build_agents(graph)          # mỗi node → 1 Agent
...
for dst in graph.successors(aid):           # compromised → gửi tới successors
    incoming[dst].append(Message(...))
```

→ Graph đóng vai trò: **xác định ai gửi cho ai** (edge = hop), và **out_degree**
của từng agent quyết định phạm vi lan truyền khi compromised (đóng góp vào `R0`).

---

## 14. Tóm tắt

- **Edge** = 1 trust boundary = 1 hop = 1 cơ hội lan truyền.
- **Chọn topology** = chọn cấu trúc out_degree/branching → khác biệt R0.
- **Chain**: baseline. **Tree**: branching 2 → dễ vượt epidemic threshold. **Star**:
  nhiều nguồn đổ về center.
