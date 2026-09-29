# 第 3 讲配图 4：10 折交叉验证示意（用于"交叉验证选阶"页）
# 数据：示意数据 —— 10 个验证 MSE 为课件给定的示意值（非真实实验输出）；
#       平均值按定义手算，可验证。
#
# 教学数字手算验证（平均值）：
#   和 = 0.41+0.38+0.45+0.40+0.42+0.39+0.44+0.41+0.43+0.40
#      = 0.79+1.24+1.64+2.06+2.45+2.89+3.30+3.73+4.13 = 4.13
#   平均 = 4.13 / 10 = 0.413
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# 中文字体（照抄 03a-gradient-descent.ipynb cell#8）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE = "#4177b7", "#a14a22"

mses = [0.41, 0.38, 0.45, 0.40, 0.42, 0.39, 0.44, 0.41, 0.43, 0.40]
assert abs(sum(mses) / 10 - 0.413) < 1e-9     # 复核手算平均值 0.413

fig, ax = plt.subplots(figsize=(8.6, 5.8))
ax.set_xlim(0, 13.6)
ax.set_ylim(0, 12.5)
ax.axis("off")

cell, gap, x0, y_top = 0.82, 0.18, 1.35, 10.6

# 图例：手绘色块横排在网格上方的空白带（legend API 会压到"块9/块10"列标）
ax.add_patch(Rectangle((x0, 11.55), 0.6, 0.42, fc=ORANGE, ec="none"))
ax.text(x0 + 0.8, 11.76, "橙 = 当考卷（验证）", fontsize=10.5, color="#333333",
        va="center", ha="left")
ax.add_patch(Rectangle((x0 + 4.6, 11.55), 0.6, 0.42, fc=BLUE, ec="none"))
ax.text(x0 + 5.4, 11.76, "蓝 = 用于训练", fontsize=10.5, color="#333333",
        va="center", ha="left")

# 顶部列标：数据被切成的 10 块（= 10 折）
for j in range(10):
    ax.text(x0 + j + 0.41, y_top + 0.32, f"块{j + 1}", fontsize=9.5,
            color="#555555", ha="center", va="bottom")

for i in range(10):
    y = y_top - 1 - i
    ax.text(x0 - 0.25, y + 0.41, f"轮{i + 1}", fontsize=10, color="#555555",
            ha="right", va="center")
    for j in range(10):
        val = (i == j)                       # 第 i 轮：第 i 块当考卷（验证）
        ax.add_patch(Rectangle((x0 + j, y), cell, cell,
                               fc=ORANGE if val else BLUE,
                               ec="white", lw=0.8, alpha=0.92 if val else 0.75))
    ax.text(x0 + 10.35, y + 0.41, f"MSE = {mses[i]:.2f}", fontsize=10.5,
            color=ORANGE, va="center")

ax.text(x0 + 4.5, y_top - 10 - 0.62, "平均验证 MSE = 0.413", fontsize=13,
        color="#333333", weight="bold", ha="center",
        bbox=dict(boxstyle="round,pad=0.35", fc="#f2f2f2", ec="#bbbbbb"))

ax.set_title("10 折交叉验证：轮流当考卷，成绩取平均", fontsize=14.5, pad=6)

out = Path(__file__).with_name("ch3-cv-folds.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
