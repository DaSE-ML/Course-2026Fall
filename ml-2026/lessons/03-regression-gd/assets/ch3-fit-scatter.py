# 第 3 讲配图 1：面积-房价散点 + 拟合直线（用于"本章定位"页）
# 数据：脚本合成的示意数据（非真实成交数据），seed=42 保证可复现
#   价格(万元) = 3 × 面积(㎡) + 50 + 噪声，噪声 ~ N(0, 40^2)
#
# 教学数字手算验证（真直线 3x + 50 上的点）：
#   面积  30 ㎡  ->  3×30 + 50 = 140 万元
#   面积  100 ㎡ ->  3×100 + 50 = 350 万元
#   面积 150 ㎡  ->  3×150 + 50 = 500 万元
#   （散点因噪声在直线附近上下波动，σ = 40 万元）
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# 中文字体（照抄 03a-gradient-descent.ipynb cell#8）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE = "#4177b7"

rng = np.random.default_rng(42)                  # 固定 seed，图完全可复现
area = rng.uniform(30, 150, 24)                  # 24 个点，面积约 30–150 ㎡
price = 3 * area + 50 + rng.normal(0, 40, 24)    # 真直线 3x+50 加 σ=40 的噪声

fig, ax = plt.subplots(figsize=(7.2, 4.8))
fig.subplots_adjust(left=0.11, right=0.96, top=0.90, bottom=0.12)

ax.scatter(area, price, s=46, color=BLUE, alpha=0.85,
           edgecolors="white", linewidths=0.6, zorder=3)

xs = np.array([25, 155])
ax.plot(xs, 3 * xs + 50, color=BLUE, lw=2.2, zorder=2)
# mathtext 写法渲染 ŷ（中文字体缺 U+0177 字形，交由 DejaVu 数学字体渲染）
ax.text(128, 3 * 128 + 50 - 68, r"$\hat{y} = 3x + 50$", fontsize=13, color=BLUE,
        ha="center", weight="bold")

ax.grid(True, lw=0.4, alpha=0.35)
ax.set_xlabel("面积（㎡）", fontsize=12)
ax.set_ylabel("成交价（万元）", fontsize=12)
ax.set_title("线性回归：用一条直线概括面积与价格的关系", fontsize=13.5)
ax.set_xlim(20, 160)

out = Path(__file__).with_name("ch3-fit-scatter.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
