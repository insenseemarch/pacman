"""
Bài làm cho Đồ án 1: Hide and Seek Arena (Bản nâng cao v2.0)

File này chứa cài đặt cho cả PacmanAgent (Seek) và GhostAgent (Hide).

Thay đổi (v2.0):
- Nâng cấp 'PacmanAgent' với chiến thuật "Dự đoán Chuyển động"
  (Predictive Movement).
- Pacman sẽ mô phỏng logic của 'example_student' Ghost để dự đoán
  nước đi tiếp theo của Ghost.
- Pacman sẽ dùng A* để tìm đường đến vị trí *dự đoán* của Ghost,
  thay vì vị trí hiện tại của nó.
- GhostAgent (Hider) giữ nguyên chiến thuật 'tìm vị trí xa nhất' (vốn đã nâng cao).
"""

import sys
from pathlib import Path
from collections import deque
from heapq import heappush, heappop
import numpy as np
import itertools # Dùng cho bộ đếm của A*

# Thêm thư mục 'src' vào sys.path để import các lớp cơ sở
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from agent_interface import PacmanAgent as BasePacmanAgent
    from agent_interface import GhostAgent as BaseGhostAgent
    from environment import Move
except ImportError:
    print("Lỗi: Không thể import các lớp từ thư mục 'src'.")
    print(f"Đã thử thêm đường dẫn: {src_path}")
    sys.exit(1)


class AgentHelpers:
    """
    Lớp chứa các hàm tiện ích chung mà cả hai agent đều có thể sử dụng.
    """

    def _is_valid_position(self, pos: tuple, map_state: np.ndarray) -> bool:
        """Kiểm tra xem một vị trí có hợp lệ không (trong bản đồ và không phải là tường)."""
        row, col = pos
        height, width = map_state.shape
        if row < 0 or row >= height or col < 0 or col >= width:
            return False
        return map_state[row, col] == 0

    def _apply_move(self, pos: tuple, move: Move) -> tuple:
        """Áp dụng một nước đi vào vị trí hiện tại và trả về vị trí mới."""
        delta_row, delta_col = move.value
        return (pos[0] + delta_row, pos[1] + delta_col)

    def _get_neighbors(self, pos: tuple, map_state: np.ndarray) -> list:
        """Lấy tất cả các vị trí hàng xóm hợp lệ và nước đi tương ứng."""
        neighbors = []
        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            next_pos = self._apply_move(pos, move)
            if self._is_valid_position(next_pos, map_state):
                neighbors.append((next_pos, move))
        return neighbors

    def _manhattan_distance(self, pos1: tuple, pos2: tuple) -> int:
        """Tính khoảng cách Manhattan giữa hai vị trí."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def bfs(self, start: tuple, goal: tuple, map_state: np.ndarray) -> list:
        """Tìm đường đi ngắn nhất bằng BFS."""
        queue = deque([(start, [])])
        visited = {start}
        
        while queue:
            current_pos, path = queue.popleft()
            if current_pos == goal:
                return path
            
            for next_pos, move in self._get_neighbors(current_pos, map_state):
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [move]))
        return []

    def astar(self, start: tuple, goal: tuple, map_state: np.ndarray) -> list:
        """Tìm đường đi tối ưu bằng A* (đã sửa lỗi tie-breaking)."""
        
        def heuristic(pos):
            return self._manhattan_distance(pos, goal)
        
        counter = itertools.count() 
        frontier = [(heuristic(start), 0, next(counter), start, [])] 
        visited = set()
        
        while frontier:
            f_cost, g_cost, _, current_pos, path = heappop(frontier) 
            
            if current_pos == goal:
                return path
            if current_pos in visited:
                continue
            visited.add(current_pos)
            
            for next_pos, move in self._get_neighbors(current_pos, map_state):
                if next_pos not in visited:
                    new_g_cost = g_cost + 1
                    new_h_cost = heuristic(next_pos)
                    new_f_cost = new_g_cost + new_h_cost
                    heappush(frontier, (new_f_cost, new_g_cost, next(counter), next_pos, path + [move]))
        return []


class PacmanAgent(BasePacmanAgent, AgentHelpers):
    """
    Pacman (Seeker) Agent - NÂNG CAO
    Sử dụng A* với logic "Dự đoán Nước đi" (Predictive Targeting).
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.path = []

    # ===== HÀM MỚI =====
    def _predict_enemy_move(self, my_position: tuple, enemy_position: tuple, map_state: np.ndarray) -> Move:
        """
        Dự đoán nước đi của 'example_student' Ghost.
        Hàm này mô phỏng lại y hệt logic trong file 'example_student/agent.py'.
        """
        # Tính toán hướng đi *ra xa* Pacman (từ góc nhìn của Ghost)
        row_diff = enemy_position[0] - my_position[0]
        col_diff = enemy_position[1] - my_position[1]
        
        moves = []
        
        # Ưu tiên di chuyển dọc ra xa
        if row_diff > 0:
            moves.append(Move.DOWN)
        elif row_diff < 0:
            moves.append(Move.UP)
        
        # Ưu tiên di chuyển ngang ra xa
        if col_diff > 0:
            moves.append(Move.RIGHT)
        elif col_diff < 0:
            moves.append(Move.LEFT)
        
        # Thử các nước đi ưu tiên trước
        for move in moves:
            next_pos = self._apply_move(enemy_position, move)
            if self._is_valid_position(next_pos, map_state):
                return move # Đây là nước đi được dự đoán

        # Nếu các nước ưu tiên không hợp lệ, 'example_student' sẽ thử các nước còn lại
        all_moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
        
        for move in all_moves:
            # Bỏ qua nếu nó đã có trong 'moves' (vì đã thử và thất bại)
            if move in moves: 
                continue 
            
            next_pos = self._apply_move(enemy_position, move)
            if self._is_valid_position(next_pos, map_state):
                return move # Dự đoán nước đi dự phòng
        
        # Nếu bị kẹt hoàn toàn, dự đoán nó sẽ ở yên
        return Move.STAY

    # ===== HÀM MỚI =====
    def _get_predicted_enemy_position(self, my_position: tuple, enemy_position: tuple, map_state: np.ndarray) -> tuple:
        """
        Trả về vị trí *tiếp theo* (dự đoán) của 'example_student' Ghost.
        """
        predicted_move = self._predict_enemy_move(my_position, enemy_position, map_state)
        return self._apply_move(enemy_position, predicted_move)

    # ===== HÀM STEP ĐÃ NÂNG CẤP =====
    def step(self, map_state: np.ndarray, 
             my_position: tuple, 
             enemy_position: tuple,
             step_number: int) -> Move:
        """
        Quyết định nước đi tiếp theo.
        """
        
        # THAY ĐỔI CHÍNH:
        # Thay vì tìm đường đến 'enemy_position' (vị trí HIỆN TẠI)
        # Hãy tìm đường đến vị trí 'DỰ ĐOÁN' của kẻ thù
        predicted_target = self._get_predicted_enemy_position(my_position, enemy_position, map_state)
        
        # Tính đường đi A* đến vị trí dự đoán
        self.path = self.astar(my_position, predicted_target, map_state)
        
        # Nếu có đường đi, thực hiện nước đi đầu tiên
        if self.path:
            return self.path[0]
        
        # --- Dự phòng (Fallback) ---
        # Nếu không có đường đến vị trí DỰ ĐOÁN (ví dụ: nó đi vào tường?)
        # thì hãy thử tìm đường đến vị trí HIỆN TẠI của nó.
        self.path = self.astar(my_position, enemy_position, map_state)
        if self.path:
            return self.path[0]

        # Nếu vẫn không được, (ví dụ: bị kẹt)
        # thử một nước đi hợp lệ bất kỳ
        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
             if self._is_valid_position(self._apply_move(my_position, move), map_state):
                 return move

        return Move.STAY


class GhostAgent(BaseGhostAgent, AgentHelpers):
    """
    Ghost (Hider) Agent - Mục tiêu: Tránh bị bắt
    Sử dụng chiến thuật tìm vị trí xa nhất so với Pacman và di chuyển đến đó.
    (Đây vốn đã là một chiến thuật nâng cao và hiệu quả)
    """
    
    def __init__(self, **kwargs):
        """Khởi tạo agent."""
        super().__init__(**kwargs)
        self.target_position = None
        self.path = []

    def find_furthest_position(self, my_position: tuple, enemy_position: tuple, map_state: np.ndarray) -> tuple:
        """
        Tìm vị trí xa nhất có thể đến được so với kẻ thù (Pacman).
        Sử dụng BFS từ vị trí của kẻ thù.
        """
        queue = deque([(enemy_position, 0)])  # (vị trí, khoảng cách)
        visited = {enemy_position: 0}
        
        max_dist = -1
        furthest_positions = []
        
        # 1. Chạy BFS từ vị trí của Pacman
        while queue:
            current_pos, dist = queue.popleft()
            
            if dist > max_dist:
                max_dist = dist
                furthest_positions = [current_pos]
            elif dist == max_dist:
                furthest_positions.append(current_pos)
            
            for next_pos, _ in self._get_neighbors(current_pos, map_state):
                if next_pos not in visited:
                    visited[next_pos] = dist + 1
                    queue.append((next_pos, dist + 1))
        
        # 2. Tìm vị trí xa nhất mà "gần mình nhất"
        if not furthest_positions:
            return my_position 
        
        best_target = min(furthest_positions, 
                          key=lambda pos: self._manhattan_distance(my_position, pos))
        
        return best_target

    def step(self, map_state: np.ndarray, 
             my_position: tuple, 
             enemy_position: tuple,
             step_number: int) -> Move:
        """
        Quyết định nước đi tiếp theo.
        """
        
        # 1. Tìm mục tiêu mới mỗi 10 bước hoặc khi hết đường đi
        if step_number % 10 == 1 or not self.path:
            self.target_position = self.find_furthest_position(my_position, enemy_position, map_state)
            self.path = self.astar(my_position, self.target_position, map_state)

        # 2. Nếu có đường đi, đi theo đường đi đó
        if self.path:
            next_move = self.path.pop(0) 
            return next_move

        # 3. Nếu không (dự phòng), thực hiện một nước đi "an toàn" (xa Pacman nhất)
        best_move = Move.STAY
        max_dist_from_enemy = self._manhattan_distance(my_position, enemy_position)
        
        possible_moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT, Move.STAY]
        
        for move in possible_moves:
            next_pos = self._apply_move(my_position, move)
            if self._is_valid_position(next_pos, map_state):
                dist = self._manhattan_distance(next_pos, enemy_position)
                if dist > max_dist_from_enemy:
                    max_dist_from_enemy = dist
                    best_move = move
        
        return best_move