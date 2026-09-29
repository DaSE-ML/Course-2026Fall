# 第 3 讲配图：外推警示（用于"外推警示"页）
# 数据与 ch3-fit-scatter.py 同参数（seed=42）：24 条记录，面积约 30–150 ㎡，
#   价格(万元) = 3 × 面积(㎡) + 50 + N(0, 40²)
# 直线沿用第 1 页（ch3-fit-scatter.py）读图口径 ŷ = 3x + 50：
#   实线段画在 30–150 ㎡（有成交记录）；虚线是同一条线延伸到 300 ㎡（外推区，无成交记录）
# 教学读数（真直线手算）：面积 300 ㎡ → 3×300+50 = 950 万元；面积 500 ㎡ → 1550 万元
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# 中文字体（照抄 ch3-fit-scatter.py）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE, GRAY = "#4177b7", "#a14a22", "#8194aa"

rng = np.random.default_rng(42)                  # 与 ch3-fit-scatter.py 同 seed
area = rng.uniform(30, 150, 24)                  # 24 个点，面积约 30–150 ㎡
price = 3 * area + 50 + rng.normal(0, 40, 24)    # 真直线 3x+50 加 σ=40 的噪声

fig, ax = plt.subplots(figsize=(8.0, 4.8))
fig.subplots_adjust(left=0.095, right=0.97, top=0.90, bottom=0.12)

# 外推区阴影（150–300 ㎡）与数据边界
ax.axvspan(150, 300, color=ORANGE, alpha=0.10, zorder=0)
ax.axvline(150, color=GRAY, lw=1.2, ls=":", zorder=1)
ax.text(150, 1032, " 数据右边界 150 ㎡ ", fontsize=10, color=GRAY,
        ha="left", va="top")
ax.text(228, 120, "外推区：无成交记录", fontsize=12.5, color=ORANGE,
        ha="center", weight="bold")

# 拟合直线：实线 30–150，虚线延伸 150–300（同一条线 ŷ = 3x + 50）
xs_in = np.array([30, 150])
xs_out = np.array([150, 300])
ax.plot(xs_in, 3 * xs_in + 50, color=BLUE, lw=2.4, zorder=3)
ax.plot(xs_out, 3 * xs_out + 50, color=BLUE, lw=2.2, ls="--", zorder=3)
ax.text(57, 185, r"$\hat{y} = 3x + 50$", fontsize=13, color=BLUE, weight="bold")

ax.scatter(area, price, s=46, color=BLUE, alpha=0.85,
           edgecolors="white", linewidths=0.6, zorder=4)

# 300 ㎡ 处的读数：数字能算出来，区间里没有任何成交记录
ax.scatter([300], [950], s=80, facecolors="white", edgecolors=ORANGE,
           linewidths=2.0, zorder=5)
ax.annotate("300 ㎡ 读数约 950 万", xy=(298, 952), xytext=(188, 918),
            fontsize=11.5, color=ORANGE,
            arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.2))

ax.grid(True, lw=0.4, alpha=0.35)
ax.set_xlabel("面积（㎡）", fontsize=12)
ax.set_ylabel("成交价（万元）", fontsize=12)
ax.set_title("外推警示：直线只在数据范围内可信", fontsize=13.5)
ax.set_xlim(20, 310)
ax.set_ylim(0, 1060)
ax.set_xticks(range(50, 301, 50))

fig.subplots_adjust(bottom=0.16)
fig.subplots_adjust(bottom=0.24)
quote_lines = [
    '马克·吐温按 176 年的观测外推：742 年后密西西比河将只剩 1.75 英里长。',
    '“There is something fascinating about science: one gets such wholesale returns of conjecture',
    'out of such a trifling investment of fact.” — Mark Twain, Life on the Mississippi (1883)',
]
fig.text(0.5, 0.006, chr(10).join(quote_lines),
    ha='center', va='bottom', fontsize=9.5, color='#52657a', linespacing=1.7)
out = Path(__file__).with_name("ch3-extrapolation.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
