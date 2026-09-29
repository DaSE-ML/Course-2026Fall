# 第 3 讲配图：三条候选直线（用于"模型 = 一条直线 / 哪条最好"页）
# 数据：脚本合成示意数据 —— 8 个点沿 y = 2x + 1 手工布置小扰动（非随机采样）：
#   x = [0.5, 1.5, ..., 7.5]，y = 2x + 1 + ε，ε = [0.6, -0.8, 0.5, -0.4, 0.7, -0.6, 0.4, -0.5]
#   -> y = [2.6, 3.2, 6.5, 7.6, 10.7, 11.4, 14.4, 15.5]
#
# 教学数字手算验证（"较优"绿线恰为生成直线，残差即 ε）：
#   MSE(绿) = Σε²/8 = (0.36+0.64+0.25+0.16+0.49+0.36+0.16+0.25)/8 = 2.67/8 ≈ 0.33（最小）
#   MSE(灰 y=x+1)：残差 = [1.1, 0.7, 3.0, 3.1, 5.2, 4.9, 6.9, 7.0]，平方和远大
#   MSE(蓝 y=3x+0.5)：残差 = [0.6, -1.8, -1.5, -3.4, -3.3, -5.6, -5.6, -7.5]，平方和也大
#   -> 绿线最贴合点云，直观表达"哪条线最好要看离所有点的竖线总长"
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# 中文字体（照抄 03a-gradient-descent.ipynb cell#8）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE, GREEN, GRAY = "#4177b7", "#a14a22", "#23756c", "#8194aa"

x = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5])
eps = np.array([0.6, -0.8, 0.5, -0.4, 0.7, -0.6, 0.4, -0.5])
y = 2 * x + 1 + eps

# 复核"较优"线 MSE（手算见文件头注释）
mse_green = float(np.mean((y - (2 * x + 1)) ** 2))
print(f"复核 MSE(绿线) = {mse_green:.4f} (应为 {2.67 / 8:.4f})")

fig, ax = plt.subplots(figsize=(8.8, 5.6))
fig.subplots_adjust(left=0.07, right=0.985, top=0.90, bottom=0.10)

xs = np.array([0, 8])
ax.plot(xs, xs + 1, color=GRAY, lw=2.0, zorder=2)          # 太平：斜率太小
ax.plot(xs, 2 * xs + 1, color=GREEN, lw=2.6, zorder=2)     # 较优：贴合点云
ax.plot(xs, 3 * xs + 0.5, color=BLUE, lw=2.0, zorder=2)    # 太陡：斜率太大

ax.scatter(x, y, s=58, color=BLUE, edgecolors="white", linewidths=0.8, zorder=3)

# 线右侧留白区标注：词（粗体）+ 方程，三条线终点 y = 9 / 17 / 24.5 相距很远，不会重叠
for y_end, word, eq, c in [(9.0, "太平", "y = x + 1", GRAY),
                           (17.0, "较优", "y = 2x + 1", GREEN),
                           (24.5, "太陡", "y = 3x + 0.5", BLUE)]:
    ax.text(8.2, y_end + 0.65, word, fontsize=13.5, color=c, weight="bold", va="center")
    ax.text(8.2, y_end - 0.85, eq, fontsize=11.5, color=c, va="center")

ax.grid(True, lw=0.4, alpha=0.35)
ax.set_xlabel("x", fontsize=12)
ax.set_ylabel("y", fontsize=12)
ax.set_title("三条候选直线：哪条最好？", fontsize=13.5)
ax.set_xlim(0, 10.0)
ax.set_ylim(0, 26.5)
ax.set_xticks(range(0, 9))

out = Path(__file__).with_name("ch3-many-lines.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
