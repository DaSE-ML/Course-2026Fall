"""第 6 讲：数据增强与重采样的静态教学图。

抽样、变换和 SMOTE 计算均在 Notebook 中完成；本模块只接收已经算好的
数据并负责绘图。所有图都使用第 6 讲的局部中文字体设置。
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from course_plot_style import chinese_plot, course_font_settings


BLUE = "#356dac"
ORANGE = "#af6b26"
PURPLE = "#7b3fa0"
INK = "#26364a"
MUTED = "#52657a"


def _save(fig, assets_dir, stem):
    """保存 SVG（文字转路径）和 300 dpi PNG，并固定中文字体族。"""
    out = Path(assets_dir)
    family = course_font_settings()["font.family"][0]
    fig.canvas.draw()
    # Notebook 可能在调用前改变了字体；逐个固定文字，避免 SVG 回退字体。
    for text in fig.findobj(plt.Text):
        text.set_fontfamily(family)
    fig.savefig(out / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(out / f"{stem}.png", dpi=300, bbox_inches="tight")


@chinese_plot
def plot_digits_augmentation(original, shifted, rotated, labels, assets_dir):
    """展示真实 8x8 digits 的原图、右移 1px 与 180° 旋转风险反例。"""
    original = np.asarray(original)
    shifted = np.asarray(shifted)
    rotated = np.asarray(rotated)
    labels = list(labels)
    if original.shape != (2, 8, 8) or shifted.shape != original.shape or rotated.shape != original.shape:
        raise ValueError("original、shifted、rotated 都必须是形状 (2, 8, 8) 的数组")
    if len(labels) != 2:
        raise ValueError("labels 必须包含两个数字标签")

    fig, axes = plt.subplots(2, 3, figsize=(10.8, 7.0), sharex=True, sharey=True)
    panels = [(original, "原图"), (shifted, "右移 1 px"), (rotated, "旋转 180°（风险）")]
    for row in range(2):
        for col, (images, title) in enumerate(panels):
            ax = axes[row, col]
            ax.imshow(images[row], cmap="gray", vmin=0, vmax=16, interpolation="nearest")
            ax.set_title(title, fontsize=18, color=INK, pad=8)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            if col == 0:
                ax.set_ylabel(f"数字 {labels[row]}", fontsize=18, color=INK, labelpad=12)
    fig.suptitle("8×8 digits：1 px 已是强变换；灰度范围 0–16", fontsize=23, color=INK, y=0.98)
    fig.text(
        0.5,
        0.025,
        "180° 旋转可能改变数字语义（如 6/9）；增强是否保标签取决于任务",
        ha="center",
        fontsize=16,
        color=MUTED,
    )
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.10, top=0.84, wspace=0.16, hspace=0.28)
    _save(fig, assets_dir, "l6-augmentation-digits")
    return fig


@chinese_plot
def plot_sampling_counts(rows, assets_dir):
    """比较四种方法的两类样本数；数值由 Notebook 提供，不在此处采样。"""
    if len(rows) != 4:
        raise ValueError("rows 必须按指定顺序包含 4 行")
    methods = [row["方法"] for row in rows]
    class0 = np.asarray([row["类别0"] for row in rows], dtype=float)
    class1 = np.asarray([row["类别1"] for row in rows], dtype=float)
    if np.any(class0 < 0) or np.any(class1 < 0):
        raise ValueError("样本数量不能为负数")

    fig, ax = plt.subplots(figsize=(11.2, 6.3))
    y = np.arange(len(methods))
    width = 0.34
    bars0 = ax.barh(y - width / 2, class0, height=width, color=BLUE, label="类别0")
    bars1 = ax.barh(y + width / 2, class1, height=width, color=ORANGE, label="类别1")
    ax.axvline(0, color=INK, linewidth=1.2)
    ax.set_yticks(y, methods)
    ax.invert_yaxis()
    ax.set_xlabel("样本数量", fontsize=18, labelpad=10)
    ax.set_title("各方法的训练类别计数", fontsize=22, color=INK, loc="left", pad=15)
    # 图例放到坐标轴外，避免遮住最长条右端的样本数标注。
    ax.legend(frameon=False, ncols=1, loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=16)
    ax.grid(axis="x", color="#e6ebf0", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=17)
    ax.tick_params(axis="x", labelsize=15)
    xmax = max(float(np.max(class0)), float(np.max(class1)), 1.0)
    ax.set_xlim(0, xmax * 1.22)
    for bars in (bars0, bars1):
        for bar in bars:
            value = bar.get_width()
            ax.text(value + xmax * 0.018, bar.get_y() + bar.get_height() / 2,
                    f"{value:g}", va="center", fontsize=16, color=INK)
    fig.subplots_adjust(left=0.18, right=0.78, bottom=0.14, top=0.84)
    _save(fig, assets_dir, "l6-sampling-counts")
    return fig


@chinese_plot
def plot_smote_geometry(X, y, xi, xj, xnew, assets_dir):
    """展示二维 Iris 特征中的 SMOTE 线段与生成点；不计算生成点。"""
    X = np.asarray(X)
    y = np.asarray(y)
    xi = np.asarray(xi, dtype=float)
    xj = np.asarray(xj, dtype=float)
    xnew = np.asarray(xnew, dtype=float)
    if X.ndim != 2 or X.shape[1] != 2 or len(X) != len(y):
        raise ValueError("X 必须是 (n, 2)，且 y 长度与 X 相同")
    if xi.shape != (2,) or xj.shape != (2,) or xnew.shape != (2,):
        raise ValueError("xi、xj、xnew 必须是长度为 2 的坐标")

    fig, (ax, ax_zoom) = plt.subplots(
        2, 1, figsize=(11.4, 9.4),
        gridspec_kw={"height_ratios": [3, 2], "hspace": 0.42},
    )
    for cls, color, marker, name in [(0, BLUE, "o", "类别0"), (1, ORANGE, "^", "类别1")]:
        mask = y == cls
        ax.scatter(X[mask, 0], X[mask, 1], s=46, alpha=0.68, color=color,
                   marker=marker, edgecolors="white", linewidths=0.5, label=name)
    # 主图保留完整上下文；下方独立放大近邻区域，避免遮住散点。
    local_x = np.array([xi[0], xj[0], xnew[0]])
    local_y = np.array([xi[1], xj[1], xnew[1]])
    local_xpad = max(float(np.ptp(local_x)) * 3.0, 0.12)
    local_ypad = max(float(np.ptp(local_y)) * 3.0, 0.10)
    local_box = Rectangle(
        (local_x.min() - local_xpad / 3, local_y.min() - local_ypad / 3),
        local_xpad * 2 / 3,
        local_ypad * 2 / 3,
        facecolor="none",
        edgecolor=PURPLE,
        linewidth=1.5,
        linestyle=":",
        zorder=4,
    )
    ax.add_patch(local_box)
    ax.plot([xi[0], xj[0]], [xi[1], xj[1]], color=PURPLE, linewidth=2.0,
            linestyle="--", zorder=4)
    ax.scatter([xi[0], xj[0]], [xi[1], xj[1]], s=115, facecolors="white",
               edgecolors=PURPLE, linewidths=1.8, zorder=5)
    ax.scatter([xnew[0]], [xnew[1]], s=145, marker="D", color=PURPLE,
               edgecolors="white", linewidths=0.8, zorder=6)

    ax_zoom.set_xlim(local_x.mean() - local_xpad, local_x.mean() + local_xpad)
    ax_zoom.set_ylim(local_y.mean() - local_ypad, local_y.mean() + local_ypad)
    ax_zoom.plot([xi[0], xj[0]], [xi[1], xj[1]], color=PURPLE, linewidth=2.5,
                 linestyle="--", zorder=3)
    ax_zoom.scatter([xi[0], xj[0]], [xi[1], xj[1]], s=175, facecolors="white",
                    edgecolors=PURPLE, linewidths=2.0, zorder=4)
    ax_zoom.scatter([xnew[0]], [xnew[1]], s=220, marker="D", color=PURPLE,
                    edgecolors="white", linewidths=0.8, zorder=5)
    ax_zoom.annotate(r"$x_i$", xi, xytext=(14, 16), textcoords="offset points",
                     color=PURPLE, fontsize=15, ha="left")
    ax_zoom.annotate(r"$x_j$", xj, xytext=(-14, 16), textcoords="offset points",
                     color=PURPLE, fontsize=15, ha="right")
    ax_zoom.annotate(r"$x_{\mathrm{new}}$", xnew, xytext=(5, -22), textcoords="offset points",
                     color=PURPLE, fontsize=15, ha="left")
    ax_zoom.set_title("局部放大：同类邻居与 λ=0.4 插值点", fontsize=20, color=INK,
                      loc="left", pad=10)
    ax_zoom.set_xlabel("花瓣长度（cm）", fontsize=17)
    ax_zoom.set_ylabel("花瓣宽度（cm）", fontsize=17)
    ax_zoom.tick_params(labelsize=13)
    ax_zoom.grid(color="#e6ebf0", linewidth=0.8)
    ax_zoom.spines[["top", "right"]].set_visible(False)
    ax_zoom.text(0.99, 0.93, "紫色菱形：x_new", transform=ax_zoom.transAxes,
                 ha="right", va="top", fontsize=15, color=PURPLE)
    ax.set_xlabel("花瓣长度（cm）", fontsize=18)
    ax.set_ylabel("花瓣宽度（cm）", fontsize=18)
    ax.set_title("SMOTE：沿同类邻居线段生成中间点", fontsize=22, color=INK, loc="left", pad=15)
    ax.text(0.02, 0.97, "机制示意：λ = 0.4；不是某一轮随机采样结果",
            transform=ax.transAxes, va="top", fontsize=16, color=MUTED)
    ax.legend(frameon=False, fontsize=15, loc="upper left", bbox_to_anchor=(1.01, 0.98))
    ax.grid(color="#e6ebf0", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.subplots_adjust(left=0.12, right=0.80, bottom=0.10, top=0.93)
    _save(fig, assets_dir, "l6-smote-geometry")
    return fig


@chinese_plot
def render_smote_formula(assets_dir):
    """保存 SMOTE 线性插值公式图。"""
    fig = plt.figure(figsize=(10.6, 1.55))
    fig.text(0.5, 0.5, r"$x_{\mathrm{new}}=x_i+\lambda(x_j-x_i),\quad \lambda\in[0,1]$",
             ha="center", va="center", fontsize=31, color=PURPLE)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    _save(fig, assets_dir, "l6-smote-formula")
    return fig
