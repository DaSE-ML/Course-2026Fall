# 第 3 讲配图：高尔顿"向均值回归"示意（用于"小故事：为什么叫'回归'？"页）
# 合成示意数据（seed=42），非真实身高数据：
#   父母身高 x ~ N(170, 7²)，截断到 [150, 190] cm，取 n=200
#   子女身高 = 160.5 + 0.55·(x − 160.5) + N(0, 3.5²)（斜率明显小于 1 → 向均值回归）
# 画散点 + 拟合直线（LinearRegression 对散点再拟合，实测斜率 ≈ 0.56）+ 对角参考虚线 y = x
# 拟合线斜率 < 1：右上段落到对角线下方（孩子平均略矮），左下段抬到对角线上方（孩子平均略高）
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# 中文字体（照抄 ch3-fit-scatter.py）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE, GREEN, GRAY = "#4177b7", "#23756c", "#8194aa"

rng = np.random.default_rng(42)
x = rng.normal(170, 7, 2000)
x = x[(x >= 150) & (x <= 190)][:200]             # 截断到 [150, 190] cm
child = 160.5 + 0.55 * (x - 160.5) + rng.normal(0, 3.5, x.size)

reg = LinearRegression().fit(x[:, None], child)
w, b = reg.coef_[0], reg.intercept_
print(f"复核拟合直线：斜率 {w:.3f}，截距 {b:.2f}")

fig, ax = plt.subplots(figsize=(7.2, 6.2))
fig.subplots_adjust(left=0.11, right=0.97, top=0.92, bottom=0.11)

lo, hi = 148, 194
ax.set_aspect("equal")
ax.plot([lo, hi], [lo, hi], color=GRAY, lw=1.3, ls="--", zorder=2)   # y = x
xs = np.array([150.0, 190.0])
ax.plot(xs, reg.predict(xs[:, None]), color=GREEN, lw=2.4, zorder=3)
ax.scatter(x, child, s=38, color=BLUE, alpha=0.8,
           edgecolors="white", linewidths=0.5, zorder=4)

ax.text(174.0, 176.3, "y = x：孩子与父母同高", color=GRAY, fontsize=10.5,
        rotation=45, ha="center", va="bottom")
ax.text(151.5, 186.5, "拟合直线：斜率 ≈ 0.56（小于 1）", color=GREEN,
        fontsize=11.5, weight="bold")
ax.text(190.5, 167.5, "极高父母的孩子\n平均略矮", color="#a14a22",
        fontsize=11, ha="right", va="top")
ax.text(151.5, 150.5, "极矮父母的孩子\n平均略高", color="#a14a22",
        fontsize=11, ha="left", va="bottom")

ax.grid(True, lw=0.4, alpha=0.35)
ax.set_xlabel("父母身高（cm）", fontsize=12)
ax.set_ylabel("子女身高（cm）", fontsize=12)
ax.set_title("向均值回归（合成示意数据）", fontsize=13.5)
ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)

out = Path(__file__).with_name("ch3-galton.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
