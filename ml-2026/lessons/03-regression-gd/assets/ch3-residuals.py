# 第 3 讲配图 2：残差几何（用于"损失：MSE"页）
# 数据：手工布置的 6 个点（教学数字必须可手算，故不用随机数；示意数据）
#   基准直线 y0 = 0.5x + 1，x = 1..6  ->  y0 = [1.5, 2, 2.5, 3, 3.5, 4]
#   噪声 ε = [0.4, -0.5, 0.1, 0.1, -0.5, 0.4]（对称布置：Σε = 0 且 Σ(x-x̄)ε = 0）
#   -> y = [1.9, 1.5, 2.6, 3.1, 3.0, 4.4]
#
# 教学数字手算验证：
#   x̄ = (1+2+3+4+5+6)/6 = 3.5，ȳ = (1.9+1.5+2.6+3.1+3.0+4.4)/6 = 16.5/6 = 2.75
#   最小二乘斜率 = Σ(x-x̄)(y-ȳ) / Σ(x-x̄)² = 8.75 / 17.5 = 0.5
#   截距 = ȳ - 0.5×x̄ = 2.75 - 1.75 = 1  ->  拟合线恰为 ŷ = 0.5x + 1
#   各点残差 y - ŷ = [0.4, -0.5, 0.1, 0.1, -0.5, 0.4]
#   MSE = (0.16 + 0.25 + 0.01 + 0.01 + 0.25 + 0.16) / 6 = 0.84 / 6 = 0.14
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# 中文字体（照抄 03a-gradient-descent.ipynb cell#8）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE = "#4177b7", "#a14a22"

x = np.arange(1, 7, dtype=float)
y = np.array([1.9, 1.5, 2.6, 3.1, 3.0, 4.4])

# 复核：最小二乘解应恰为 0.5, 1.0（手算见文件头注释）
slope, intercept = np.polyfit(x, y, 1)
print(f"复核最小二乘: slope={slope:.4f} (应为0.5), intercept={intercept:.4f} (应为1)")

fig, ax = plt.subplots(figsize=(7.2, 4.8))
fig.subplots_adjust(left=0.10, right=0.96, top=0.90, bottom=0.12)

xs = np.array([0.4, 6.6])
ax.plot(xs, 0.5 * xs + 1, color=BLUE, lw=2.2, zorder=2)

# 每个点到直线的竖直残差线段（橙色竖虚线）
ax.vlines(x, 0.5 * x + 1, y, color=ORANGE, lw=1.8, linestyle=(0, (4, 3)), zorder=2)

ax.scatter(x, y, s=62, color=BLUE, edgecolors="white", linewidths=0.8, zorder=3)

# 角落文字框（MSE 定义：各段竖线长度的平方和 ÷ 点数）
ax.text(0.03, 0.95, "MSE = 各段竖线长度的平方和 ÷ 点数",
        transform=ax.transAxes, fontsize=12.5, color=ORANGE, va="top",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=ORANGE, lw=1.0, alpha=0.9))

ax.grid(True, lw=0.4, alpha=0.35)
ax.set_xlabel("x", fontsize=12)
ax.set_ylabel("y", fontsize=12)
ax.set_title("损失：每条竖线的平方，平均成一个数", fontsize=13.5)
ax.set_xlim(0.4, 6.6)
ax.set_ylim(0.5, 5.2)

out = Path(__file__).with_name("ch3-residuals.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
