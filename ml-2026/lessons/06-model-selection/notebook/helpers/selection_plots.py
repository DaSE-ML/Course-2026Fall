"""第 6 讲绘图 helper；只接收 Notebook 已经算好的数组和表格。"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from course_plot_style import chinese_plot


@chinese_plot
def plot_loo_comparison(table, assets_dir: Path):
    """同一开发数据的两种折外预测协议；不把差值解释为显著收益。"""
    fig, ax = plt.subplots(figsize=(9, 2.8))
    colors = ["#356dac", "#b66c2d"]
    for index, row in table.iterrows():
        ax.barh(index, row["折外总体准确率"] * 100, color=colors[index], height=.48)
        ax.text(3, index, f'{int(row["答对数"])}/{int(row["总数"])} = {row["折外总体准确率"]:.2%}', va="center", color="white")
    ax.set(xlim=(0, 100), xticks=[0, 25, 50, 75, 100])
    ax.set_xlabel("折外总体准确率（%）")
    ax.set_yticks([0, 1], table["方法"])
    ax.invert_yaxis()
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-loo-comparison.png", bbox_inches="tight")
    # 转路径的SVG不依赖浏览器字体，投影/打印缩放也保持清晰。
    fig.savefig(assets_dir / "l6-loo-comparison.svg", bbox_inches="tight")
    return fig


@chinese_plot
def plot_opening(table, assets_dir: Path):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    numeric = table[table["C"] != "Dummy"]
    ax.plot(numeric["C"], numeric["训练准确率"], "o-", label="训练准确率", color="#1f77b4")
    ax.plot(numeric["C"], numeric["验证准确率"], "o-", label="验证准确率", color="#f28e2b")
    dummy = table[table["C"] == "Dummy"].iloc[0]
    ax.set_xscale("log")
    ax.set_ylim(.78, 1.02)
    ax.set(xlabel="C（对数轴；越大，正则化越弱）", ylabel="准确率", title="固定划分：训练与验证准确率")
    # 保留全部候选点，只标关键位置及验证最高点，避免密集标签相撞。
    label_points = {numeric.index[0], numeric.index[-1],
                    numeric["验证准确率"].idxmax()}
    label_points.update(numeric.index[numeric["C"].isin([0.01, 1, 100])])
    for index, row in numeric.iterrows():
        if index not in label_points:
            continue
        ax.annotate(f"{row['验证准确率']:.1%}", (row["C"], row["验证准确率"]),
                    xytext=(0, 8), textcoords="offset points", ha="center", fontsize=14)
    ax.text(.02, .02, f"Dummy 验证约 {dummy['验证准确率']:.1%}，不在此 y 轴范围",
            transform=ax.transAxes, fontsize=14, color="#555")
    ax.legend(fontsize=14)
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-opening-comparison.png", bbox_inches="tight")
    return fig


@chinese_plot
def plot_learning(table, assets_dir: Path, fold_valid=None):
    from matplotlib.ticker import PercentFormatter
    fig, ax = plt.subplots(figsize=(10.6, 6.5))
    sizes = table["每折训练样本数"].to_numpy()
    if fold_valid is not None:
        colors = ["#527d99", "#68896b", "#95804f", "#837299", "#985f6d"]
        markers = ["o", "s", "^", "D", "v"]
        for fold in range(fold_valid.shape[1]):
            ax.plot(sizes, fold_valid[:, fold], color=colors[fold], marker=markers[fold],
                    ms=3.5, lw=1.2, alpha=.35, label=f"验证折{fold+1}")
    ax.plot(sizes, table["训练准确率"], "s--", color="#245d8c", ms=5, lw=2.5,
            label="训练均值（5折）", zorder=5)
    ax.plot(sizes, table["CV准确率"], "o-", color="#c56825", ms=5, lw=3,
            label="验证均值（5折）", zorder=6)
    ax.set(xlabel="每折训练样本数", ylabel="准确率", title="学习曲线：固定模型与5折划分")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xticks([sizes[0], 300, 500, 700, 900, sizes[-1]])
    ax.grid(axis="y", color="#e6ebf0", linewidth=.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.20), ncol=3, fontsize=13)
    fig.tight_layout()
    for stem in ["l6-learning-curve", "l6-learning-curve-intro"]:
        fig.savefig(assets_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
        fig.savefig(assets_dir / f"{stem}.svg", bbox_inches="tight")
    return fig


@chinese_plot
def plot_selection(cv_table, assets_dir: Path):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(cv_table["C"], cv_table["训练准确率均值"], "o-", color="#1f77b4", label="训练准确率均值")
    ax.plot(cv_table["C"], cv_table["CV准确率均值"], "o-", color="#f28e2b", label="CV验证准确率均值")
    ax.set_xscale("log")
    ax.set(xlabel="C（对数轴）", ylabel="准确率", title="开发集五折：候选 C 的训练与验证分数")
    ax.legend(fontsize=14)
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-selection-c.png", bbox_inches="tight")
    return fig


@chinese_plot
def plot_leakage(leakage_table, assets_dir: Path):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(leakage_table["流程"], leakage_table["验证准确率"], color=["#e15759", "#59a14f", "#4e79a7"])
    ax.set(ylim=(0, 1.05), ylabel="验证准确率", title="随机标签：全体选列与 Pipeline")
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-leakage-comparison.png", bbox_inches="tight")
    return fig


@chinese_plot
def plot_bootstrap_complexity(grid, x_train, y_train, predictions, references, assets_dir: Path):
    """仅画Notebook实算结果；保留完整范围图，不隐藏极端预测。"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
    for ax, degree in zip(axes, sorted(predictions)):
        ax.plot(grid, predictions[degree].T, color="#4e79a7", alpha=.16, lw=.8)
        ax.plot([], [], color="#4e79a7", label="40次Bootstrap拟合")
        ax.plot(grid, references[degree], color="#e28728", lw=2, label="原训练集拟合")
        ax.scatter(x_train, y_train, s=15, color="#535c68", zorder=3, label="原训练记录")
        ax.set(title=f"多项式阶数 {degree}", xlabel="x", ylim=(-2, 2), xlim=(-1, 1))
    axes[0].set_ylabel("预测值 / 观测值")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=14)
    fig.tight_layout(rect=(0, .12, 1, 1))
    fig.savefig(assets_dir / "l6-complexity-bootstrap.png", bbox_inches="tight")

    full, full_axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
    for ax, degree in zip(full_axes, sorted(predictions)):
        ax.plot(grid, predictions[degree].T, color="#4e79a7", alpha=.16, lw=.8)
        ax.plot(grid, references[degree], color="#e28728", lw=2)
        ax.scatter(x_train, y_train, s=15, color="#535c68", zorder=3)
        ax.set(title=f"多项式阶数 {degree}", xlabel="x", xlim=(-1, 1), yscale="symlog")
    full_axes[0].set_ylabel("预测值 / 观测值（symlog）")
    full.suptitle("Bootstrap拟合完整范围：symlog压缩极端值，不裁掉数据")
    full.tight_layout()
    full.savefig(assets_dir / "l6-complexity-bootstrap-full.png", bbox_inches="tight")
    return fig, full


@chinese_plot
def plot_complexity(x_grid, true_curve, components, assets_dir: Path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    for ax, degree in zip(axes, sorted(components)):
        predictions = components[degree]["predictions"]
        for prediction in predictions:
            ax.plot(x_grid, prediction, color="#4e79a7", alpha=.12, linewidth=.8)
        ax.plot(x_grid, true_curve, color="#222", linewidth=2, label="真实函数")
        ax.plot(x_grid, components[degree]["mean_prediction"], color="#f28e2b", linewidth=2, label="40次平均预测")
        ax.set_title(f"多项式阶数 {degree}")
        ax.set_xlabel("x（内部比较区间 [-0.9, 0.9]）")
        ax.set_ylim(-2, 2)
    axes[0].set_ylabel("y")
    axes[-1].legend(fontsize=14, loc="lower left")
    fig.suptitle("40次重新抽样拟合：主图纵轴仅显示 -2 至 2，完整范围见附录")
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-complexity-fits.png", bbox_inches="tight")
    full_fig, full_axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    for ax, degree in zip(full_axes, sorted(components)):
        predictions = components[degree]["predictions"]
        for prediction in predictions:
            ax.plot(x_grid, prediction, color="#4e79a7", alpha=.12, linewidth=.8)
        ax.plot(x_grid, true_curve, color="#222", linewidth=2)
        ax.plot(x_grid, components[degree]["mean_prediction"], color="#f28e2b", linewidth=2)
        ax.set_title(f"多项式阶数 {degree}")
        ax.set_xlabel("x")
        ax.set_yscale("symlog", linthresh=1)
    full_axes[0].set_ylabel("y（symlog）")
    full_fig.suptitle("附录：symlog 轴保留 degree15 的完整极端范围")
    full_fig.tight_layout()
    full_fig.savefig(assets_dir / "l6-complexity-fits-full.png", bbox_inches="tight")
    plt.close(full_fig)
    return fig


@chinese_plot
def plot_decomposition(table, assets_dir: Path):
    fig, ax = plt.subplots(figsize=(8.5, 5))
    table.set_index("阶数")[["平均偏差²", "平均方差", "噪声方差"]].plot.bar(
        ax=ax, color=["#59a14f", "#4e79a7", "#bab0ab"]
    )
    ax.set_yscale("symlog", linthresh=.1)
    ax.set(xlabel="多项式阶数", ylabel="固定网格上的平均贡献（symlog）",
           title="教学模拟：symlog 只压缩极端值，精确数值见分量表")
    ax.legend(title="分解项", fontsize=14, title_fontsize=14)
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-bias-variance-components.png", bbox_inches="tight")
    return fig


@chinese_plot
def plot_bootstrap_decomposition(table, assets_dir: Path):
    """分解固定留出标签下的实际误差，不将第一项命名为理论偏差平方。"""
    fig, ax = plt.subplots(figsize=(10.2, 6.3))
    fields = ["平均留出MSE", "平均预测的留出MSE", "预测方差"]
    colors = ["#667788", "#23756c", "#b66c25"]
    positions = np.arange(len(table))
    for j, (field, color) in enumerate(zip(fields, colors)):
        bars = ax.bar(positions + (j-1)*.24, table[field], width=.22,
                      label=field, color=color)
        ax.bar_label(bars, labels=[f"{value:.4g}" for value in table[field]],
                     fontsize=12, padding=4)
    ax.set_xticks(positions, [f"{int(d)}阶" for d in table["阶数"]])
    ax.set_yscale("symlog", linthresh=.1)
    ax.set_ylim(0, table[fields].to_numpy().max()*5)
    ax.set(xlabel="多项式阶数", ylabel="均方误差（对称对数刻度）",
           title="同一批模型：平均留出MSE＝平均预测的留出MSE＋预测方差")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e6ebf0", lw=.8)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.17), ncol=2, fontsize=13)
    fig.tight_layout()
    for ext in ["png", "svg"]:
        fig.savefig(assets_dir / f"l6-bootstrap-decomposition.{ext}", dpi=300, bbox_inches="tight")
    return fig


@chinese_plot
def render_holdout_decomposition_formula(assets_dir: Path):
    fig = plt.figure(figsize=(8, .95))
    fig.text(.5, .5, r"$\overline{\mathrm{MSE}}=\mathrm{MSE}(\bar f)+V$",
             ha="center", va="center", fontsize=31, color="#255d9b")
    for ext in ["png", "svg"]:
        fig.savefig(assets_dir / f"l6-holdout-decomposition-formula.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
