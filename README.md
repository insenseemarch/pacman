# Project 1: Pacman vs. Ghost AI Arena

Dự án yêu cầu cài đặt hai agent riêng biệt:
* **`Seek Agent` (Pacman):** Có nhiệm vụ tìm và bắt `Ghost Agent` càng nhanh càng tốt.
* **`Hide Agent` (Ghost):** Có nhiệm vụ trốn tránh `Pacman` cho đến khi hết số bước đi tối đa (mặc định là 200).

Một cơ chế quan trọng của đấu trường là **di chuyển đồng bộ (Synchronous Execution)**, nghĩa là cả Pacman và Ghost đều ra quyết định và di chuyển cùng một lúc.

## Cài đặt Agent (Agent Implementation)

File cài đặt (`submissions/23120172/agent.py`) sử dụng các thuật toán sau:

### 1. PacmanAgent (Seeker): Chiến thuật A* Dự đoán (Predictive A\* Search)

Một agent A* đơn giản sẽ luôn đi sau Ghost một bước do cơ chế di chuyển đồng bộ. Để khắc phục điều này, Pacman của tôi sử dụng logic dự đoán để "chặn đầu" Ghost.

1.  **Mô phỏng Ghost:** Agent Pacman mô phỏng lại logic của `example_student` Ghost (là logic "di chuyển ra xa" đơn giản).
2.  **Dự đoán Mục tiêu:** Pacman dự đoán ô tiếp theo mà Ghost *sẽ* di chuyển đến.
3.  **Tìm đường A\*:** Thay vì tìm đường đến vị trí *hiện tại* của Ghost, Pacman chạy thuật toán A* để tìm đường ngắn nhất đến vị trí *tương lai* đã được dự đoán.

### 2. GhostAgent (Hider): Chiến thuật "Tìm điểm xa nhất" (BFS + A\* Strategy)

Để trốn thoát hiệu quả, Ghost cần tìm một vị trí an toàn và xa nhất có thể.

1.  **Tìm vị trí xa nhất (BFS):** Agent chạy thuật toán Breadth-First Search (BFS) xuất phát từ vị trí của Pacman. Quá trình này lập bản đồ khoảng cách từ Pacman đến mọi ô có thể đi được trên bản đồ.
2.  **Chọn Mục tiêu:** Ghost xác định một (hoặc nhiều) ô có khoảng cách (số bước đi) xa nhất so với Pacman.
3.  **Di chuyển (A\*):** Sau khi có mục tiêu, Ghost sử dụng thuật toán A* để tìm đường đi ngắn nhất từ vị trí *hiện tại của chính nó* đến ô mục tiêu an toàn đó.
4.  Agent sẽ tính toán lại đường đi định kỳ (mỗi 10 bước) để thích ứng với các di chuyển mới của Pacman.

## Cài đặt và Môi trường

Dự án yêu cầu Python 3.7+ và môi trường Conda.

Cài đặt các thư viện cần thiết (`numpy`):
    ```bash
    pip install numpy
    ```

## Cách chạy

Tất cả các lệnh phải được chạy từ bên trong thư mục `src/`.

```bash
cd src
```

### Chạy Agent (23120172) vs. Agent Mẫu

```bash
# Thử Pacman (Seeker) vs. Ghost mẫu (Hider)
python arena.py --seek 23120172 --hide example_student

# Thử Ghost (Hider) vs. Pacman mẫu (Seeker)
python arena.py --seek example_student --hide 23120172
```

### Chạy 2 Agent đấu với nhau

```bash
# Pacman dự đoán (Seeker) vs. Ghost tìm điểm xa nhất (Hider)
python arena.py --seek 23120172 --hide 23120172
```

### Các tùy chọn hữu ích

* `--delay 0.5`: Làm chậm trò chơi (0.5 giây mỗi bước) để dễ dàng quan sát.
* `--no-viz`: Tắt giao diện đồ họa để chạy kiểm thử nhanh.
* `--max-steps 300`: Thay đổi độ dài tối đa của ván đấu (mặc định là 200).

## Cấu trúc Thư mục

```
pacman/
├── src/                  # Mã nguồn của framework đấu trường (không chỉnh sửa)
│   ├── arena.py          # Trình điều khiển chính của trò chơi
│   ├── environment.py    # Định nghĩa môi trường, bản đồ, luật chơi
│   ├── agent_interface.py# Lớp (class) cơ sở cho agent
│   └── ...
├── submissions/          # Nơi chứa code của sinh viên
│   ├── 23120172/         # Thư mục nộp bài của tôi
│   │   └── agent.py      # <-- File cài đặt agent của tôi
│   └── example_student/  # Agent mẫu với logic cơ bản
├── .gitignore            # Bỏ qua các file tạm
├── AI 23_4 - Project 1.pdf # File PDF mô tả đồ án
└── requirements.txt      # Các thư viện Python cần thiết
```
