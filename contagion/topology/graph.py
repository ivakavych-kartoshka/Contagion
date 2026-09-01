"""Agent graph constructs: nodes (agents), edges (trust boundaries), and the
topology builders for chain / star / tree.

================================================================================
TOPOLOGY GRAPH LÀ GÌ TRONG MÔ HÌNH CONTAGION?
================================================================================

Topology graph là directed graph (đồ thị có hướng) biểu diễn cấu trúc giao tiếp
giữa các agent trong multi-agent network:

    - NODE  = một Agent (với role cụ thể: Planner, Worker, Reviewer...)
    - EDGE  = một trust boundary: message đi từ agent.src → agent.dst
              Mỗi edge tương ứng với MỘT communication hop
              Và mỗi hop là một cơ hội cho injection lan truyền

    +---agent_0---+---agent_1---+---agent_2---+     (CHAIN topology)
        Planner       Worker        Reviewer

    Variants:
    - Chain:  linear, mỗi agent có 1 successor. Phù hợp cho baseline.
              P_E2E = ∏ s_i (đúng lý thuyết branching process trivial).
    - Star:   1 center + N leaves, fan-in edges.
              Center nhận nhiều infection sources → super-spreader risk.
    - Tree:   balanced binary tree.
              Branching factor 2 → reproduction number R0 = 2 × s (nếu s > 0.5 thì R0 > 1).

    Mesh và Debate nằm trong scope mở rộng (tháng 2+).

Mỗi topology quyết định:
    1. out_degree của mỗi agent → ảnh hưởng trực tiếp đến R0
       (R0 = E[new compromises per compromised agent] ≈ out_degree × s)
    2. Số trust boundary (edges) → tổng số hop propagation có thể xảy ra
    3. Cấu trúc fan-out/fan-in → xác định super-spreader roles

================================================================================
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List

from ..core import AgentRole, TopologyType


class Connection(str, enum.Enum):
    """Loại kết nối giữa hai agent.

    FORWARD   : A → B (1-1, mặc định: chain, tree)
    BROADCAST : A → {B, C, D} (1-N, fanout cao: broadcaster role)
    FAN_IN    : {A, B} → C (N-1, star center aggregates từ nhiều nguồn)
    """
    FORWARD = "forward"
    BROADCAST = "broadcast"
    FAN_IN = "fan_in"


@dataclass
class Edge:
    """Một cạnh có hướng trong agent graph.

    Mỗi edge = MỘT trust boundary = MỘT hop.
    Khi agent_src bị compromise, message đi qua edge này có thể infect agent_dst.
    "Có thể infect" = per-hop survival rate s = P(dst compromised | src compromised).
    """
    src: str       # sender agent id
    dst: str       # receiver agent id
    conn: Connection = Connection.FORWARD


@dataclass
class AgentGraph:
    """Directed graph biểu diễn cấu trúc multi-agent network.

    Thuộc tính:
        topology : Chain/Star/Tree (decision graph forme)
        nodes    : danh sách agent id ["agent_0", "agent_1", ...]
        edges    : danh sách Edge (trust boundaries)
        roles    : ánh xạ agent_id → AgentRole (Planner/Worker/...)
        parents  : ánh xạ agent_id → danh sách parent ids (ai gửi cho nó)

    Methods quan trọng:
        successors(agent_id) : danh sách agent nhận message từ agent này
        degree(agent_id)     : số agent downstream (out-degree)
        topological_order()  : thứ tự chạy agents (hiện tại = insertion order)
    """
    topology: TopologyType
    nodes: List[str] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    roles: Dict[str, AgentRole] = field(default_factory=dict)
    parents: Dict[str, List[str]] = field(default_factory=dict)

    def add_node(self, agent_id: str, role: AgentRole, out_degree: int) -> None:
        """Thêm agent node vào graph."""
        self.nodes.append(agent_id)
        self.roles[agent_id] = role
        # out_degree được set cho到最后 một node (lưu ý: AttributeError nếu add nhiều node)
        # Fix: nên lưu dict/out_degree per node thay vì single attribute
        setattr(self, "_out_degree", out_degree)

    def add_edge(self, src: str, dst: str, conn: Connection = Connection.FORWARD) -> None:
        """Thêm trust boundary giữa hai agent.

        Edge src → dst có nghĩa:
            agent_src gửi message (response) → agent_dst
            Nếu agent_src bị compromise, message này có thể chứa injection
            → agent_dst có thể bị compromise tiếp theo
        """
        self.edges.append(Edge(src, dst, conn))
        self.parents.setdefault(dst, []).append(src)

    def successors(self, agent_id: str) -> List[str]:
        """Danh sách agent nhận message từ agent_id (downstream neighbors).

        Ví dụ chain 0→1→2→3:
            successors("agent_0") = ["agent_1"]
            successors("agent_3") = []  # cuối chain
        Ví dụ star 0←1,0←2,0←3:
            successors("agent_0") = []  # center là leaf
            successors("agent_1") = ["agent_0"]  # leaf gửi cho center
        """
        return [e.dst for e in self.edges if e.src == agent_id]

    def degree(self, agent_id: str) -> int:
        """Out-degree = số agent downstream (legacy, hiện trả về len(successors))."""
        return len(self.successors(agent_id))

    def topological_order(self) -> List[str]:
        """Thứ tự chạy agents.

        Hiện tại = thứ tự nodes (insertion order).
        ⚠️ Lưu ý: đây là simplified version. Tree/Star có thể cần BFS từ entry
        để đảm bảo parents chạy trước children. Bản hiện tại sử dụng
        pending/processed tracking trong Runner để xử lý đúng.
        """
        return self.nodes


# =============================================================================
# ROLE CYCLE: phân bổ role tuần hoàn cho agents
# =============================================================================
def _role_cycle():
    """Generator role tuần hoàn: Planner → Worker → Reviewer → Aggregator → Planner...

    Dùng khi tạo agents: agent_0 = Planner, agent_1 = Worker, agent_2 = Reviewer,
    agent_3 = Aggregator, agent_4 = Planner, ...
    """
    roles = [
        AgentRole.PLANNER,
        AgentRole.WORKER,
        AgentRole.REVIEWER,
        AgentRole.AGGREGATOR,
    ]
    while True:
        for r in roles:
            yield r


# =============================================================================
# GRAPH BUILDERS: hàm tạo topology graph
# =============================================================================

def build_graph(topology: TopologyType, n: int, seed: int = 0) -> AgentGraph:
    """Factory: tạo AgentGraph theo topology type và số agents.

    Args:
        topology : CHAIN, STAR, TREE (mesh/debate chưa hỗ trợ)
        n        : số agents (3-50 trong scope nghiên cứu 1 tháng, 3-10 thực tế)
        seed     : seed cho RNG (hiện tại chưa dùng, để sẵn cho future randomization)

    Returns:
        AgentGraph đã populated nodes + edges

    Raises:
        ValueError nếu topology chưa được implement
    """
    if topology == TopologyType.CHAIN:
        return _chain(n)
    if topology == TopologyType.STAR:
        return _star(n)
    if topology == TopologyType.TREE:
        return _tree(n)
    raise ValueError(f"Topology not yet supported in one-month scope: {topology}")


def _chain(n: int) -> AgentGraph:
    """Tạo chain topology: agent_0 → agent_1 → agent_2 → ... → agent_{n-1}.

    Cấu trúc:
        [Planner] → [Worker] → [Reviewer] → [Aggregator] → [Planner] → ...

    Mỗi agent (trừ last) có out_degree = 1.
    Last agent (agent_{n-1}) có out_degree = 0 (no successor).

    P_E2E (end-to-end propagation) trên chain = ∏_{i=0}^{n-2} s_i
    Với s_i ≈ 1 (mock), P_E2E = 1.0.
    """
    g = AgentGraph(topology=TopologyType.CHAIN)
    r = _role_cycle()
    for i in range(n):
        # out_degree = 1 cho tất cả trừ agent cuối (i == n-1 → out_degree = 0)
        g.add_node(f"agent_{i}", next(r), out_degree=1 if i < n - 1 else 0)
    # Chain edges: agent_i → agent_{i+1}
    for i in range(n - 1):
        g.add_edge(f"agent_{i}", f"agent_{i + 1}")
    return g


def _star(n: int) -> AgentGraph:
    """Tạo star topology: center (aggregator) nhận fan-in từ N-1 leaves.

    Cấu trúc:
                    [Worker_1]
                   /
        [Worker_2] → [Aggregator]  (center)
                   \
                    [Worker_3]

    Trong infected star:
        - Leaves (Worker) nhận infection riêng biệt
        - Center (Aggregator) nhận tất cả → super-spreader candidate
        - Nếu center bị compromise, không có downstream (out_degree = 0)
    """
    g = AgentGraph(topology=TopologyType.STAR)
    # Center = aggregator (nhận fan-in từ tất cả leaves)
    g.add_node("agent_0", AgentRole.AGGREGATOR, out_degree=n - 1)
    for i in range(1, n):
        g.add_node(f"agent_{i}", AgentRole.WORKER, out_degree=0)
    # Fan-in edges: leaves → center
    for i in range(1, n):
        g.add_edge(f"agent_{i}", "agent_0", Connection.FAN_IN)
    return g


def _tree(n: int) -> AgentGraph:
    """Tạo balanced binary tree topology.

    Cấu trúc (n=7):
              [Planner]              <- agent_0 (root)
              /          \
        [Worker]       [Reviewer]    <- agent_1, agent_2
        /   \\          /    \\
    [Aggr] [Plan]  [Work] [Rev]      <- agent_3..6

    Branching factor = 2.
    R0 lý thuyết ≈ 2 × s (nếu s > 0.5, R0 > 1 → supercritical).
    """
    g = AgentGraph(topology=TopologyType.TREE)
    r = _role_cycle()
    for i in range(n):
        g.add_node(f"agent_{i}", next(r), out_degree=0)
    # Balanced binary tree: parent of i = (i - 1) // 2
    # Ví dụ: parent(1)=0, parent(2)=0, parent(3)=1, parent(4)=1, parent(5)=2, parent(6)=2
    for i in range(1, n):
        parent = (i - 1) // 2
        g.add_edge(f"agent_{parent}", f"agent_{i}")
    return g