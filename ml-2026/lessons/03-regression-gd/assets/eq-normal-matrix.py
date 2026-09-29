# 第 3 讲公式图：正规方程（矩阵形式）+ 维度标注
# 数值验证：用两个教学点 (1,3)、(3,7) 代入正规方程，应解得 w* = [1, 2]
# （即直线 y = 2x + 1 恰好穿过两点，与 ch3-normal-eq.py 同一教学数据）
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["mathtext.fontset"] = "cm"
# 中文字体：macOS PingFang SC + 回退链（照抄 ch3-normal-eq.py）
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE = "#174b87"   # 与课件 .equation 同色
GRAY = "#5a5a5a"

# ---- 数值验证：正规方程在两点数据上解出 y = 2x + 1 ----
X = np.array([[1.0, 1.0],
              [1.0, 3.0]])   # 设计矩阵，列 = [截距, x]
y = np.array([3.0, 7.0])
w_star = np.linalg.inv(X.T @ X) @ X.T @ y
assert np.allclose(w_star, [1.0, 2.0], atol=1e-10), f"正规方程解异常: {w_star}"
print("数值验证通过: w* =", w_star, "（直线 y = 2x + 1 过点 (1,3) 与 (3,7)）")

tex_main = r"$\mathbf{w}^{*} = \left(\mathbf{X}^{T}\mathbf{X}\right)^{-1}\mathbf{X}^{T}\mathbf{y}$"

fig = plt.figure(figsize=(12, 1.8))
# 主公式（大号，居中偏上）
fig.text(0.5, 0.60, tex_main, ha="center", va="center", fontsize=40, color=BLUE)
# 下方维度标注行（小号灰色，普通文本 + 少量 mathtext）
fig.text(0.5, 0.20,
         r"$X$: n×d（n 个样本、d 个特征）　　$y$: n　　$w$: d",
         ha="center", va="center", fontsize=15, color=GRAY)

out = Path(__file__).with_name("eq-normal-matrix.png")
fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.15)
print("saved:", out)
