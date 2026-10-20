"""Lesson06 added figures; training and candidate evaluation remain in the notebook."""
import matplotlib.pyplot as plt
import numpy as np
from course_plot_style import chinese_plot


@chinese_plot
def search_budget_plot(grid, random, assets_dir):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5), sharex=True, sharey=True)
    low = min(grid.mean_test_score.min(), random.mean_test_score.min())
    high = max(grid.mean_test_score.max(), random.mean_test_score.max())
    for ax, table, title in zip(axes, [grid, random], ["网格：3个C × 3档列数", "随机：9个实际采样组合"]):
        dots = ax.scatter(table.param_logistic__C.astype(float),
                          table.param_select__k.astype(int), c=table.mean_test_score,
                          cmap="viridis", vmin=low, vmax=high, s=160, edgecolors="white")
        ax.set_xscale("log")
        ax.set(xlim=(.008, 1.25), xticks=[.01, .1, 1], ylim=(10, 54),
               yticks=[16, 32, 48], xlabel="C（对数尺度；本次范围 0.01–1）", title=title)
        ax.grid(alpha=.15)
    axes[0].set_ylabel("每折保留特征数 k")
    fig.colorbar(dots, ax=axes, label="相同三折的平均验证准确率", shrink=.8)
    fig.suptitle("C 范围 0.01–1；相同候选数、相同折：每种策略9×3＝27次拟合；refit=False", y=1.06)
    fig.savefig(assets_dir / "l6-search-budget.png", bbox_inches="tight")
    return fig


@chinese_plot
def early_stopping_plot(table, best_epoch, assets_dir):
    fig, ax = plt.subplots(figsize=(8, 4.7))
    ax.plot(table.epoch, table.train_loss, label="训练 Log Loss", color="#2F6DB0")
    ax.plot(table.epoch, table.valid_loss, label="验证 Log Loss", color="#D9822B")
    row = table.loc[table.epoch == best_epoch].iloc[0]
    ax.axvline(best_epoch, ls=":", color="#666")
    ax.scatter([best_epoch], [row.valid_loss], facecolor="white", edgecolor="#D9822B", zorder=4, s=75)
    ax.annotate(f"候选轮次中最低：第{best_epoch}轮", (best_epoch, row.valid_loss),
                xytext=(12, 30), textcoords="offset points", fontsize=13)
    ax.set(xlabel="训练轮次 Epoch", ylabel="Log Loss（越小越好）", title="训练多久，也要由验证结果决定")
    ax.legend()
    ax.grid(alpha=.15)
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-early-stopping.png", bbox_inches="tight")
    return fig


@chinese_plot
def augmentation_plot(images, labels, assets_dir):
    fig, axes = plt.subplots(2, 3, figsize=(9, 4.7))
    for row, (image, label) in enumerate(zip(images, labels)):
        shifted = np.zeros_like(image)
        shifted[:, 1:] = image[:, :-1]
        for ax, pic, title in zip(axes[row], [image, shifted, np.rot90(image, 2)],
                                   [f"原图：数字{label}", "向右平移1像素", "旋转180°，标签可能改变"]):
            ax.imshow(pic, cmap="gray_r", vmin=0, vmax=16)
            ax.set_title(title, fontsize=13)
            ax.axis("off")
    fig.suptitle("digits训练图片的确定性变换：增强需要标签保持假设", fontsize=16)
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-augmentation.png", bbox_inches="tight")
    return fig


@chinese_plot
def validation_curve_plot(table, assets_dir):
    """Plot the C validation curve from scores computed in the notebook."""
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.errorbar(table["C"], table["训练准确率均值"],
                yerr=table["训练准确率标准差"], marker="o", capsize=4,
                label="训练准确率", color="#2F6DB0")
    ax.errorbar(table["C"], table["验证准确率均值"],
                yerr=table["验证准确率标准差"], marker="o", capsize=4,
                label="验证准确率", color="#D9822B")
    ax.set_xscale("log")
    ax.set(xlabel="C（对数尺度；越大，正则化越弱）", ylabel="准确率",
           title="验证曲线：只改变 C，协议固定")
    ax.grid(alpha=.15)
    ax.legend()
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-validation-curve.png", bbox_inches="tight")
    return fig


@chinese_plot
def penalty_comparison_plot(table, assets_dir):
    """Plot same-CV L1/L2 comparison; the notebook owns the fit and table."""
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    x = np.arange(len(table))
    colors = ["#6B8E23", "#4E79A7"]
    ax.errorbar(x, table["验证准确率均值"], yerr=table["验证准确率标准差"],
                fmt="o", markersize=10, capsize=6, linewidth=2,
                color="#333333", ecolor="#333333", zorder=3)
    for xpos, value, color, label in zip(x, table["验证准确率均值"], colors, table["惩罚"]):
        ax.scatter([xpos], [value], s=130, color=color, edgecolor="white", zorder=4, label=label)
        ax.text(xpos, value + 0.0017, f"{value:.3f}", ha="center", fontsize=13)
    ax.set_ylim(0.94, 0.985)
    ax.set_xticks(x, table["惩罚"])
    ax.set(xlabel="惩罚项（同一分层五折）", ylabel="验证准确率",
           title="L1 与 L2：同协议对照（点为均值，误差棒为五折标准差，非置信区间）")
    ax.grid(axis="y", alpha=.15)
    ax.legend(title="惩罚项", frameon=False)
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-penalty-comparison.png", bbox_inches="tight")
    return fig


@chinese_plot
def error_examples_plot(images, rows, assets_dir):
    """Show up to six validation errors selected by the Notebook."""
    fig, axes = plt.subplots(2, 3, figsize=(8.5, 5.8))
    for ax in axes.flat:
        ax.axis("off")
    for ax, image, row in zip(axes.flat, images, rows.itertuples(index=False)):
        ax.imshow(image, cmap="gray_r", vmin=0, vmax=16)
        ax.set_title(f"索引 {row.索引}：真值 {row.真实} / 预测 {row.预测}", fontsize=13)
        ax.axis("off")
    fig.suptitle("验证集错例：先看模型错在哪里", fontsize=16)
    fig.tight_layout()
    fig.savefig(assets_dir / "l6-errors.png", bbox_inches="tight")
    return fig
