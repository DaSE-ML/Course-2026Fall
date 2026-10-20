# 第 6 讲配图：靶心图比喻（用于"比喻：靶心图——偏差与方差"页）
# 合成示意图（固定 seed）：2×2 四张靶，每靶 4 个弹孔，位置按四种模式手工布置
#   甲：四枪紧抱靶心（想准也真准）
#   乙：散在靶心四周（平均不离靶心，枪枪不稳）
#   丙：整齐偏在同一角落（很稳，瞄错了地方）
#   丁：又偏又散（瞄错且不稳）
# 弹孔基准坐标手工给定，另加 seed=42 的 ±0.02 微扰；同心圆靶 + 弹孔点，非实弹数据
# 标注只用生活词（准/稳/偏/散），不写偏差方差术语（正式命名在下一页正文）
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

# 中文字体（照抄 ch3-galton.py）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

GRAY, DARK, RED = "#8194aa", "#333333", "#a14a22"

# 手工布置的弹孔基准位置（靶半径 = 1，靶心 = 原点），键序即版面序：左上、右上、左下、右下
HOLES = {
    "甲：又准又稳": [(0.05, 0.07), (-0.09, 0.01), (0.02, -0.10), (0.11, -0.03)],
    "乙：准而不稳": [(-0.55, 0.45), (0.60, 0.28), (-0.28, -0.60), (0.32, -0.52)],
    "丙：稳而不准": [(0.60, 0.64), (0.46, 0.70), (0.66, 0.50), (0.48, 0.55)],
    "丁：又偏又散": [(0.15, -0.10), (0.78, -0.42), (0.02, -0.88), (0.72, -0.15)],
}

# 复核四种模式的均值（仅打印，不进图）：乙平均在靶心附近，丙均值整体偏右上，丁均值偏且散
for name, pts in HOLES.items():
    arr = np.array(pts)
    print(f"{name}  均值 = ({arr[:, 0].mean():+.2f}, {arr[:, 1].mean():+.2f})")

rng = np.random.default_rng(42)          # 固定 seed：只做 ±0.02 的微扰

fig, axes = plt.subplots(2, 2, figsize=(8.6, 9.2))
fig.subplots_adjust(left=0.04, right=0.96, top=0.90, bottom=0.03, wspace=0.10, hspace=0.14)

for ax, (label, base) in zip(axes.flat, HOLES.items()):
    holes = np.array(base) + rng.uniform(-0.02, 0.02, size=(len(base), 2))
    for r in (1.0, 0.75, 0.5):                       # 同心圆靶：三道外环
        ax.add_patch(Circle((0, 0), r, fc="white", ec=GRAY, lw=1.2, zorder=1))
    ax.add_patch(Circle((0, 0), 0.25, fc=RED, alpha=0.25, ec=RED, lw=1.2, zorder=2))
    ax.plot(0, 0, "+", color=GRAY, markersize=9, zorder=3)       # 靶心十字
    ax.scatter(holes[:, 0], holes[:, 1], s=90, color=DARK, zorder=5,
               edgecolors="white", linewidths=1.0)               # 弹孔
    ax.text(0, -1.22, label, ha="center", va="top", fontsize=13.5, color=DARK)
    ax.set_xlim(-1.32, 1.32)
    ax.set_ylim(-1.42, 1.32)
    ax.set_aspect("equal")
    ax.axis("off")

fig.suptitle("四张靶纸：先看瞄得正不正，再看稳不稳", fontsize=15.5)

out = Path(__file__).with_name("ch6-target-diagram.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
