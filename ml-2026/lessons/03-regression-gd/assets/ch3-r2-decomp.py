# 第 3 讲配图 5：R² 直觉（用于"R²"页）
# 数据：与 ch3-residuals.py 同一套手工布置点（示意数据，教学数字可手算）
#   基准直线 y0 = 0.5x + 1，x = 1..6；噪声 ε = [0.4, -0.5, 0.1, 0.1, -0.5, 0.4]
#   -> y = [1.9, 1.5, 2.6, 3.1, 3.0, 4.4]，最小二乘拟合线恰为 ŷ = 0.5x + 1
#
# 教学数字手算验证：
#   ȳ = 16.5 / 6 = 2.75（均值线）
#   SS_res = Σ(y - ŷ)² = (0.16 + 0.25 + 0.01 + 0.01 + 0.25 + 0.16) = 0.84（各点到拟合线）
#   SS_tot = Σ(y - ȳ)²
#          = (-0.85)² + (-1.25)² + (-0.15)² + (0.35)² + (0.25)² + (1.65)²
#          = 0.7225 + 1.5625 + 0.0225 + 0.1225 + 0.0625 + 2.7225 = 5.215（各点到均值线）
#   R² = 1 - SS_res / SS_tot = 1 - 0.84 / 5.215 ≈ 1 - 0.161 = 0.839
#   选中展示的点 (6, 4.4)：残差 = 4.4 - (0.5×6+1) = 0.4；总偏差 = 4.4 - 2.75 = 1.65
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# 中文字体（照抄 03a-gradient-descent.ipynb cell#8）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE, GRAY = "#4177b7", "#a14a22", "#8194aa"

x = np.arange(1, 7, dtype=float)
y = np.array([1.9, 1.5, 2.6, 3.1, 3.0, 4.4])
ybar = y.mean()

# 复核手算（见文件头注释）
slope, intercept = np.polyfit(x, y, 1)
ss_res = float(np.sum((y - (slope * x + intercept)) ** 2))
ss_tot = float(np.sum((y - ybar) ** 2))
print(f"复核: slope={slope:.4f}(0.5) intercept={intercept:.4f}(1) "
      f"SS_res={ss_res:.4f}(0.84) SS_tot={ss_tot:.4f}(5.215) R2={1 - ss_res / ss_tot:.4f}(0.839)")

fig, ax = plt.subplots(figsize=(7.6, 5.0))
fig.subplots_adjust(left=0.10, right=0.96, top=0.90, bottom=0.12)

xs = np.array([0.4, 6.7])
# ŷ、ȳ、² 等字符中文字体缺字形，一律用 mathtext（由 DejaVu 数学字体渲染）
ax.plot(xs, 0.5 * xs + 1, color=BLUE, lw=2.2, zorder=2,
        label=r"拟合线 $\hat{y} = 0.5x + 1$")
ax.axhline(ybar, color=GRAY, lw=1.8, linestyle="--", zorder=1,
           label=rf"均值线 $\bar{{y}}$ = {ybar:.2f}")

ax.scatter(x, y, s=58, color=BLUE, edgecolors="white", linewidths=0.8, zorder=3)

# 选中点 (6, 4.4)：橙色竖线段 = 残差（到拟合线）；灰色竖线段 = 总偏差（到均值线）
# 两条竖线水平错开 0.16，避免重叠遮挡
ax.vlines([6.0], [4.0], [4.4], color=ORANGE, lw=3.2, zorder=4)
ax.vlines([6.16], [ybar], [4.4], color=GRAY, lw=3.2, zorder=4)
ax.scatter([6.0], [4.4], s=120, facecolors="none", edgecolors=ORANGE, linewidths=1.6, zorder=5)

ax.annotate("残差 = 0.4\n（到拟合线）", (6.0, 4.16), textcoords="offset points",
            xytext=(-78, 4), fontsize=10.5, color=ORANGE, ha="left")
ax.annotate("总偏差 = 1.65\n（到均值线）", (6.16, 3.5), textcoords="offset points",
            xytext=(10, -6), fontsize=10.5, color="#5a6b80", ha="left")

ax.text(0.03, 0.965,
        r"$SS_{res}$ = 橙线平方和 = 0.84" + "\n"
        r"$SS_{tot}$ = 灰线平方和 = 5.215" + "\n"
        r"$R^2$ = 1 - 0.84/5.215 ≈ 0.84",
        transform=ax.transAxes, fontsize=11, color="#333333", va="top",
        bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="#bbbbbb"))

ax.grid(True, lw=0.4, alpha=0.35)
ax.set_xlabel("x", fontsize=12)
ax.set_ylabel("y", fontsize=12)
ax.set_title(r"$R^2$：拟合线比均值线好多少", fontsize=13.5)
ax.set_xlim(0.4, 6.9)
ax.set_ylim(0.4, 5.3)
ax.legend(loc="lower right", fontsize=10, frameon=True)

out = Path(__file__).with_name("ch3-r2-decomp.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
