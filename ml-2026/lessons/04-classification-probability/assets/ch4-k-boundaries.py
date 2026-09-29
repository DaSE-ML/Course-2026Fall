# 第 4 讲配图：k 的三档 kNN 决策边界（k=1 / k=3 / k=15，moons 数据，三面板）
# 数据与划分逐项照抄 04-classification-probability.ipynb cell 31：
#   make_moons(noise=0.3, random_state=0)
#   train_test_split(X_small, y_small, test_size=0.4, random_state=42)  → 训练 60 / 测试 40
# 画法照抄 cell 34：DecisionBoundaryDisplay(predict, alpha=0.25, cmap="RdBu")，
#   训练点深色（edgecolors="k"）、测试点浅色（alpha=0.5）。
# k=3 档复算值 0.975 与 cell 31 输出同值（脚本内 assert）；k=1、k=15 为同一划分下的复算值。
from pathlib import Path

import matplotlib.pyplot as plt
from sklearn.datasets import make_moons
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# 中文字体（照抄第 3 讲 assets 脚本字体链）：macOS PingFang SC + 回退链
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                                   "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

INK = "#333333"

# ---- 数据：与 notebook cell 31 完全同参 ----
X_small, y_small = make_moons(noise=0.3, random_state=0)
a, b, c, d = train_test_split(X_small, y_small, test_size=0.4, random_state=42)

K_LIST = (1, 3, 15)
scores, train_scores = {}, {}
for k in K_LIST:

    model = make_pipeline(StandardScaler(), KNeighborsClassifier(k)).fit(a, c)
    scores[k] = model.score(b, d)
    train_scores[k] = model.score(a, c)
assert abs(scores[3] - 0.975) < 1e-9, f"k=3 应为 0.975（notebook cell 31 同值），实得 {scores[3]}"
assert abs(train_scores[3] - 0.967) < 5e-4, f"k=3 训练分应为 0.967，实得 {train_scores[3]}"
assert abs(train_scores[1] - 1.0) < 1e-9, f"k=1 训练分应为 1.000，实得 {train_scores[1]}"
print("k=1/3/15 测试准确率:", {k: round(v, 3) for k, v in scores.items()})
print("k=1/3/15 训练准确率:", {k: round(v, 3) for k, v in train_scores.items()})

_k7 = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=7))
_k7.fit(a, c)
_k7_train, _k7_test = _k7.score(a, c), _k7.score(b, d)
assert abs(_k7_test - 0.950) < 1e-9, f"k=7 测试分应为 0.950，实得 {_k7_test}"
print("k=7（练习锚定）训练/测试:", round(_k7_train, 3), round(_k7_test, 3))
# k=7 档：第 22 页课堂练习②与作业 2 的先猜再跑锚定（不入图）
k7_model = None

fig, axes = plt.subplots(3, 1, figsize=(7.2, 9.6))
fig.suptitle("k 的三档：kNN 决策边界（moons，训练 60 / 测试 40）",
             fontsize=15, weight="bold", color=INK, y=1.04)

for ax, k in zip(axes.flat, K_LIST):
    model = make_pipeline(StandardScaler(), KNeighborsClassifier(k)).fit(a, c)
    DecisionBoundaryDisplay.from_estimator(
        model, X_small, ax=ax, response_method="predict", alpha=0.25, cmap="RdBu")
    ax.scatter(a[:, 0], a[:, 1], c=c, cmap="RdBu", s=22, edgecolors="k")
    ax.scatter(b[:, 0], b[:, 1], c=d, cmap="RdBu", s=22, edgecolors="k", alpha=0.5)
    ax.set_title(f"k={k}（测试 {scores[k]:.3f}）", fontsize=13, color=INK)
    ax.set_xlabel("feature 1")
    ax.set_ylabel("feature 2")

fig.tight_layout()
out = Path(__file__).with_name("ch4-k-boundaries.png")
fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight")
print("saved:", out)
