"""正则化效果图：只画Notebook已拟合的预测，不在helper中训练。"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, SymLogNorm
from course_plot_style import chinese_plot


@chinese_plot
def plot_regularization_effect(x_train, y_train, grid, predictions, table, assets_dir,
                               weights, intercepts):
    """曲线旁的小矩阵仅排列参数；灰色截距不进入惩罚或色标。"""
    fig = plt.figure(figsize=(11, 9.8))
    panels = fig.add_gridspec(3, 2, width_ratios=[4, 1.15], hspace=.92, wspace=.30)
    axes = []
    palette = LinearSegmentedColormap.from_list("coefficient_sign",
                                                ["#b66c2d", "#ffffff", "#245d8c"])
    palette.set_bad("#c8cdd3")
    bound = 10 ** np.ceil(np.log10(np.max(np.abs(weights))))
    norm = SymLogNorm(linthresh=.01, linscale=.7, vmin=-bound, vmax=bound)
    names = ["不加正则化", "加入L2惩罚", "较强L2惩罚"]
    for index, (name, (_, row)) in enumerate(zip(names, table.iterrows())):
        ax = fig.add_subplot(panels[index, 0])
        axes.append(ax)
        alpha = row["alpha"]
        ax.scatter(x_train, y_train, s=32, color="#527d99", alpha=.8,
                   label="相同训练样本", zorder=3)
        ax.plot(grid, predictions[alpha], color="#c56825", lw=2.6,
                label="拟合曲线", zorder=4)
        ax.set_title(f"{name}（α={alpha:g}）", loc="left", fontsize=22, pad=36)
        stats = f"训练/验证 MSE：{row['训练MSE']:.3f} / {row['验证MSE']:.3f}"
        ax.text(0, 1.035, stats, transform=ax.transAxes, fontsize=19, color="#405366")
        ax.set(xlim=(grid.min(), grid.max()), ylim=(-1.4, 1.5), ylabel="y")
        ax.set_yticks([-1, 0, 1])
        ax.grid(axis="y", color="#e6ebf0", linewidth=.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=17)
        ax.tick_params(labelbottom=index == 2)
        # 最后一格仅显示b的位置，不给它赋予参与惩罚的颜色。
        layout = np.append(weights[index], np.nan).reshape(4, 4)
        matrix_ax = fig.add_subplot(panels[index, 1])
        artist = matrix_ax.imshow(np.ma.masked_invalid(layout), cmap=palette,
                                  norm=norm, interpolation="nearest")
        matrix_ax.text(3, 3, f"b\n{intercepts[index]:.2f}", ha="center", va="center",
                       fontsize=11, color="#26364a")
        matrix_ax.set_title(r"$\|w\|_2^2$=" + f"{row['权重平方和']:.3g}", fontsize=17, pad=7)
        matrix_ax.set_xticks([])
        matrix_ax.set_yticks([])
        matrix_ax.set_xticks(np.arange(-.5, 4, 1), minor=True)
        matrix_ax.set_yticks(np.arange(-.5, 4, 1), minor=True)
        matrix_ax.grid(which="minor", color="white", linewidth=.7)
        matrix_ax.tick_params(which="minor", length=0)
        for spine in matrix_ax.spines.values():
            spine.set_color("#ccd5de")
    axes[0].legend(loc="lower right", fontsize=15, frameon=False, ncol=2)
    axes[-1].set_xlabel("输入 x（仅画原训练取值范围）", fontsize=17)
    fig.subplots_adjust(left=.085, right=.98, top=.90, bottom=.12)
    color_ax = fig.add_axes([.77, .045, .20, .016])
    bar = fig.colorbar(artist, cax=color_ax, orientation="horizontal", ticks=[-1000, 0, 1000])
    bar.ax.set_xticklabels(["−1000", "0", "+1000"])
    bar.ax.tick_params(labelsize=12)
    fig.text(.08, .025, "小矩阵：前15格为w，灰格b不惩罚；统一对称对数色标。", fontsize=15)
    for extension in ("png", "svg"):
        fig.savefig(assets_dir / f"l6-regularization-effect.{extension}",
                    dpi=300, bbox_inches="tight")
    return fig


@chinese_plot
def plot_l1_l2_weights(weights, intercepts, assets_dir):
    """相同坐标、相同色标展示系数，精确零单独标注。"""
    from matplotlib.colors import TwoSlopeNorm
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    palette = LinearSegmentedColormap.from_list(
        "l1_l2_sign", ["#b66c2d", "#ffffff", "#245d8c"])
    palette.set_bad("#c8cdd3")
    bound = np.max(np.abs(weights))
    for i, ax in enumerate(axes):
        layout = np.append(weights[i], np.nan).reshape(4, 4)
        artist = ax.imshow(np.ma.masked_invalid(layout), cmap=palette,
                           norm=TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound))
        for j, value in enumerate(weights[i]):
            label = "0" if value == 0 else f"{value:.2g}"
            ax.text(j % 4, j // 4, label,
                    ha="center", va="center", fontsize=11 if len(label) > 4 else 14,
                    color="white" if abs(value) > bound * .65 else "#26364a")
        ax.text(3, 3, f"b\n{intercepts[i]:.2f}", ha="center", va="center", fontsize=13)
        name = ["L1：LASSO（α=0.01）", "L2：Ridge（α=0.6）"][i]
        ax.set_title(name + f"\n精确零权重：{(weights[i] == 0).sum()} / 15", fontsize=21)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticks(np.arange(-.5, 4, 1), minor=True)
        ax.set_yticks(np.arange(-.5, 4, 1), minor=True)
        ax.grid(which="minor", color="#d8dfe5", linewidth=.8)
        ax.tick_params(which="minor", length=0)
    fig.subplots_adjust(wspace=.18, bottom=.20, top=.80)
    cax = fig.add_axes([.26, .045, .48, .018])
    fig.colorbar(artist, cax=cax, orientation="horizontal")
    for extension in ("png", "svg"):
        fig.savefig(assets_dir / f"l6-l1-l2-weights.{extension}", dpi=300, bbox_inches="tight")
    # 上方保留原几何图，下方并排放实算热力图；内嵌SVG避免外部依赖。
    import re
    import xml.etree.ElementTree as ET
    namespace = "http://www.w3.org/2000/svg"
    combined = ET.Element(f"{{{namespace}}}svg", viewBox="0 0 720 720", width="720", height="720")
    for prefix, filename, y, height in [
        ("geometry", "l6-penalty-geometry.svg", 0, 360),
        ("weights", "l6-l1-l2-weights.svg", 370, 350)]:
        source = (assets_dir / filename).read_text()
        for identifier in re.findall(r'id="([^"]+)"', source):
            source = source.replace(f'id="{identifier}"', f'id="{prefix}-{identifier}"')
            source = source.replace(f'#{identifier}"', f'#{prefix}-{identifier}"')
            source = source.replace(f'#{identifier})', f'#{prefix}-{identifier})')
        panel = ET.fromstring(source)
        panel.attrib.update(x="0", y=str(y), width="720", height=str(height))
        combined.append(panel)
    ET.ElementTree(combined).write(assets_dir / "l6-l1-l2-comparison.svg", encoding="utf-8", xml_declaration=True)
    return fig
