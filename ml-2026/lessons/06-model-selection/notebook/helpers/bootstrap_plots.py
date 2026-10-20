"""Bootstrap教学图。抽样与统计计算留在Notebook，图示按教材原理重绘。"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np
from course_plot_style import course_font_settings


def _style():
    return plt.rc_context({**course_font_settings(), "font.size": 18})


def _save(fig, assets_dir, stem):
    # Notebook的全局字体可能不同；逐个固定图中文字，避免回退到旧的中文字体。
    from matplotlib.text import Text
    family = course_font_settings()["font.family"][0]
    fig.canvas.draw()
    for label in fig.findobj(Text):
        label.set_fontfamily(family)
    fig.savefig(assets_dir / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(assets_dir / f"{stem}.png", dpi=240, bbox_inches="tight")


def plot_bootstrap_draws(values, indices, assets_dir):
    """真实Iris前五条，仅用于示意有放回抽样，不用五条估计总体区间。"""
    with _style():
        fig, ax = plt.subplots(figsize=(11.4, 7.6))
        ax.set(xlim=(0, 11.7), ylim=(0, 8.7)); ax.axis("off")
        fig.subplots_adjust(left=.01, right=.99, bottom=.01, top=.99)
        ink, blue, orange, muted = "#192b41", "#356dac", "#af6b26", "#52657a"
        labels = np.array(list("ABCDE"))
        def card(x, y, idx, repeated=False):
            color = orange if repeated else blue
            ax.add_patch(FancyBboxPatch((x, y), 1.12, .98,
                boxstyle="round,pad=.02,rounding_size=.08", linewidth=1.8,
                edgecolor=color, facecolor="#fff3e5" if repeated else "#edf4fc"))
            ax.text(x + .56, y + .65, labels[idx], ha="center", va="center", fontsize=25, color=color)
            ax.text(x + .56, y + .24, f"{values[idx]:.1f}", ha="center", va="center", fontsize=18, color=ink)

        ax.text(1.6, 8.35, "原样本：5条记录", fontsize=23, color=ink, va="center")
        ax.text(10.5, 8.35, "均值（cm）", fontsize=19, color=muted, ha="center", va="center")
        for idx in range(5):
            card(1.6 + idx * 1.32, 6.95, idx)
        ax.text(10.5, 7.44, f"{values.mean():.2f}", ha="center", va="center", fontsize=27, color=blue)
        ax.text(1.6, 6.35, "每次都从原样本中，有放回地抽5次", fontsize=20, color=ink, va="center")

        # 三条分支均始于原样本，避免画成“从上一份重抽样继续抽”。
        ax.plot([1.35, .12, .12], [7.44, 7.44, 1.6], color="#a5b7cb", lw=1.8)
        for r, row in enumerate(indices):
            y = 4.75 - r * 1.8
            ax.add_patch(FancyBboxPatch((1.35, y - .38), 10, 1.56,
                boxstyle="round,pad=.02,rounding_size=.12", facecolor="#f7f9fc", edgecolor="none"))
            ax.annotate("", xy=(1.32, y + .49), xytext=(.12, y + .49),
                        arrowprops={"arrowstyle": "->", "color": blue, "lw": 1.8})
            ax.text(.6, y + .85, f"第{r+1}次", fontsize=16, color=muted, ha="center")
            counts = np.bincount(row, minlength=5)
            for col, idx in enumerate(row):
                card(1.6 + col * 1.32, y, idx, repeated=counts[idx] > 1)
            missing = "、".join(labels[counts == 0]) or "无"
            repeated = "、".join(f"{labels[i]}×{counts[i]}" for i in np.flatnonzero(counts > 1)) or "无"
            ax.text(1.6, y - .23, f"重复：{repeated}    未抽到：{missing}", fontsize=16, color=muted, va="center")
            ax.annotate("", xy=(9.65, y + .49), xytext=(8.3, y + .49),
                        arrowprops={"arrowstyle": "->", "color": "#8b9eb2", "lw": 1.6})
            ax.text(10.5, y + .49, f"{values[row].mean():.2f}", ha="center", va="center", fontsize=27, color=ink)
        ax.text(1.6, .26, "橙框标出本轮重复的记录；每份仍是5条，均值却可能不同", fontsize=17, color=muted)
        _save(fig, assets_dir, "l6-bootstrap-draws")
    return fig


def plot_bootstrap_distribution(values, means, assets_dir):
    with _style():
        fig, axes = plt.subplots(2, 1, figsize=(9, 6.2))
        axes[0].hist(values, bins=15, color="#356dac", edgecolor="white", linewidth=.5)
        axes[0].set(title="原始测量值的分布", xlabel="每株花的萼片长度（cm）", ylabel="样本数")
        axes[0].text(.98, .85, f"数据标准差 s = {np.std(values, ddof=1):.3f} cm",
                     transform=axes[0].transAxes, ha="right", fontsize=16)
        axes[1].hist(means, bins=40, color="#af6b26", edgecolor="white", linewidth=.5)
        axes[1].axvline(np.mean(values), color="#26364a", ls="--", linewidth=1.5)
        axes[1].set(title=f"{len(means)}次重抽样均值的分布", xlabel="每份重抽样数据的均值（cm）", ylabel="重抽次数")
        axes[1].text(.98, .85, f"Bootstrap标准误差 = {np.std(means, ddof=1):.4f} cm",
                     transform=axes[1].transAxes, ha="right", fontsize=16)
        for ax in axes:
            ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout(h_pad=2)
        _save(fig, assets_dir, "l6-bootstrap-distribution")
    return fig


def plot_bootstrap_oob(assets_dir):
    """A,A,C,E,E用于训练，未抽到的B,D才是本轮袋外样本。"""
    with _style():
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.set(xlim=(0, 10), ylim=(0, 6)); ax.axis("off")
        ax.text(5, 5.6, "原始记录 A、B、C、D、E", ha="center", fontsize=23)
        ax.text(2.2, 4.35, "袋内样本\nA、A、C、E、E", ha="center", va="center", color="#356dac", fontsize=24)
        ax.text(7.6, 4.35, "本轮袋外样本\nB、D", ha="center", va="center", color="#af6b26", fontsize=24)
        ax.annotate("", xy=(2.2, 4.95), xytext=(4.4, 5.35), arrowprops={"arrowstyle": "->", "color": "#356dac", "lw": 2})
        ax.annotate("", xy=(7.6, 4.95), xytext=(5.6, 5.35), arrowprops={"arrowstyle": "->", "color": "#af6b26", "lw": 2})
        ax.add_patch(Rectangle((.85, 1.7), 2.7, .9, facecolor="#eef3fa", edgecolor="#356dac", linewidth=1.5))
        ax.text(2.2, 2.15, "拟合本轮模型", ha="center", va="center", fontsize=20)
        ax.add_patch(Rectangle((6.15, 1.7), 2.9, .9, facecolor="white", edgecolor="#af6b26", linewidth=1.5))
        ax.text(7.6, 2.15, "评价本轮模型", ha="center", va="center", fontsize=20)
        for x, color in [(2.2, "#356dac"), (7.6, "#af6b26")]:
            ax.annotate("", xy=(x, 2.7), xytext=(x, 3.65), arrowprops={"arrowstyle": "->", "color": color, "lw": 2})
        ax.annotate("模型预测", xy=(6.05, 2.15), xytext=(3.8, 2.15), va="center", fontsize=17,
                    arrowprops={"arrowstyle": "->", "color": "#26364a", "lw": 1.5})
        ax.text(5, .65, "本次2/5在袋外；换一次重抽样，袋外记录会改变", ha="center", fontsize=18, color="#52657a")
        _save(fig, assets_dir, "l6-bootstrap-oob")
    return fig


def render_bootstrap_formulas(assets_dir):
    expressions = {
        "l6-bootstrap-se-formula": r"$\widehat{\mathrm{SE}}_{\mathrm{boot}}(\hat\theta)=\sqrt{\frac{1}{B-1}\sum_{b=1}^{B}(\hat\theta^{*(b)}-\overline{\hat\theta^{*}})^2}$",
        "l6-bootstrap-oob-formula": r"$P(\mathrm{OOB})=(1-1/n)^n\ \overset{n\to\infty}{\longrightarrow}\ e^{-1}\approx36.8\%$",
    }
    with _style():
        for stem, expression in expressions.items():
            fig = plt.figure(figsize=(9, 1.35))
            fig.text(.5, .5, expression, ha="center", va="center", color="#255d9b", fontsize=26)
            _save(fig, assets_dir, stem)
            plt.close(fig)
