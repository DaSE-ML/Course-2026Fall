# 第 3 讲配图：梯度下降的"下山"比喻（用于"梯度下降"引入页）
# 数据：损失曲线 L(w) = (w − 3)²（与 03a notebook 手算同一例子，示意曲线）
#
# 教学数字手算验证：
#   L'(w) = 2(w − 3)，L'(0) = −6 < 0  ->  负梯度方向 = +6，即 w 增大（向右下坡）
#   学习率 η = 0.1 时一步更新：w₁ = 0 − 0.1 × (−6) = 0.6，L(0.6) = (0.6−3)² = 5.76 < 9 = L(0)
#   谷底：L'(3) = 0  ->  w = 3 是最低点，L(3) = 0
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

# 中文字体（照抄 03a-gradient-descent.ipynb cell#8）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE, GREEN, GRAY = "#4177b7", "#a14a22", "#23756c", "#8194aa"

grid = np.linspace(-0.9, 6.9, 300)
L = (grid - 3) ** 2

fig, ax = plt.subplots(figsize=(8.4, 5.9))
fig.subplots_adjust(left=0.09, right=0.97, top=0.90, bottom=0.11)

ax.plot(grid, L, color=BLUE, lw=2.4, zorder=2)

# 谷底：w = 3（L' = 0）
ax.scatter([3], [0], s=90, color=GREEN, edgecolors="white", linewidths=1.2, zorder=4)
ax.annotate("最低点 w = 3", (3, 0), textcoords="offset points", xytext=(10, 12),
            fontsize=12.5, color=GREEN, weight="bold")

# w = 0 处的切线（斜率 L'(0) = −6）：方向即负梯度方向
tw = np.array([-0.35, 1.8])
ax.plot(tw, 9 - 6 * tw, color=GRAY, lw=1.3, linestyle=(0, (5, 4)), zorder=1)

# 长箭头：沿切线向下的方向（负梯度）
ax.add_patch(FancyArrowPatch((0.02, 8.9), (1.2, 1.8), arrowstyle="-|>",
                             mutation_scale=22, color=ORANGE, lw=1.8,
                             shrinkA=0, shrinkB=0, zorder=3))
# 粗短箭头：实际迈出的一步（步长 = 学习率），止于方向路径中途
ax.add_patch(FancyArrowPatch((0.02, 8.9), (0.72, 4.6), arrowstyle="-|>",
                             mutation_scale=26, color=ORANGE, lw=5.5,
                             shrinkA=0, shrinkB=0, zorder=4))

ax.annotate("负梯度＝最陡下坡方向", (1.2, 1.8), textcoords="offset points",
            xytext=(14, -6), fontsize=12.5, color=ORANGE, weight="bold")
ax.annotate("步长＝学习率\n（一步别迈太大）", (0.72, 4.6), textcoords="offset points",
            xytext=(-118, -34), fontsize=11.5, color=ORANGE,
            arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1.0))

# 小人（简笔）：蒙眼（眼上一条布带），站在 w = 0 的山坡上（曲线点 (0, 9)）
fx, fy = 0.0, 9.0
ax.plot([fx, fx], [fy + 0.15, fy + 1.5], color="#333333", lw=2.2, zorder=5)   # 身体
ax.add_patch(Circle((fx, fy + 1.95), 0.4, fc="white", ec="#333333", lw=2.0, zorder=5))  # 头
ax.plot([fx - 0.42, fx + 0.42], [fy + 2.0, fy + 2.0], color=ORANGE, lw=3.4, zorder=6)   # 蒙眼布
ax.plot([fx, fx - 0.26], [fy + 0.15, fy - 0.52], color="#333333", lw=2.2, zorder=5)     # 左腿
ax.plot([fx, fx + 0.24], [fy + 0.15, fy - 0.50], color="#333333", lw=2.2, zorder=5)     # 右腿
ax.plot([fx, fx - 0.50], [fy + 1.15, fy + 0.62], color="#333333", lw=2.0, zorder=5)     # 左臂
ax.plot([fx, fx + 0.50], [fy + 1.15, fy + 0.68], color="#333333", lw=2.0, zorder=5)     # 右臂

ax.grid(True, lw=0.4, alpha=0.35)
ax.set_xlabel("参数 w", fontsize=12.5)
ax.set_ylabel("损失", fontsize=12.5)
ax.set_title("梯度下降：蒙着眼下山，每步走最陡的下坡", fontsize=13.5)
ax.set_xlim(-1.1, 6.9)
ax.set_ylim(-1.6, 15.5)
ax.set_xticks(range(-1, 7))

out = Path(__file__).with_name("ch3-downhill.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
