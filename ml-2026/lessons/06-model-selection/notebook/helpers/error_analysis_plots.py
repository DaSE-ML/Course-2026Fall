"""错误分析的展示；训练、预测与计数留在Notebook。"""
import matplotlib.pyplot as plt
import numpy as np
from course_plot_style import chinese_plot


@chinese_plot
def plot_error_changes(images, truth, before, after, assets_dir):
    old_wrong = before != truth
    new_wrong = after != truth
    groups = [old_wrong & ~new_wrong, ~old_wrong & new_wrong, old_wrong & new_wrong]
    labels = ["修正旧错", "新增错误", "仍然出错"]
    colors = ["#2F6DB0", "#D9822B", "#65758B"]
    # 每组按验证集索引顺序取第一张，避免挑最好看的图。
    fig = plt.figure(figsize=(8.5, 6.8), layout="constrained")
    grid = fig.add_gridspec(2, 3, height_ratios=[1.2, 1], hspace=.18)
    for col, (mask, label, color) in enumerate(zip(groups, labels, colors)):
        ax = fig.add_subplot(grid[0, col])
        indices = np.flatnonzero(mask)
        if indices.size:
            i = int(indices[0])
            ax.imshow(images[i].reshape(8, 8), cmap="gray_r", vmin=0, vmax=16,
                      interpolation="nearest")
            ax.set_title(f"{label}：索引{i}\n真实 {truth[i]}｜回归 {before[i]}\n近邻 {after[i]}",
                         fontsize=16, color=color, linespacing=1.4)
        ax.axis("off")
    ax = fig.add_subplot(grid[1, :])
    counts = [int(mask.sum()) for mask in groups]
    y = np.arange(3)
    ax.barh(y, counts, color=colors, height=.55)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(counts) + 1.5)
    ax.set_xticks(np.arange(max(counts) + 1))
    ax.set_xlabel("验证样本数（条）")
    for ypos, count in zip(y, counts):
        ax.text(count + .15, ypos, str(count), va="center", fontsize=18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=.15)
    ax.set_axisbelow(True)
    for suffix in ["svg", "png"]:
        fig.savefig(assets_dir / f"l6-error-analysis.{suffix}", bbox_inches="tight")
    return fig
