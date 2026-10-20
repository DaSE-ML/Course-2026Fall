"""第6讲 Ridge 风险图辅助；拟合、预测与损失口径留在 Notebook。"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from course_plot_style import course_font_settings


def plot_diabetes_risk_ridge(
    diabetes_bmi,
    diabetes_target,
    train_idx,
    heldout_idx,
    fitted_model,
    output_path: Path,
):
    """绘制已拟合 Ridge 在训练/留出样本上的风险；本函数不训练模型。"""
    diabetes_bmi = np.asarray(diabetes_bmi).reshape(-1, 1)
    diabetes_target = np.asarray(diabetes_target).reshape(-1)
    train_idx = np.asarray(train_idx)
    heldout_idx = np.asarray(heldout_idx)

    predictions = fitted_model.predict(diabetes_bmi)
    loss = (diabetes_target - predictions) ** 2
    grid = np.linspace(diabetes_bmi.min(), diabetes_bmi.max(), 1200).reshape(-1, 1)
    curve = fitted_model.predict(grid)

    # 使用真实字体族名；局部样式不受Notebook前面单元格的字体设置影响。
    rc = {**course_font_settings(), "font.size": 16, "axes.labelsize": 16,
          "xtick.labelsize": 16, "ytick.labelsize": 16}
    with plt.rc_context(rc):
        fig, axes = plt.subplots(1, 2, figsize=(15, 7), sharex=True, sharey=True)
        fig.subplots_adjust(left=.075, right=.98, bottom=.29, top=.74, wspace=.12)
        fig.suptitle("同一条预测曲线，在训练样本和新样本上表现如何？", fontsize=23, y=.97)
        fig.text(.5, .90, "Diabetes真实数据｜BMI → 一年后的疾病进展｜五次多项式特征 + Ridge（α=1）",
                 ha="center", fontsize=16, color="#516173")
        all_min, all_max = float(diabetes_bmi.min()), float(diabetes_bmi.max())
        train_min, train_max = float(diabetes_bmi[train_idx].min()), float(diabetes_bmi[train_idx].max())
        for ax, ids, color, title in zip(
            axes, [train_idx, heldout_idx], ["#2F6DB0", "#C66B24"],
            ["经验风险：训练样本平均", "泛化风险的估计：留出样本平均"],
        ):
            ax.plot(grid[:, 0], curve, color="#273A50", lw=2.4, label="同一条已拟合曲线")
            ax.scatter(diabetes_bmi[ids, 0], diabetes_target[ids],
                       s=50 if len(ids) == 20 else 21, color=color,
                       alpha=.9 if len(ids) == 20 else .45, edgecolors="none",
                       label="训练样本" if len(ids) == 20 else "留出样本")
            ordered = ids[np.argsort(diabetes_bmi[ids, 0], kind="stable")]
            shown = ids if len(ids) == 20 else ordered[np.linspace(0, len(ids) - 1, 12, dtype=int)]
            ax.vlines(diabetes_bmi[shown, 0], predictions[shown], diabetes_target[shown],
                      color=color, alpha=.7, lw=1.4)
            ax.set_title(title, fontsize=19, weight="medium", color=color, pad=39, loc="left")
            ax.text(0, 1.025, f"{len(ids)} 个样本｜MSE = {loss[ids].mean():,.1f}",
                    transform=ax.transAxes, color=color, fontsize=18)
            ax.set_xlabel("BMI（原始值）")
            ax.grid(axis="y", color="#E6EBF0")
            ax.spines[["top", "right"]].set_visible(False)
            ax.axvspan(all_min, train_min, color="#A7B0BC", alpha=.13)
            ax.axvspan(train_max, all_max, color="#A7B0BC", alpha=.13)
            ax.legend(loc="upper left", fontsize=14)
        axes[0].set_ylabel("一年后的疾病进展指标")
        low = min(0, float(curve.min()), float(predictions.min()))
        high = max(float(diabetes_target.max()), float(curve.max()), float(predictions.max()))
        axes[0].set_ylim(low - .04 * (high - low), high + .08 * (high - low))
        fig.text(.5, .135, "竖线表示预测误差，平方后求平均得到 MSE；两图使用同一模型、相同坐标。",
                 ha="center", fontsize=15)
        fig.text(.5, .08, "灰区为训练范围外的外推；右图画12条误差线，MSE用全部422条留出记录。总体风险未知。",
                 ha="center", fontsize=14, color="#516173")
        fig.text(.5, .03, "仅20条训练记录、单特征用于教学，不作临床结论。",
                 ha="center", fontsize=14, color="#516173")
        fig.savefig(output_path, dpi=300, facecolor="white")
    return fig
