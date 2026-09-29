# 第 3 讲公式图：线性回归损失对 w、b 的偏导数（单特征版）
# 数值验证：数据 (1,3)、(3,7)，在 w=1, b=1 处
#   ŷ = [2, 4]，残差 ŷ−y = [−1, −3]
#   ∂L/∂w = (2/n)·[(−1)·1 + (−3)·3] = −10
#   ∂L/∂b = (2/n)·(−1 + −3)        = −4
# 解析偏导与有限差分相互印证。
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

# ---- 数值验证：解析偏导 vs 有限差分 ----
xs = np.array([1.0, 3.0])
ys = np.array([3.0, 7.0])
w0, b0 = 1.0, 1.0


def loss(w, b):
    return np.mean((w * xs + b - ys) ** 2)


h = 1e-6
num_dw = (loss(w0 + h, b0) - loss(w0 - h, b0)) / (2 * h)
num_db = (loss(w0, b0 + h) - loss(w0, b0 - h)) / (2 * h)
ana_dw = 2 / len(xs) * np.sum(((w0 * xs + b0) - ys) * xs)
ana_db = 2 / len(xs) * np.sum((w0 * xs + b0) - ys)
assert abs(num_dw - ana_dw) < 1e-4, (num_dw, ana_dw)
assert abs(num_db - ana_db) < 1e-4, (num_db, ana_db)
assert abs(ana_dw - (-10.0)) < 1e-9 and abs(ana_db - (-4.0)) < 1e-9, (ana_dw, ana_db)
print(f"数值验证通过: ∂L/∂w = {ana_dw}，∂L/∂b = {ana_db}（与有限差分一致）")

tex = (r"$\frac{\partial L}{\partial w} = \frac{2}{n}\sum_{i=1}^{n}(\hat{y}_i - y_i)\,x_i"
       r"\qquad"
       r"\frac{\partial L}{\partial b} = \frac{2}{n}\sum_{i=1}^{n}(\hat{y}_i - y_i)$")

fig = plt.figure(figsize=(13, 2.8))
# 两行主体并排为一行（用 \qquad 分隔），大号居中
fig.text(0.5, 0.62, tex, ha="center", va="center", fontsize=34, color=BLUE)
# 下方标注行（小号灰色）
fig.text(0.5, 0.16,
         r"$\hat{y}_i = w x_i + b$；偏导数为 0 的 $(w,\,b)$ 就是损失最低点",
         ha="center", va="center", fontsize=15, color=GRAY)

out = Path(__file__).with_name("eq-grad-wb.png")
fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.15)
print("saved:", out)
