"""一箭又一箭：基于 Tkinter 的箭头解谜小游戏。"""

import tkinter as tk
from dataclasses import dataclass
from typing import Dict, List, Tuple


WINDOW_WIDTH = 760
WINDOW_HEIGHT = 720
GRID_SIZE = 6
CELL_SIZE = 72
BOARD_LEFT = 120
BOARD_TOP = 130
MAX_MISSES = 3

BG = "#f4f7fb"
PANEL = "#ffffff"
INK = "#1f2937"
MUTED = "#64748b"
ACCENT = "#2563eb"
ARROW_COLORS = {"up": "#ef4444", "down": "#f97316", "left": "#8b5cf6", "right": "#0f766e"}
ARROW_SYMBOLS = {"up": "↑", "down": "↓", "left": "←", "right": "→"}


@dataclass
class Arrow:
    row: int
    col: int
    direction: str


class ArrowGame:
    """管理界面、关卡数据以及玩家输入。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("一箭又一箭")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

        self.screen = "start"
        self.level_index = 0
        self.arrows: Dict[Tuple[int, int], Arrow] = {}
        self.misses = MAX_MISSES
        self.message = "点击开始，观察箭头方向并依次清空棋盘。"
        self.levels = [[
            Arrow(0, 0, "right"), Arrow(0, 3, "down"), Arrow(2, 3, "left"),
            Arrow(4, 1, "up"), Arrow(5, 4, "left"), Arrow(3, 5, "up"),
        ]]
        self.draw_start()

    def draw_start(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(WINDOW_WIDTH // 2, 170, text="一箭又一箭", font=("Microsoft YaHei", 34, "bold"), fill=INK)
        self.canvas.create_text(WINDOW_WIDTH // 2, 225, text="点击没有阻挡的箭头，让它飞出棋盘", font=("Microsoft YaHei", 15), fill=MUTED)
        self.canvas.create_rectangle(265, 330, 495, 395, fill=ACCENT, outline="")
        self.canvas.create_text(WINDOW_WIDTH // 2, 362, text="开始游戏", font=("Microsoft YaHei", 18, "bold"), fill="white")
        self.canvas.create_text(WINDOW_WIDTH // 2, 520, text="方向：上 / 下 / 左 / 右    失误机会：3 次", font=("Microsoft YaHei", 12), fill=MUTED)

    def draw_game(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(38, 34, anchor="w", text=f"第 {self.level_index + 1} 关", font=("Microsoft YaHei", 22, "bold"), fill=INK)
        self.canvas.create_text(38, 75, anchor="w", text=self.message, font=("Microsoft YaHei", 11), fill=MUTED)
        self.canvas.create_text(540, 35, text=f"剩余箭头：{len(self.arrows)}", font=("Microsoft YaHei", 12, "bold"), fill=INK)
        self.canvas.create_text(540, 65, text=f"剩余失误：{self.misses}", font=("Microsoft YaHei", 12, "bold"), fill="#dc2626")
        self.canvas.create_rectangle(BOARD_LEFT - 8, BOARD_TOP - 8, BOARD_LEFT + GRID_SIZE * CELL_SIZE + 8, BOARD_TOP + GRID_SIZE * CELL_SIZE + 8, fill=PANEL, outline="#dbe3ef", width=2)
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x1 = BOARD_LEFT + col * CELL_SIZE
                y1 = BOARD_TOP + row * CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE, fill="#f8fafc", outline="#e2e8f0")
        for arrow in self.arrows.values():
            self.draw_arrow(arrow)
        self.canvas.create_rectangle(BOARD_LEFT, 595, BOARD_LEFT + 170, 640, fill="#e2e8f0", outline="")
        self.canvas.create_text(BOARD_LEFT + 85, 617, text="重新开始本关", font=("Microsoft YaHei", 12, "bold"), fill=INK)

    def draw_arrow(self, arrow: Arrow, color: str = "") -> None:
        x = BOARD_LEFT + arrow.col * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_TOP + arrow.row * CELL_SIZE + CELL_SIZE // 2
        self.canvas.create_text(x, y, text=ARROW_SYMBOLS[arrow.direction], font=("Arial", 38, "bold"), fill=color or ARROW_COLORS[arrow.direction], tags="arrow")

    def on_click(self, event: tk.Event) -> None:
        if self.screen == "start":
            if 265 <= event.x <= 495 and 330 <= event.y <= 395:
                self.start_level(0)
            return
        if self.screen == "result":
            if 260 <= event.x <= 500 and 420 <= event.y <= 480:
                self.start_level(self.level_index if self.misses <= 0 else (self.level_index + 1) % len(self.levels))
            return
        if BOARD_LEFT <= event.x < BOARD_LEFT + GRID_SIZE * CELL_SIZE and BOARD_TOP <= event.y < BOARD_TOP + GRID_SIZE * CELL_SIZE:
            col = (event.x - BOARD_LEFT) // CELL_SIZE
            row = (event.y - BOARD_TOP) // CELL_SIZE
            self.handle_arrow_click(int(row), int(col))
        elif BOARD_LEFT <= event.x <= BOARD_LEFT + 170 and 595 <= event.y <= 640:
            self.start_level(self.level_index)

    def handle_arrow_click(self, row: int, col: int) -> None:
        """阶段一只显示点击反馈，路径规则在后续提交中实现。"""
        arrow = self.arrows.get((row, col))
        if arrow:
            self.message = f"已选择 {ARROW_SYMBOLS[arrow.direction]} 箭头"
            self.draw_game()

    def start_level(self, index: int) -> None:
        self.level_index = index
        self.misses = MAX_MISSES
        self.message = "选择前方没有箭头的目标。"
        self.arrows = {(a.row, a.col): Arrow(a.row, a.col, a.direction) for a in self.levels[index]}
        self.screen = "game"
        self.draw_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = ArrowGame(root)
    root.mainloop()
