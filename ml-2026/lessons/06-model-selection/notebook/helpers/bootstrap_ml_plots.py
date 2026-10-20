"""Bootstrap的模型训练图；抽样、拟合和数值计算均留在Notebook。"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.ticker import PercentFormatter
from course_plot_style import chinese_plot

BLUE, ORANGE, INK = "#356dac", "#af6b26", "#26364a"


def _save(fig, assets_dir, stem):
    fig.savefig(assets_dir / f"{stem}.svg", bbox_inches="tight", dpi=300)
    fig.savefig(assets_dir / f"{stem}.png", bbox_inches="tight", dpi=300)


@chinese_plot
def plot_ml_draws(draws, assets_dir):
    """每列是同一条原训练记录，颜色深浅表示本轮被抽到几次。"""
    n = draws.shape[1]
    counts = np.vstack([np.ones(n, dtype=int)] + [
        np.bincount(row, minlength=n) for row in draws[:3]
    ])
    fig, ax = plt.subplots(figsize=(12, 6.5))
    fig.subplots_adjust(left=.12, right=.74, bottom=.25, top=.85)
    vmax = int(counts.max())
    cmap = ListedColormap(["#f1f3f5", "#b8d2eb", "#6e9dca", "#356dac", "#20496f", "#112d47"][:vmax+1])
    ax.imshow(counts, aspect="auto", cmap=cmap,
              norm=BoundaryNorm(np.arange(vmax+2)-.5, cmap.N))
    ax.set_yticks(range(4), ["原训练集", "重抽1", "重抽2", "重抽3"], fontsize=18)
    ax.set_xticks([0, 9, 19, 29, 39, 49, 59, 69], [1, 10, 20, 30, 40, 50, 60, 70])
    ax.set_xlabel("原训练记录编号（每列始终对应同一条记录）", fontsize=17, labelpad=12)
    ax.set_xticks(np.arange(-.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 4, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=.8)
    ax.tick_params(which="minor", length=0)
    ax.spines[:].set_visible(False)
    for row in range(4):
        unique = int(np.count_nonzero(counts[row]))
        text = f"70条 / {unique}朵不同花" if row else "70条 / 70朵不同花"
        ax.text(n+1, row-.16, text, fontsize=16, va="center", color=INK)
        if row:
            ax.text(n+1, row+.22, f"→ 重新拟合模型{row}", fontsize=17, va="center", color=BLUE)
    fig.suptitle("每次都从原训练集中抽70次，再训练一个模型", fontsize=23, color=INK, y=.97)
    fig.text(.12, .10, "浅灰：未抽到（0次）    浅蓝：1次    深蓝：重复抽到（≥2次）", fontsize=17, color=INK)
    _save(fig, assets_dir, "l6-bootstrap-ml-draws")
    return fig


@chinese_plot
def plot_ml_predictions(X, y, grid, curves, probe, predictions, reference, assets_dir):
    fig, axes = plt.subplots(2, 1, figsize=(11.4, 9), gridspec_kw={"height_ratios": [1.3, 1]})
    ax = axes[0]
    for curve in curves[:30]:
        ax.plot(grid[:, 0], curve, color=BLUE, alpha=.19, lw=1.2)
    ax.plot(grid[:, 0], reference, color=INK, ls="--", lw=2, label="原70条训练的模型")
    for value, color, marker, label in [(0, BLUE, "o", "Iris versicolor（0）"), (1, ORANGE, "^", "Iris virginica（1）")]:
        ax.scatter(X[y == value, 0], y[y == value], color=color, marker=marker, s=23, alpha=.65, label=label)
    probe_color = "#7B3FA0"
    ax.axvline(probe, color=probe_color, ls=":", lw=1.6)
    ax.scatter(np.full(30, probe), predictions[:30], s=24, color=probe_color,
               edgecolors="white", linewidths=.35, zorder=5, label=f"{probe:.1f} cm处各模型预测")
    ax.axhline(.5, color="#64748b", ls="-.", lw=1.3, zorder=2)
    ax.annotate("p = 0.5（50%）", xy=(.99, .5), xycoords=("axes fraction", "data"),
                xytext=(0, 5), textcoords="offset points", ha="right", va="bottom",
                fontsize=12, color="#516173", bbox={"facecolor":"white", "edgecolor":"none", "alpha":.85, "pad":1.5})
    ax.set(xlabel="花瓣长度（cm）", ylabel="预测为类别1的概率", ylim=(-.08, 1.08))
    ax.set_title("同一训练规则，换一份重抽训练集，拟合曲线也会变化", fontsize=20, loc="left", pad=15)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(fontsize=12, loc="upper left")
    ax = axes[1]
    ax.hist(predictions, bins=18, color=BLUE, edgecolor="white")
    ax.axvline(np.mean(predictions), color=ORANGE, ls="--", lw=2)
    ax.set(xlabel="预测为类别1的概率", ylabel="模型数")
    ax.set_title(f"固定输入：花瓣长度{probe:.1f} cm；{len(predictions)}个模型的预测", fontsize=20, loc="left", pad=15)
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.text(.98, .92, f"均值 {np.mean(predictions):.1%}\n预测波动（标准差）\n{np.std(predictions, ddof=1)*100:.2f}个百分点",
            transform=ax.transAxes, ha="right", va="top", fontsize=16, color=INK)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#e6ebf0", linewidth=.7)
    fig.tight_layout(h_pad=2.5)
    _save(fig, assets_dir, "l6-bootstrap-ml-predictions")
    return fig


@chinese_plot
def plot_ml_oob(draw, assets_dir):
    n = len(draw)
    counts = np.bincount(draw, minlength=n)
    inside = np.count_nonzero(counts)
    outside = n - inside
    fig, ax = plt.subplots(figsize=(11, 6.4))
    ax.axis("off")
    ax.set(xlim=(0, 10), ylim=(0, 6))
    ax.text(5, 5.7, "同一次重抽：训练记录与袋外记录分开", ha="center", fontsize=24, color=INK)
    for i, count in enumerate(counts):
        x, y = .55 + (i % 14)*.64, 4.75 - (i // 14)*.48
        ax.text(x, y, str(i+1), ha="center", va="center", fontsize=13,
                bbox={"boxstyle": "square,pad=.25", "facecolor": "#dbe8f5" if count else "#fff4e5",
                      "edgecolor": BLUE if count else ORANGE})
    ax.text(5, 2.25, "编号沿用原70条训练记录；蓝色被抽到，橙色未抽到", ha="center", fontsize=16, color=INK)
    for x, label, color in [(2.5, f"袋内：{inside}朵不同花\n重复计入后70条 → 拟合模型", BLUE),
                             (7.5, f"袋外：{outside}朵花\n不拟合 → 评价本轮模型", ORANGE)]:
        ax.text(x, 1.25, label, ha="center", va="center", fontsize=20, color=color)
    ax.text(5, .25, "另留出的30条评价记录不参与重抽；本图仅用第1轮的实际抽样结果", ha="center", fontsize=16, color=INK)
    _save(fig, assets_dir, "l6-bootstrap-ml-oob")
    return fig
