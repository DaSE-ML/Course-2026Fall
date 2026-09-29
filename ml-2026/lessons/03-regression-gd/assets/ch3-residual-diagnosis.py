# 第 3 讲配图：残差诊断双面板（用于"残差诊断"页）
# 数据与 03-regression-gd.ipynb cell 2 完全一致：
#   np.random.seed(0), n=30, X = sort(rand(30)), y = cos(1.5πX) + randn(30)*0.1
# 左面板：1 阶 LinearRegression 直接拟合 → 残差（ŷ−y，第 5 页口径：预测减真实）对 x 呈倒 U 弯弧（欠拟合信号）
# 右面板：Pipeline(PolynomialFeatures(degree=4) + LinearRegression) → 残差随机散布、无模式
# 两面板纵轴同尺度（sharey），灰色虚线为残差 = 0 参考线；左面板橙色折线为分箱均值（突出模式）
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

# 中文字体（照抄 ch3-fit-scatter.py）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE, GRAY = "#4177b7", "#a14a22", "#8194aa"

# ---- 数据：与 notebook cell 2 完全相同的三行 ----
np.random.seed(0)
X = np.sort(np.random.rand(30))
y = np.cos(1.5 * np.pi * X) + np.random.randn(30) * 0.1

models = {
    1: LinearRegression(),
    4: Pipeline([("poly", PolynomialFeatures(degree=4, include_bias=False)),
                 ("lin", LinearRegression())]),
}

fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.3), sharey=True)
fig.subplots_adjust(left=0.075, right=0.985, top=0.90, bottom=0.135, wspace=0.07)

for ax, (deg, model) in zip(axes, models.items()):
    pred = model.fit(X[:, None], y).predict(X[:, None])
    resid = pred - y                                # 残差 = 预测 − 真实（第 5 页口径）
    ax.axhline(0, color=GRAY, lw=1.2, ls="--", zorder=1)
    ax.scatter(X, resid, s=42, color=BLUE, alpha=0.85,
               edgecolors="white", linewidths=0.6, zorder=3)
    ax.set_xlabel("x（训练样本）", fontsize=12)
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-1.15, 0.85)
    ax.grid(True, lw=0.4, alpha=0.35)
    if deg == 1:
        # 分 6 箱画均值折线，突出"倒 U"系统模式
        bins = np.linspace(0.0, 1.0, 7)
        mids, means = [], []
        for a, b in zip(bins[:-1], bins[1:]):
            m = (X >= a) & (X < b)
            if m.sum():
                mids.append(0.5 * (a + b))
                means.append(resid[m].mean())
        ax.plot(mids, means, color=ORANGE, lw=2.2, zorder=2)
        ax.text(0.03, 0.66, "橙色折线：分箱均值", fontsize=10.5, color=ORANGE)
        ax.set_title("1 阶（直线）：残差连成倒 U 弯弧", fontsize=13)
    else:
        ax.set_title("4 阶（多项式）：残差随机散布、无模式", fontsize=13)

axes[0].set_ylabel("残差 " + r"$\hat{y}-y$" + "（预测减真实）", fontsize=12)

out = Path(__file__).with_name("ch3-residual-diagnosis.png")
fig.savefig(out, dpi=200, facecolor="white")
print("saved:", out)
