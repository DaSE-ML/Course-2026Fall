"""第6讲真实时间序列划分图；切分与索引计算全部留在 Notebook。"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from course_plot_style import chinese_plot


_TRAIN = "#2F6DB0"
_VALID = "#C66B24"
_TEST = "#756B9A"
_UNUSED = "#A7B0BC"
_TEXT = "#516173"


def _dates_and_counts(bike):
    dates = bike["dteday"].to_numpy()
    counts = bike["cnt"].to_numpy()
    return dates, counts


def _style_axis(ax, dates, counts):
    ax.set_xlim(dates[0], dates[-1])
    ax.set_ylim(0, float(counts.max()) * 1.12)
    ax.grid(axis="y", color="#E6EBF0", linewidth=.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.tick_params(axis="x", rotation=35)
    ax.set_ylabel("每日租赁次数（cnt）")


def _plot_segments(ax, dates, counts, train_idx, valid_idx, final_test_idx):
    """在完整真实曲线上叠加传入的 train/valid/final-test 索引。"""
    ax.plot(dates, counts, color=_UNUSED, alpha=.36, linewidth=1.1, zorder=1)
    for indices, color, label, alpha in [
        (train_idx, _TRAIN, "训练", .95),
        (valid_idx, _VALID, "验证", .95),
        (final_test_idx, _TEST, "最终测试", .88),
    ]:
        if len(indices):
            ax.plot(dates[indices], counts[indices], color=color, linewidth=1.9,
                    alpha=alpha, label=label, zorder=3)
            ax.scatter(dates[indices], counts[indices], color=color, s=8,
                       alpha=alpha, edgecolors="none", zorder=4)


def _source_note(fig):
    fig.text(.99, .01, "来源：UCI Bike Sharing Dataset（CC BY 4.0）；daily cnt，2011–2012",
             ha="right", va="bottom", fontsize=11, color=_TEXT)


def _save(fig, output_path: Path):
    stem = Path(output_path).with_suffix("")
    fig.savefig(stem.with_suffix(".png"), bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")


@chinese_plot
def plot_time_holdout_real(bike, train_idx, valid_idx, final_test_idx, output_path: Path):
    """绘制一次留出：开发前491天训练、后120天验证、最后120天最终测试。"""
    dates, counts = _dates_and_counts(bike)
    fig, ax = plt.subplots(figsize=(13, 5.8))
    _plot_segments(ax, dates, counts, train_idx, valid_idx, final_test_idx)
    _style_axis(ax, dates, counts)
    ax.axvline(dates[valid_idx[0]], color=_VALID, ls="--", lw=1.2, alpha=.75)
    ax.axvline(dates[final_test_idx[0]], color=_TEST, ls="--", lw=1.2, alpha=.75)
    ax.set_title("按时间留出 Chronological Holdout", loc="left", pad=14)
    ax.set_xlabel("日期（真实每日连续曲线）")
    handles, _ = ax.get_legend_handles_labels()
    labels = [f"训练（{len(train_idx)}天）", f"验证（{len(valid_idx)}天）",
              f"最终测试（{len(final_test_idx)}天）"]
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, .99),
               ncol=3, frameon=False)
    fig.tight_layout(rect=(0, .04, 1, .90))
    _source_note(fig)
    _save(fig, output_path)
    return fig


@chinese_plot
def plot_time_windows_real(bike, expanding_splits, rolling_splits, final_test_idx, output_path: Path):
    """比较 expanding 与 rolling 的第1/3轮窗口；不重新计算切分。"""
    dates, counts = _dates_and_counts(bike)
    fig, axes = plt.subplots(2, 2, figsize=(15, 8), sharex=True, sharey=True)
    configs = [("expanding", expanding_splits), ("rolling", rolling_splits)]
    for row, fold_number in enumerate([1, 3]):
        for col, (name, splits) in enumerate(configs):
            ax = axes[row, col]
            train_idx, valid_idx = splits[fold_number - 1]
            _plot_segments(ax, dates, counts, train_idx, valid_idx, final_test_idx)
            _style_axis(ax, dates, counts)
            ax.axvspan(dates[train_idx[0]], dates[train_idx[-1]], color=_TRAIN,
                       alpha=.07, zorder=0)
            ax.axvspan(dates[valid_idx[0]], dates[valid_idx[-1]], color=_VALID,
                       alpha=.07, zorder=0)
            ax.axvspan(dates[final_test_idx[0]], dates[-1], color=_TEST,
                       alpha=.07, zorder=0)
            ax.axvline(dates[valid_idx[0]], color=_VALID, ls="--", lw=1, alpha=.7)
            ax.set_title(f"{name} Windows｜第{fold_number}轮（{len(train_idx)}+{len(valid_idx)}天）",
                         loc="left", pad=10)
            if row == 1:
                ax.set_xlabel("日期")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, .99),
               ncol=3, frameon=False)
    # 两列分别表示两种窗口协议，给轴标签留出空间后再放分割线。
    fig.tight_layout(rect=(0, .04, 1, .90), w_pad=6, h_pad=2)
    left = axes[0, 0].get_position()
    right = axes[0, 1].get_position()
    separator_x = left.x1 + (right.x0 - left.x1) * .35
    fig.add_artist(Line2D([separator_x, separator_x],
                         [axes[1, 0].get_position().y0 - .02, left.y1 + .035],
                         transform=fig.transFigure, color="#CBD4DE", linewidth=1.2))
    _source_note(fig)
    _save(fig, output_path)
    return fig


@chinese_plot
def plot_time_gap_real(bike, train_idx, gap_idx, valid_idx, final_test_idx, output_path: Path):
    """绘制指定轮次 gap=7 的完整曲线与边界放大图；索引由 Notebook 传入。"""
    dates, counts = _dates_and_counts(bike)
    fig, axes = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={"height_ratios": [1.2, 1]})
    _plot_segments(axes[0], dates, counts, train_idx, valid_idx, final_test_idx)
    _style_axis(axes[0], dates, counts)
    axes[0].set_title("训练与验证之间的7天间隔 Gap=7", loc="left", pad=12)
    axes[0].axvspan(dates[gap_idx[0]], dates[gap_idx[-1]], color="#9299A3", alpha=.28,
                    label="gap（不进拟合和评分）", zorder=0)
    axes[0].axvline(dates[gap_idx[0]], color="#9299A3", ls="--", lw=1)
    axes[0].axvline(dates[gap_idx[-1]], color="#9299A3", ls="--", lw=1)

    zoom_start = max(0, int(train_idx[-1]) - 18)
    zoom_end = min(len(dates) - 1, int(valid_idx[-1]) + 18)
    zoom_idx = np.arange(zoom_start, zoom_end + 1)
    ax = axes[1]
    ax.plot(dates[zoom_idx], counts[zoom_idx], color=_UNUSED, alpha=.38, linewidth=1.4)
    ax.plot(dates[train_idx], counts[train_idx], color=_TRAIN, linewidth=2, label="训练")
    ax.plot(dates[valid_idx], counts[valid_idx], color=_VALID, linewidth=2, label="验证/评分")
    ax.scatter(dates[gap_idx], counts[gap_idx], color="#9299A3", s=24, zorder=4, label="gap")
    ax.axvspan(dates[gap_idx[0]], dates[gap_idx[-1]], color="#9299A3", alpha=.28)
    ax.annotate("7天 gap\n不参与拟合，也不参与评分",
                xy=(dates[gap_idx[len(gap_idx) // 2]], counts[gap_idx].max()),
                xytext=(0, 42), textcoords="offset points", ha="center", color=_TEXT,
                arrowprops={"arrowstyle": "-", "color": _TEXT})
    ax.set_xlim(dates[zoom_start], dates[zoom_end])
    ax.set_ylim(0, float(counts[zoom_idx].max()) * 1.18)
    ax.grid(axis="y", color="#E6EBF0", linewidth=.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    ax.tick_params(axis="x", rotation=35)
    ax.set_ylabel("每日租赁次数（cnt）")
    ax.set_xlabel("边界日期（放大）")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5, .99),
               ncol=4, frameon=False)
    fig.tight_layout(rect=(0, .04, 1, .90))
    _source_note(fig)
    _save(fig, output_path)
    return fig
