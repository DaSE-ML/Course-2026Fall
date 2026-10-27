"""固定划分实验：上方准确率，下方每个C对应的完整权重竖带。"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
from course_plot_style import chinese_plot


@chinese_plot
def plot_opening_weights(table, weights, assets_dir):
    """接收已拟合权重，不训练、不按列重新归一化。"""
    rows = table[table["C"] != "Dummy"]
    values = rows["C"].to_numpy(dtype=float)
    assert weights.shape == (len(values), 10, 64)  # 每个C有10类、每类64个系数。
    strips = weights.reshape(len(values), -1).T
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(8.5, 7.5), sharex=True,
                                      gridspec_kw={"height_ratios": [1, 1.1], "hspace": .30})
    for column, color in [("训练准确率", "#267eb7"), ("验证准确率", "#ed8b2c")]:
        top.plot(values, rows[column], marker="o", lw=2, color=color, label=column)
    best = rows.loc[rows["验证准确率"].idxmax()]
    top.annotate(f"C={best['C']:g}：{best['验证准确率']:.1%}",
                 xy=(best["C"], best["验证准确率"]), xytext=(0, -27),
                 textcoords="offset points", ha="center", fontsize=14)
    top.set(ylim=(.79, 1.015), ylabel="准确率")
    top.set_title("固定划分：准确率与权重随C的变化", fontsize=20, pad=12)
    top.grid(alpha=.15)
    top.legend(loc="lower right", fontsize=13)
    edges = 10.0 ** np.arange(-4.5, 5, 1)
    bound = float(np.max(np.abs(strips)))
    artist = bottom.pcolormesh(edges, np.arange(641), strips, shading="flat",
                              cmap="RdBu_r", norm=SymLogNorm(linthresh=.001, linscale=.5,
                                                            vmin=-bound, vmax=bound),
                              rasterized=True)
    bottom.set_xscale("log")
    bottom.set_xlim(edges[0], edges[-1])
    bottom.set_ylim(640, 0)
    bottom.set_xticks(values, [rf"$10^{{{int(np.log10(c))}}}$" for c in values])
    bottom.set_yticks(np.arange(10) * 64 + 32, [str(c) for c in range(10)])
    bottom.set_ylabel("类别（每类64个权重）", fontsize=15)
    bottom.set_xlabel("C增大 → 正则化减弱（对数轴）", fontsize=16)
    bottom.set_title("每列一个C：10×64个标准化特征权重", fontsize=16, pad=9)
    for y in np.arange(0, 641, 64):
        bottom.axhline(y, color="#888888", lw=.35, alpha=.5)
    fig.subplots_adjust(left=.13, right=.97, top=.92, bottom=.23)
    color_ax = fig.add_axes([.35, .08, .39, .015])
    colorbar = fig.colorbar(artist, cax=color_ax, orientation="horizontal")
    colorbar.set_ticks([-bound, -.01, 0, .01, bound],
                       labels=[f"−{bound:.1f}", "−0.01", "0", "0.01", f"{bound:.1f}"])
    colorbar.ax.tick_params(labelsize=11)
    fig.text(.13, .015, "统一对称对数色标：蓝负、红正、白色近0；不含截距。", fontsize=12)
    for extension in ("svg", "png"):
        fig.savefig(assets_dir / f"l6-opening-with-weights.{extension}", dpi=300, bbox_inches="tight")
    return fig
