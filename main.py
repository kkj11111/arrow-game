"""一箭又一箭：基于 Tkinter 的箭头解谜小游戏。"""

import tkinter as tk
import time
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
        self.score = 0
        self.undo_stack = []
        self.started_at = 0.0
        self.elapsed = 0
        self.timer_job = None
        self.message = "点击开始，观察箭头方向并依次清空棋盘。"
        self.levels = [
            [Arrow(0, 0, "left"), Arrow(0, 3, "down"), Arrow(2, 3, "left"), Arrow(4, 1, "up"), Arrow(5, 4, "right"), Arrow(3, 5, "right")],
            [Arrow(0, 2, "up"), Arrow(1, 2, "down"), Arrow(2, 4, "right"), Arrow(2, 5, "left"), Arrow(4, 0, "left"), Arrow(5, 3, "down"), Arrow(5, 5, "right")],
            [Arrow(0, 0, "up"), Arrow(1, 1, "left"), Arrow(1, 4, "right"), Arrow(3, 1, "down"), Arrow(4, 1, "right"), Arrow(4, 4, "down"), Arrow(5, 0, "left"), Arrow(5, 4, "right")],
            [Arrow(0, 1, "up"), Arrow(0, 4, "right"), Arrow(2, 1, "down"), Arrow(2, 4, "left"), Arrow(4, 2, "up"), Arrow(5, 5, "down")],
            [Arrow(0, 0, "left"), Arrow(1, 0, "left"), Arrow(2, 2, "up"), Arrow(3, 2, "down"), Arrow(4, 5, "right"), Arrow(5, 3, "down"), Arrow(5, 5, "right")],
        ]
        self.draw_start()

    def draw_start(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(WINDOW_WIDTH // 2, 170, text="一箭又一箭", font=("Microsoft YaHei", 34, "bold"), fill=INK)
        self.canvas.create_text(WINDOW_WIDTH // 2, 225, text="点击没有阻挡的箭头，让它飞出棋盘", font=("Microsoft YaHei", 15), fill=MUTED)
        self.canvas.create_rectangle(250, 320, 510, 385, fill=ACCENT, outline="", tags="start")
        self.canvas.create_text(WINDOW_WIDTH // 2, 352, text="开始游戏", font=("Microsoft YaHei", 18, "bold"), fill="white")
        self.canvas.create_text(WINDOW_WIDTH // 2, 440, text="选择关卡", font=("Microsoft YaHei", 13, "bold"), fill=INK)
        for i in range(len(self.levels)):
            x = 270 + i * 58
            self.canvas.create_oval(x, 465, x + 38, 503, fill="#dbeafe" if i else ACCENT, outline="", tags=f"level_{i}")
            self.canvas.create_text(x + 19, 484, text=str(i + 1), font=("Arial", 12, "bold"), fill=INK if i else "white")
        self.canvas.create_text(WINDOW_WIDTH // 2, 555, text="方向：上 / 下 / 左 / 右    失误机会：3 次    支持撤销", font=("Microsoft YaHei", 12), fill=MUTED)

    def draw_game(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(38, 30, anchor="w", text=f"第 {self.level_index + 1} 关", font=("Microsoft YaHei", 22, "bold"), fill=INK)
        self.canvas.create_text(38, 68, anchor="w", text=self.message, font=("Microsoft YaHei", 11), fill=MUTED)
        self.canvas.create_text(420, 30, text=f"箭头 {len(self.arrows)}", font=("Microsoft YaHei", 12, "bold"), fill=INK)
        self.canvas.create_text(515, 30, text=f"失误 {self.misses}", font=("Microsoft YaHei", 12, "bold"), fill="#dc2626")
        self.canvas.create_text(625, 30, text=f"得分 {self.score}", font=("Microsoft YaHei", 12, "bold"), fill="#a16207")
        self.canvas.create_text(420, 68, text=f"用时 {self.elapsed}s", font=("Microsoft YaHei", 11), fill=MUTED)
        self.canvas.create_rectangle(BOARD_LEFT - 8, BOARD_TOP - 8, BOARD_LEFT + GRID_SIZE * CELL_SIZE + 8, BOARD_TOP + GRID_SIZE * CELL_SIZE + 8, fill=PANEL, outline="#dbe3ef", width=2)
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x1 = BOARD_LEFT + col * CELL_SIZE
                y1 = BOARD_TOP + row * CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE, fill="#f8fafc", outline="#e2e8f0")
        for arrow in self.arrows.values():
            self.draw_arrow(arrow)
        self.canvas.create_rectangle(BOARD_LEFT, 595, BOARD_LEFT + 170, 640, fill="#e2e8f0", outline="", tags="restart")
        self.canvas.create_text(BOARD_LEFT + 85, 617, text="重新开始本关", font=("Microsoft YaHei", 12, "bold"), fill=INK)
        self.canvas.create_rectangle(310, 595, 440, 640, fill="#dbeafe", outline="", tags="undo")
        self.canvas.create_text(375, 617, text="撤销上一步", font=("Microsoft YaHei", 12, "bold"), fill=ACCENT)

    def draw_arrow(self, arrow: Arrow, color: str = "") -> None:
        x = BOARD_LEFT + arrow.col * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_TOP + arrow.row * CELL_SIZE + CELL_SIZE // 2
        self.canvas.create_text(x, y, text=ARROW_SYMBOLS[arrow.direction], font=("Arial", 38, "bold"), fill=color or ARROW_COLORS[arrow.direction], tags="arrow")

    def on_click(self, event: tk.Event) -> None:
        if self.screen == "start":
            if 250 <= event.x <= 510 and 320 <= event.y <= 385:
                self.start_level(0)
            elif 270 <= event.x <= 540 and 460 <= event.y <= 510:
                index = min(len(self.levels) - 1, max(0, (event.x - 270) // 58))
                self.start_level(index)
            return
        if self.screen == "result":
            if 260 <= event.x <= 500 and 420 <= event.y <= 480:
                next_index = (self.level_index + 1) % len(self.levels) if self.result_success else self.level_index
                self.start_level(next_index)
            return
        if BOARD_LEFT <= event.x < BOARD_LEFT + GRID_SIZE * CELL_SIZE and BOARD_TOP <= event.y < BOARD_TOP + GRID_SIZE * CELL_SIZE:
            col = (event.x - BOARD_LEFT) // CELL_SIZE
            row = (event.y - BOARD_TOP) // CELL_SIZE
            self.handle_arrow_click(int(row), int(col))
        elif BOARD_LEFT <= event.x <= BOARD_LEFT + 170 and 595 <= event.y <= 640:
            self.start_level(self.level_index)
        elif 310 <= event.x <= 440 and 595 <= event.y <= 640:
            self.undo()

    def handle_arrow_click(self, row: int, col: int) -> None:
        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return
        arrow = self.arrows.get((row, col))
        if not arrow:
            return
        if self.is_clear_path(arrow):
            self.undo_stack.append((dict(self.arrows), self.misses, self.score))
            del self.arrows[(row, col)]
            self.score += 100 + self.misses * 10
            self.message = f"{ARROW_SYMBOLS[arrow.direction]} 箭头飞出棋盘！"
            if not self.arrows:
                self.show_result(True)
        else:
            self.misses -= 1
            self.message = "前方有箭头阻挡，点击顺序不正确。"
            if self.misses <= 0:
                self.show_result(False)
        if self.screen == "game":
            self.draw_game()
            if not self.is_clear_path(arrow):
                self.flash_collision(row, col)

    def is_clear_path(self, arrow: Arrow) -> bool:
        """只检查同一行或同一列、朝向边界一侧的格子。"""
        dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[arrow.direction]
        row, col = arrow.row + dr, arrow.col + dc
        while 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            if (row, col) in self.arrows:
                return False
            row += dr
            col += dc
        return True

    def show_result(self, success: bool) -> None:
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.screen = "result"
        self.result_success = success
        self.canvas.delete("all")
        all_cleared = success and self.level_index == len(self.levels) - 1
        title = "全部关卡完成！" if all_cleared else ("本关通关！" if success else "挑战失败")
        subtitle = "点击按钮重新体验" if all_cleared else ("准备进入下一关" if success else "失误次数已用完，请重新尝试")
        color = "#15803d" if success else "#dc2626"
        self.canvas.create_text(WINDOW_WIDTH // 2, 220, text=title, font=("Microsoft YaHei", 32, "bold"), fill=color)
        self.canvas.create_text(WINDOW_WIDTH // 2, 275, text=subtitle, font=("Microsoft YaHei", 15), fill=MUTED)
        if success:
            stars = "★" * (3 if self.misses == MAX_MISSES else 2 if self.misses > 0 else 1)
            self.canvas.create_text(WINDOW_WIDTH // 2, 330, text=f"{stars}   得分 {self.score}   用时 {self.elapsed}s", font=("Arial", 18, "bold"), fill="#eab308")
        self.canvas.create_rectangle(260, 420, 500, 480, fill=ACCENT, outline="")
        action = "重新开始" if all_cleared else ("进入下一关" if success else "重新开始")
        self.canvas.create_text(WINDOW_WIDTH // 2, 450, text=action, font=("Microsoft YaHei", 16, "bold"), fill="white")

    def flash_collision(self, row: int, col: int) -> None:
        """短暂高亮被阻挡的箭头，提供明确的碰撞反馈。"""
        x = BOARD_LEFT + col * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_TOP + row * CELL_SIZE + CELL_SIZE // 2
        self.canvas.create_text(x, y, text="✕", font=("Arial", 32, "bold"), fill="#dc2626", tags="collision")
        self.root.after(180, lambda: self.canvas.delete("collision"))

    def start_level(self, index: int) -> None:
        self.level_index = index
        self.misses = MAX_MISSES
        self.score = 0
        self.undo_stack = []
        self.started_at = time.monotonic()
        self.elapsed = 0
        self.message = "选择前方没有箭头的目标。"
        self.arrows = {(a.row, a.col): Arrow(a.row, a.col, a.direction) for a in self.levels[index]}
        self.screen = "game"
        self.draw_game()
        self.update_timer()

    def update_timer(self) -> None:
        if self.screen != "game":
            return
        self.elapsed = int(time.monotonic() - self.started_at)
        self.draw_game()
        self.timer_job = self.root.after(1000, self.update_timer)

    def undo(self) -> None:
        if self.undo_stack:
            self.arrows, self.misses, self.score = self.undo_stack.pop()
            self.message = "已撤销上一步操作。"
            self.draw_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = ArrowGame(root)
    root.mainloop()
