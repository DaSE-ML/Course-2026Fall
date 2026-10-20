"""第6讲真实风险示例的紧凑绘图辅助。训练与损失计算留在 Notebook。"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from course_plot_style import course_font_settings


def plot_diabetes_risk_realdata(
    train_bmi,
    train_y,
    heldout_bmi,
    heldout_y,
    model,
    train_predictions,
    heldout_predictions,
    train_mse,
    heldout_mse,
    output_path: Path,
    *,
    compact=True,
):
    """画同一条1近邻预测曲线下的训练风险与留出风险。"""
    train_bmi = np.asarray(train_bmi).reshape(-1)
    train_y = np.asarray(train_y).reshape(-1)
    heldout_bmi = np.asarray(heldout_bmi).reshape(-1)
    heldout_y = np.asarray(heldout_y).reshape(-1)
    train_predictions = np.asarray(train_predictions).reshape(-1)
    heldout_predictions = np.asarray(heldout_predictions).reshape(-1)
    all_bmi = np.concatenate([train_bmi, heldout_bmi])
    grid = np.linspace(all_bmi.min() - 1, all_bmi.max() + 1, 800).reshape(-1, 1)
    grid_predictions = model.predict(grid)
    rc = {**course_font_settings(), "font.size": 16 if compact else 18}
    with plt.rc_context(rc):
        fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.4), sharex=True, sharey=True)
        fig.subplots_adjust(left=.08, right=.98, bottom=.16, top=.82, wspace=.12)
        colors = {"train": "#2F6DB0", "heldout": "#CF6C20"}
        for ax in axes:
            ax.plot(grid[:, 0], grid_predictions, color="#23364B", lw=2.2, label="同一条已学预测曲线")
            ax.set(xlabel="BMI（原始值）", xlim=(all_bmi.min() - 1, all_bmi.max() + 1), ylim=(0, 365))
            ax.set_xticks([20, 25, 30, 35, 40])
            ax.set_yticks([0, 100, 200, 300])
            ax.grid(axis="y", color="#E6EBF0", linewidth=.8)
            ax.spines[["top", "right"]].set_visible(False)
            ax.spines[["bottom", "left"]].set_color("#AAB7C4")
        axes[0].set_ylabel("一年后的疾病进展指标（数据集原始量表）")
        axes[0].vlines(train_bmi, train_predictions, train_y, color=colors["train"], lw=2, zorder=3)
        axes[0].scatter(train_bmi, train_y, s=58, c=colors["train"], edgecolor="white", lw=.7,
                        zorder=4, label="参与训练的患者记录")
        axes[0].set_title("经验风险：训练样本平均", loc="left", pad=42, color=colors["train"], weight=600)
        axes[0].text(0, 1.035, f"{len(train_y)}个训练样本｜平方损失均值 = {train_mse:,.1f}",
                     transform=axes[0].transAxes, color=colors["train"], fontsize=15)
        order = np.argsort(heldout_bmi, kind="stable")
        shown = order[np.linspace(0, len(order) - 1, min(12, len(order)), dtype=int)]
        axes[1].scatter(heldout_bmi, heldout_y, s=18, c="#A4B0BB", alpha=.55,
                        edgecolors="none", zorder=1, label="未参与训练的患者记录")
        axes[1].vlines(heldout_bmi[shown], heldout_predictions[shown], heldout_y[shown],
                       color=colors["heldout"], lw=2, zorder=3, label="部分样本的预测误差")
        axes[1].scatter(heldout_bmi[shown], heldout_y[shown], s=44, c=colors["heldout"],
                        edgecolor="white", lw=.7, zorder=4)
        axes[1].set_title("泛化风险的估计：留出样本平均", loc="left", pad=42, color=colors["heldout"], weight=600)
        axes[1].text(0, 1.035, f"真实总体风险未知｜{len(heldout_y)}个留出样本估计 = {heldout_mse:,.1f}",
                     transform=axes[1].transAxes, color=colors["heldout"], fontsize=14)
        axes[0].legend(loc="lower right", fontsize=11, framealpha=.94)
        axes[1].legend(loc="lower right", fontsize=10.5, framealpha=.94)
        if compact:
            fig.text(.5, .045, "竖线表示单个样本的预测误差；均值使用各自全部样本。少量数据＋单特征仅供教学，不作临床结论。",
                     ha="center", fontsize=11.5, color="#52657A")
        else:
            fig.suptitle("同一个模型：训练风险不等于泛化风险", fontsize=22, weight=600, color="#23364B")
            fig.text(.5, .07, r"$\widehat R_{train}=\frac{1}{n}\sum_i(y_i-f_D(x_i))^2$；右图只估计未知总体风险。",
                     ha="center", fontsize=15, color="#23364B")
        fig.savefig(output_path, dpi=240, bbox_inches="tight", facecolor="white")
    return fig
