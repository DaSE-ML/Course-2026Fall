# 三个"化"的对比示意图：标准化 / 归一化 / 正则化，三栏横排，白底
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

BLUE = "#2077B4"
ORANGE = "#E8740C"
GRAY = "#555555"

rng = np.random.default_rng(42)

fig, axes = plt.subplots(1, 3, figsize=(14.4, 5.0))
fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.06, wspace=0.05)


def setup(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")


def tag(ax, text, color):
    ax.text(0.15, 9.55, text, fontsize=13, color="white", weight="bold",
            va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.32", fc=color, ec="none"))


def arrow(ax, x0, x1, y, label):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>",
                                 mutation_scale=24, color=GRAY, lw=2))
    ax.text((x0 + x1) / 2 - 0.25, y + 0.62, label, fontsize=12.5, color=GRAY, ha="center")


# ---------- 第一栏：标准化 ----------
ax = axes[0]
setup(ax)
tag(ax, "管数据", BLUE)
ax.set_title("标准化 Standardization", fontsize=20.5, weight="bold", pad=10)

# 前：两把长度悬殊的数轴（身高范围 50，收入范围 50000）
ax.add_patch(Rectangle((0.5, 7.5), 0.28, 0.55, fc=BLUE, ec="none", alpha=0.85))
ax.text(0.95, 8.45, "身高（cm）150~200", fontsize=12, color=GRAY)
ax.add_patch(Rectangle((0.5, 5.7), 3.1, 0.55, fc=BLUE, ec="none", alpha=0.85))
ax.text(0.95, 6.65, "收入（元）0~50000", fontsize=12, color=GRAY)
ax.text(2.05, 4.85, "尺度相差上千倍", fontsize=12, color=BLUE, ha="center")

arrow(ax, 4.35, 5.25, 6.9, "按列统一")

# 后：两条完全一致的点带，都以 0 为中心
for y in (7.75, 5.95):
    ax.plot([5.9, 9.8], [y, y], color="#bbbbbb", lw=1)
    dots = 7.85 + rng.normal(0, 0.68, 42)
    ax.scatter(dots, np.full(42, y), s=14, color=BLUE, alpha=0.75, zorder=3)
ax.text(7.85, 8.5, "均值 0、方差 1", fontsize=12, color=BLUE, ha="center")
ax.text(7.9, 4.85, "两列尺度一致，大小顺序不变", fontsize=12, color=BLUE, ha="center")

ax.text(5, 1.15, "减均值、除标准差，逐列（跨样本）计算\n处理后无固定范围", fontsize=16,
        color=GRAY, ha="center", linespacing=1.6)

# ---------- 第二栏：归一化 ----------
ax = axes[1]
setup(ax)
tag(ax, "管数据", BLUE)
ax.set_title("归一化 Normalization", fontsize=20.5, weight="bold", pad=10)

# 前：0~100 的分数数轴
x0, x1 = 0.6, 4.4
ax.plot([x0, x1], [6.9, 6.9], color="#999999", lw=1.5)
scores = np.array([62, 71, 78, 85, 93])
ax.scatter(x0 + scores / 100 * (x1 - x0), np.full(5, 6.9), s=42, color=BLUE, zorder=3)
for t, lab in [(0, "0"), (50, "50"), (100, "100")]:
    xt = x0 + t / 100 * (x1 - x0)
    ax.plot([xt, xt], [6.72, 7.08], color="#999999", lw=1.2)
    ax.text(xt, 6.15, lab, fontsize=11.5, color=GRAY, ha="center")
ax.text(2.5, 7.7, "考试分数 0~100", fontsize=9.5, color=GRAY, ha="center")

arrow(ax, 4.95, 5.7, 6.9, "归一化")

# 后：同样的分数被压进 [0,1] 的小框
bx0, bx1 = 6.3, 8.1
ax.add_patch(Rectangle((bx0, 6.55), bx1 - bx0, 0.7, fc="#e8f1f8", ec=BLUE, lw=1.4))
ax.scatter(bx0 + scores / 100 * (bx1 - bx0), np.full(5, 6.9), s=42, color=BLUE, zorder=3)
ax.text(bx0, 6.0, "0", fontsize=11.5, color=GRAY, ha="center")
ax.text(bx1, 6.0, "1", fontsize=11.5, color=GRAY, ha="center")
ax.text(7.45, 7.7, "全部落进 [0, 1]", fontsize=12, color=BLUE, ha="center")
ax.text(7.2, 4.85, "只由最大、最小值决定", fontsize=12, color=BLUE, ha="center")

ax.text(5, 1.15, "线性缩放到固定区间（如 [0, 1]）\n对最大最小值（异常值）敏感", fontsize=16,
        color=GRAY, ha="center", linespacing=1.6)

# ---------- 第三栏：正则化 ----------
ax = axes[2]
setup(ax)
tag(ax, "管模型", ORANGE)
ax.set_title("正则化 Regularization", fontsize=20.5, weight="bold", pad=10)

xs = np.linspace(0.06, 0.94, 12)
ys = np.sin(xs * 2.2 * np.pi) * 0.3 + 0.5 + rng.normal(0, 0.1, 12)

for k, (label, deg) in enumerate([("过拟合：死记每个点", 11), ("加正则化：只抓趋势", 3)]):
    ins = ax.inset_axes([0.03 + k * 0.5, 0.34, 0.44, 0.52], transform=ax.transAxes)
    ins.set_xlim(0, 1)
    ins.set_ylim(-0.25, 1.25)
    ins.set_xticks([])
    ins.set_yticks([])
    for s in ins.spines.values():
        s.set_color("#cccccc")
    ins.scatter(xs, ys, s=22, color="#888888", zorder=3)
    coef = np.polyfit(xs, ys, deg)
    xx = np.linspace(0.02, 0.98, 300)
    ins.plot(xx, np.polyval(coef, xx), color=ORANGE, lw=2.2)
    ins.set_title(label, fontsize=12, color=GRAY, pad=4)

ax.text(5, 2.9, "惩罚过大的模型参数，让曲线平滑", fontsize=12.5, color=ORANGE, ha="center")

ax.text(5, 1.15, "在损失函数中加入参数惩罚项（如 λ·R(θ)）\n训练时约束模型复杂度，防止过拟合",
        fontsize=10.5, color=GRAY, ha="center", linespacing=1.6)

# ---------- 底部横幅 ----------
fig.savefig("lessons/02-first-workflow/assets/three-izations-comparison-v1.png",
            dpi=200, facecolor="white")
print("saved")
