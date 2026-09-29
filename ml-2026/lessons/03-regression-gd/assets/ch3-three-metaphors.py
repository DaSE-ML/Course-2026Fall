# 第 3 讲配图：五格比喻总结（用于"本章总结"页，竖版 3×2 网格）
# 数据：纯示意排版图，无数据计算；图标全部用几何图形自绘
#   （emoji 字符在 PingFang SC 中文字体链中缺字形会渲染成方框，故一律不用 emoji，
#     用简笔图形表达：尺子直线 / 山坡箭头 / 打开的书 / 勾选考卷 / 扭曲过拟合曲线）
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle

# 中文字体（照抄 03a-gradient-descent.ipynb cell#8）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE, GREEN, GRAY = "#4177b7", "#a14a22", "#23756c", "#8194aa"
INK, SUB = "#333333", "#555555"

fig, axes = plt.subplots(3, 2, figsize=(8.4, 13.4))
fig.subplots_adjust(left=0.025, right=0.975, top=0.93, bottom=0.018, wspace=0.12, hspace=0.15)

fig.suptitle("五个比喻串起本章", fontsize=22, weight="bold", color=INK, y=0.965)


def new_cell(ax, tag, tag_color):
    """统一格子：圆角浅框 + 右上角标签。内部坐标系 0~10。"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_aspect("auto")
    ax.add_patch(FancyBboxPatch((0.25, 0.4), 9.5, 9.2,
                                boxstyle="round,pad=0.12,rounding_size=0.55",
                                fc="white", ec="#d5dde6", lw=1.4))
    ax.text(9.25, 9.15, tag, fontsize=12.5, color="white", weight="bold",
            ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.38", fc=tag_color, ec="none"))


def cell_text(ax, name, line1, line2):
    ax.text(5, 3.42, name, fontsize=19.5, weight="bold", color=INK, ha="center", va="center")
    ax.text(5, 1.95, line1, fontsize=13.5, color=SUB, ha="center", va="center")
    ax.text(5, 1.05, line2, fontsize=13.5, color=SUB, ha="center", va="center")


# ---------- 格 1：直线（模型） ----------
ax = axes[0][0]
new_cell(ax, "模型", BLUE)
px = np.array([2.0, 3.5, 5.0, 6.5, 8.0])
py = np.array([6.2, 5.8, 5.4, 4.9, 4.6])
ax.plot([1.4, 8.6], [6.55, 4.15], color=BLUE, lw=2.6, zorder=2)
ax.scatter(px, py, s=52, color=BLUE, alpha=0.85, edgecolors="white", linewidths=0.7, zorder=3)
ax.add_patch(Rectangle((2.2, 7.0), 5.6, 1.1, fc="#eef3f9", ec=BLUE, lw=1.4))
for i in range(12):                      # 尺子刻度
    xt = 2.5 + i * 0.46
    ax.plot([xt, xt], [7.12, 7.45 + (0.28 if i % 2 == 0 else 0.0)],
            color=BLUE, lw=1.1)
cell_text(ax, "直线", "最好的直线", "离所有点最近")

# ---------- 格 2：下山（求解） ----------
ax = axes[0][1]
new_cell(ax, "求解", ORANGE)
ax.add_patch(Polygon([(1.0, 4.6), (4.9, 4.6), (2.9, 8.9)], fc="#dce8e6", ec=GREEN, lw=1.6))
ax.add_patch(Polygon([(4.2, 4.6), (9.0, 4.6), (6.7, 7.3)], fc="#eef1f4", ec=GRAY, lw=1.4))
ax.annotate("", xy=(4.35, 4.9), xytext=(3.15, 7.6),          # 沿山坡向下的橙色箭头
            arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=3.2,
                            mutation_scale=24, shrinkA=0, shrinkB=0))
ax.scatter([5.6], [4.6], s=60, color=GREEN, zorder=4)        # 谷底
cell_text(ax, "下山", "每步走最陡下坡", "步长别太大")

# ---------- 格 3：读书（SGD） ----------
ax = axes[1][0]
new_cell(ax, "SGD", GREEN)
# 打开的书（正视摊开：中缝高、两页向外下垂）
ax.add_patch(Polygon([(5.0, 7.3), (1.6, 6.1), (1.6, 4.5), (5.0, 5.7)],
                     fc="#eef3f9", ec=BLUE, lw=1.6))
ax.add_patch(Polygon([(5.0, 7.3), (8.4, 6.1), (8.4, 4.5), (5.0, 5.7)],
                     fc="#e2ecf7", ec=BLUE, lw=1.6))
for y1, y2 in ((6.72, 5.62), (6.14, 5.04)):  # 每页两行"文字"线，沿页面向外下斜
    ax.plot([2.05, 4.62], [y2, y1], color=GRAY, lw=1.2)      # 左页
    ax.plot([5.38, 7.95], [y1, y2], color=GRAY, lw=1.2)      # 右页
ax.plot([5.0, 5.0], [5.7, 7.3], color=BLUE, lw=1.8)          # 中缝
cell_text(ax, "读书", "不用读完全书", "翻一篇学一点")

# ---------- 格 4：考卷（交叉验证） ----------
ax = axes[1][1]
new_cell(ax, "交叉验证", ORANGE)
ax.add_patch(Rectangle((3.0, 4.4), 4.4, 4.2, angle=-4, fc="white",
                       ec=GRAY, lw=1.6))
for yy in (7.7, 7.05, 6.4):              # 卷面横线
    ax.plot([3.6, 6.8], [yy, yy], color="#c3cdd8", lw=1.4)
ax.plot([4.15, 4.75, 5.9], [5.35, 4.85, 6.05], color=GREEN, lw=3.0,
        solid_capstyle="round", solid_joinstyle="round")      # 大勾
ax.add_patch(Circle((7.55, 7.9), 0.62, fc="white", ec=ORANGE, lw=2.2))
ax.text(7.55, 7.9, "分", fontsize=12, color=ORANGE, weight="bold",
        ha="center", va="center")
cell_text(ax, "考卷", "轮流当考卷", "成绩才公平")

# ---------- 格 5：死记硬背（诊断） ----------
ax = axes[2][0]
new_cell(ax, "诊断", GRAY)
sx = np.array([1.9, 3.2, 4.6, 6.0, 7.4, 8.5])
sy = np.array([5.3, 6.7, 5.1, 6.9, 5.4, 6.4])
coef = np.polyfit(sx, sy, 5)             # 5 次多项式恰好穿过 6 个点 = "死记硬背"
xx = np.linspace(sx.min(), sx.max(), 240)  # 只画散点区间，避免多项式两端外推爆冲
ax.plot(xx, np.polyval(coef, xx), color=ORANGE, lw=2.4, zorder=2)
ax.scatter(sx, sy, s=50, color=BLUE, edgecolors="white", linewidths=0.7, zorder=3)
ax.plot([7.9, 8.7], [8.3, 7.5], color=ORANGE, lw=2.2)        # 自绘叉号
ax.plot([8.7, 7.9], [8.3, 7.5], color=ORANGE, lw=2.2)
cell_text(ax, "死记硬背", "曲线把每个点都记住", "就是过拟合")

# ---------- 格 6：收尾（一条主线） ----------
ax = axes[2][1]
new_cell(ax, "主线", BLUE)
ax.text(5, 6.4, "直线 → 下山 → 读书 → 考卷 → 防背书", fontsize=14.5,
        color=INK, ha="center", va="center")
ax.text(5, 4.3, "模型 · 求解 · 加速 · 评估 · 诊断", fontsize=13.5,
        color=SUB, ha="center", va="center")
ax.text(5, 2.6, "下一讲：概率与统计，让这些工具更稳", fontsize=12.5,
        color="#8896a6", ha="center", va="center")

out = Path(__file__).with_name("ch3-three-metaphors.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
