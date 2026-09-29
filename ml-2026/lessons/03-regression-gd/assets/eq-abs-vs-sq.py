# 第 3 讲公式图：为什么用平方，不用绝对值？（课程风格重绘，白底）
# 页面标题由课件 h1 承担，图内不再重复标题行。
# 残差方向全章统一为预测减真实：r = ŷ − y（与第 5 页 MSE 公式、第 11 页梯度一致）。
# 数值验证：在 x = 0 处用差商对比 |x| 与 x² 的可导性
#   |x| 左差商 = −1，右差商 = +1  -> 左右不等，不可导
#   x²  左差商 = 0，右差商 = 0    -> 相等，处处可导
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["mathtext.fontset"] = "cm"
# 中文字体：macOS PingFang SC + 回退链（照抄 ch3-normal-eq.py）
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE = "#174b87"    # 与课件 .equation 同色
ORANGE = "#a14a22"  # 辅橙
GRAY = "#6b6b6b"
GREEN = "#2e7d32"

# ---- 数值验证：|x| 在 0 处不可导，x² 在 0 处可导 ----
# 单侧差商（步长 h）：左 = (f(0) − f(−h))/h，右 = (f(h) − f(0))/h
# 左右差商之差 jump：|x| 恒为 2（不随 h 消失 -> 不可导）；x² = 2h（随 h→0 消失 -> 可导）
h = 1e-6
left_abs = (abs(0.0) - abs(-h)) / h        # -> -1
right_abs = (abs(h) - abs(0.0)) / h        # -> +1
jump_abs = right_abs - left_abs
left_sq = (0.0 - (-h) ** 2) / h            # -> -h
right_sq = (h ** 2 - 0.0) / h              # -> +h
jump_sq = right_sq - left_sq
assert abs(left_abs + 1) < 1e-9 and abs(right_abs - 1) < 1e-9
assert abs(jump_abs - 2.0) < 1e-9 and abs(jump_sq - 2 * h) < 1e-12
assert jump_sq < 1e-5 < jump_abs
print(f"数值验证通过: |x| 在 0 处左右差商 {left_abs} / {right_abs}，差 {jump_abs}（不可导）；"
      f"x² 左右差商 {left_sq} / {right_sq}，差仅 {jump_sq}（随 h→0 消失，可导）")

fig = plt.figure(figsize=(11, 4.2))
# 顶部公式（橙色强调，大号）
fig.text(0.5, 0.82, r"$\sum_{i=1}^{n}\left|r_i\right|$", ha="center", va="center",
         fontsize=36, color=ORANGE)
# 公式配文
fig.text(0.5, 0.58, "绝对值同样能消除正负号", ha="center", va="center",
         fontsize=18, color=BLUE)
# 残差小注
fig.text(0.5, 0.42, r"其中 $r_i = \hat{y}_i - y_i$ 为第 $i$ 个样本的残差",
         ha="center", va="center", fontsize=13, color=GRAY)
# 下部两行对比：灰（不可导）→ 绿（可导）
fig.text(0.5, 0.23, r"但 $|x|$ 在 $x=0$ 处不可导，无法用微积分求极值",
         ha="center", va="center", fontsize=17, color=GRAY)
fig.text(0.5, 0.07, r"$x^2$ 处处光滑可导 $\rightarrow$ 后续可用梯度下降 / 求导法",
         ha="center", va="center", fontsize=17, color=GREEN, weight="bold")

out = Path(__file__).with_name("eq-abs-vs-sq.png")
fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.18)
print("saved:", out)
