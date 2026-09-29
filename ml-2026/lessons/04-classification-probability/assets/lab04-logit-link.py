"""Create the p4 teaching chart linking the linear score and logit."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


OUT = Path(__file__).with_name("lab04-logit-link.png")

plt.rcParams.update({
    "font.family": "PingFang SC",
    "axes.edgecolor": "#52657a",
    "axes.labelcolor": "#192b41",
    "xtick.color": "#52657a",
    "ytick.color": "#52657a",
    "text.color": "#192b41",
    "axes.titleweight": "bold",
})

fig, (ax_linear, ax_logit) = plt.subplots(
    1,
    2,
    figsize=(9, 5.8),
    sharey=True,
    gridspec_kw={"wspace": 0.42},
)
fig.suptitle("同一个中间分数 z 的两种表达", fontsize=18, fontweight="bold", y=0.98)

z_ticks = [-4, -2, 0, 2, 4]
for ax in (ax_linear, ax_logit):
    ax.set_ylim(-4.3, 4.3)
    ax.set_yticks(z_ticks)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#dce4eb", linewidth=0.8)
    ax.axhline(0, color="#8295a8", linewidth=1.2, linestyle=(0, (4, 3)), zorder=1)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_color("#71859a")
    ax.spines["bottom"].set_color("#71859a")

# Schematic: vary one feature while holding the others fixed.
x = np.linspace(-4, 4, 300)
z = 0.8 * x + 0.25
ax_linear.plot(x, z, color="#4177b7", linewidth=3, zorder=2)
ax_linear.set_xlim(-4.3, 4.3)
ax_linear.set_xticks([-4, -2, 0, 2, 4])
ax_linear.set_title("线性预测（示意）\nz = w₁x₁ + c", fontsize=15, pad=12)
ax_linear.set_xlabel("一个特征 x₁（其余固定）", fontsize=13, labelpad=9)
ax_linear.set_ylabel("线性分数 z", fontsize=14, labelpad=9)
ax_linear.text(
    0.04,
    0.05,
    "只让一个特征变化",
    transform=ax_linear.transAxes,
    fontsize=11,
    color="#52657a",
)

# Logit: the horizontal coordinate is probability; its open interval is (0, 1).
p = np.linspace(0.018, 0.982, 800)
logit = np.log(p / (1 - p))
ax_logit.plot(p, logit, color="#23756c", linewidth=3, zorder=2)
ax_logit.set_xlim(0, 1)
ax_logit.set_xticks([0, 0.5, 1], labels=["0", "0.5", "1"])
ax_logit.set_title("模型概率取 logit\nz = ln[p(x)/(1−p(x))]", fontsize=15, pad=12)
ax_logit.set_xlabel("模型概率 p(x)（0 < p(x) < 1）", fontsize=13, labelpad=9)
ax_logit.yaxis.tick_right()
ax_logit.yaxis.set_label_position("right")
ax_logit.set_ylabel("线性分数 z", fontsize=14, labelpad=9)
ax_logit.tick_params(axis="y", which="both", right=True, labelright=True, left=False, labelleft=False)
ax_logit.spines["left"].set_visible(False)
ax_logit.spines["right"].set_color("#71859a")
ax_logit.grid(axis="x", color="#edf1f5", linewidth=0.8)
ax_logit.scatter([0.5], [0], s=38, color="#23756c", zorder=3)
ax_logit.annotate(
    "p(x) = 0.5 时 z = 0",
    xy=(0.5, 0),
    xytext=(0.57, -1.2),
    fontsize=11,
    color="#23756c",
    arrowprops={"arrowstyle": "-", "color": "#23756c", "lw": 1},
)

fig.text(
    0.5,
    0.025,
    "左右横轴含义不同；两边纵轴都是 z，刻度相同。",
    ha="center",
    fontsize=11,
    color="#52657a",
)
fig.subplots_adjust(left=0.1, right=0.9, top=0.82, bottom=0.16)
fig.savefig(OUT, dpi=200, facecolor="white")
print(OUT)
