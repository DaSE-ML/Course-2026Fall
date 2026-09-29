# 第 3 讲配图 3：两点定线（用于"正规方程"页）
# 数据：固定的两个教学点 (1, 3) 与 (3, 7)，示意数据（非采样数据）
#
# 教学数字手算验证（直线 y = 2x + 1 恰好穿过两点）：
#   x = 1:  2×1 + 1 = 3   -> 过点 (1, 3) ✓
#   x = 3:  2×3 + 1 = 7   -> 过点 (3, 7) ✓
#   （两点解两方程 a·1+b=3, a·3+b=7 -> a=2, b=1，即正规方程给出的解）
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# 中文字体（照抄 03a-gradient-descent.ipynb cell#8）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE = "#4177b7"

fig, ax = plt.subplots(figsize=(7.2, 4.8))
fig.subplots_adjust(left=0.10, right=0.96, top=0.90, bottom=0.12)

xs = np.array([0, 4])
ax.plot(xs, 2 * xs + 1, color=BLUE, lw=2.4, zorder=2)

px, py = np.array([1.0, 3.0]), np.array([3.0, 7.0])
ax.scatter(px, py, s=160, color=BLUE, edgecolors="white", linewidths=1.4, zorder=3)

# 标注两点坐标
ax.annotate("(1, 3)", (1, 3), textcoords="offset points", xytext=(-8, -18),
            fontsize=13, color=BLUE, weight="bold", ha="center")
ax.annotate("(3, 7)", (3, 7), textcoords="offset points", xytext=(4, 10),
            fontsize=13, color=BLUE, weight="bold", ha="left")

# 方程标注（放在线右上方的空白处）
# mathtext 写法渲染 ŷ（中文字体缺 U+0177 字形，交由 DejaVu 数学字体渲染）
ax.text(3.05, 4.4, r"$\hat{y} = 2x + 1$", fontsize=16, color=BLUE, weight="bold")

ax.grid(True, lw=0.4, alpha=0.35)
ax.set_xlabel("x", fontsize=12)
ax.set_ylabel("y", fontsize=12)
ax.set_title("两个点确定一条直线（正规方程的几何直观）", fontsize=13.5)
ax.set_xlim(0, 4)
ax.set_ylim(0, 8)
ax.set_xticks(range(5))
ax.set_yticks(range(0, 9, 2))

out = Path(__file__).with_name("ch3-normal-eq.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
