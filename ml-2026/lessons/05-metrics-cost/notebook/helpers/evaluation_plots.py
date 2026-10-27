"""Lesson05 display-only helpers. Training and evaluation stay in the notebook."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager, ft2font
from matplotlib.ticker import PercentFormatter
from matplotlib_inline.backend_inline import set_matplotlib_formats
from sklearn.metrics import roc_curve, precision_recall_curve, roc_auc_score, average_precision_score

COLORS = {"LR": "#245D8C", "kNN3": "#B66C25", "binnedCategoricalNB": "#747738", "Dummy": "#756579", "单调变换": "#B66C25"}
STYLES = {"LR": "-", "kNN3": "--", "binnedCategoricalNB": "-.", "Dummy": ":", "单调变换": "--"}
DISPLAY_NAMES = {"LR": "Logistic", "kNN3": "kNN（k=3）", "binnedCategoricalNB": "分箱NB", "Dummy": "Dummy", "单调变换": "单调变换"}


def _font_settings():
    """选择实际存在的中文字体与字重，不靠字体替换或隐藏日志。"""
    entries = font_manager.fontManager.ttflist
    for family in ["PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Heiti SC", "Arial Unicode MS"]:
        weights = sorted({font_manager.weight_dict.get(f.weight, f.weight)
                          for f in entries if f.name == family and f.style == "normal"})
        if not weights:
            continue
        regular = min(weights, key=lambda weight: abs(weight - 400))
        semibold = min(weights, key=lambda weight: abs(weight - 600))
        font_path = font_manager.findfont(
            font_manager.FontProperties(family=family, weight=regular), fallback_to_default=False)
        font = ft2font.FT2Font(font_path)
        if all(font.get_char_index(ord(char)) for char in "训练违约概率样本−"):
            return {"font.family": [family], "font.sans-serif": [family],
                    "font.weight": regular, "axes.labelweight": regular,
                    "axes.titleweight": regular, "figure.titleweight": semibold}
    raise RuntimeError("缺少可用的中文绘图字体，请安装 Noto Sans CJK SC 后重新运行。")


def setup():
    set_matplotlib_formats("retina")
    plt.rcParams.update({**_font_settings(),
                         "axes.unicode_minus": False, "font.size": 15, "axes.titlesize": 17,
                         "axes.labelsize": 15, "legend.fontsize": 13, "figure.dpi": 120,
                         "savefig.dpi": 220, "axes.spines.top": False, "axes.spines.right": False})


def finish(fig, path):
    if path is not None:
        fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.show()


def rates(ax, x=True, y=True):
    if x:
        ax.xaxis.set_major_formatter(PercentFormatter(1))
    if y:
        ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.grid(alpha=.15)


def plot_roc(y, scores, path=None):
    fig, ax = plt.subplots(figsize=(6.8, 5.2), layout="constrained")
    for name, p in scores.items():
        fpr, tpr, _ = roc_curve(y, p)
        ax.plot(fpr, tpr, color=COLORS[name], ls=STYLES[name], lw=2,
                label=f"{DISPLAY_NAMES[name]} · AUC={roc_auc_score(y, p):.3f}")
    ax.plot([0, 1], [0, 1], ":", color="#686868", label="随机排序参考")
    ax.set(xlim=(0, 1), ylim=(0, 1.02), xlabel="假正率 FPR", ylabel="真正率 TPR（召回率）",
           title="ROC｜同一验证集 6,000 人")
    ax.legend(loc="lower right")
    rates(ax)
    finish(fig, path)


def plot_pr(y, scores, baseline, path=None):
    fig, ax = plt.subplots(figsize=(6.8, 5.2), layout="constrained")
    for name, p in scores.items():
        precision, recall, thresholds = precision_recall_curve(y, p)
        # Descending recall + post uses P_i on the segment R_i -> R_(i+1).
        # Its positive area is exactly sklearn's non-interpolated AP sum.
        staircase_area = -np.sum(np.diff(recall) * precision[:-1])
        # 核对图中PR阶梯面积与非插值AP一致。
        assert np.isclose(staircase_area, average_precision_score(y, p))
        ax.step(recall, precision, where="post", color=COLORS[name], ls=STYLES[name], lw=2,
                label=f"{DISPLAY_NAMES[name]} · AP={average_precision_score(y, p):.3f}")
        if name == "kNN3":
            # 只标真正有阈值的工作点；末尾(Recall=0, Precision=1)是绘图端点。
            labels = ["t=0", "t=1/3", "t=2/3", "t=1"]
            offsets = [(-50, -30), (12, -30), (15, 18), (15, 18)]
            assert np.allclose(thresholds, [0, 1/3, 2/3, 1])
            ax.scatter(recall[:-1], precision[:-1], s=42, color=COLORS[name], zorder=5)
            for r, pr, label, offset in zip(recall[:-1], precision[:-1], labels, offsets):
                ax.annotate(label, (r, pr), xytext=offset, textcoords="offset points",
                            fontsize=12, color=COLORS[name],
                            bbox=dict(facecolor="white", edgecolor="none", alpha=.9, pad=2),
                            arrowprops=dict(arrowstyle="-", color=COLORS[name], lw=.8))
    ax.axhline(baseline, color="#686868", ls=":", label=f"正类率参考 {baseline:.1%}")
    ax.set(xlim=(0, 1), ylim=(0, 1.03), xlabel="召回率 Recall", ylabel="查准率 Precision",
           title="PR｜同一验证集 6,000 人；图例为非插值 AP")
    ax.legend(loc="upper right")
    rates(ax)
    finish(fig, path)


def plot_ap_area(precision, recall, ap, baseline):
    """Shade the actual recall-increment weighted area, without interpolating points."""
    fig, ax = plt.subplots(figsize=(7.5, 5.2), layout="constrained")
    ax.step(recall, precision, where="post", color=COLORS["LR"], lw=2)
    ax.fill_between(recall, 0, precision, step="post", color=COLORS["LR"], alpha=.18)
    ax.axhline(baseline, ls=":", color="#686868", label=f"真实正类比例 {baseline:.1%}")
    ax.text(.60, .75, f"矩形面积之和\nAP = {ap:.3f}", transform=ax.transAxes,
            color=COLORS["LR"], fontsize=18)
    ax.set(xlim=(0, 1), ylim=(0, 1.03), xlabel="召回率 Recall",
           ylabel="查准率 Precision", title="UCI验证集：AP的矩形面积")
    ax.legend(loc="lower left")
    rates(ax)
    finish(fig, None)


def plot_threshold_rates(table, path=None):
    precision = table["Precision"].to_numpy(dtype=float)
    recall = table["Recall"].to_numpy(dtype=float)
    denom = precision + recall
    f1 = np.where(denom > 0, 2 * precision * recall / np.where(denom > 0, denom, 1.0), 0.0)
    fig, ax = plt.subplots(figsize=(7.5, 5.2), layout="constrained")
    ax.plot(table["阈值"], f1, color="#23756C", ls="-.", lw=2.4,
            label="F1（调和平均）")
    for field, color, style in [("Precision", "#245D8C", "-"),
                                ("Recall", "#B66C25", "--"),
                                ("Accuracy", "#747738", ":")]:
        ax.plot(table["阈值"], table[field], color=color, ls=style, lw=2,
                label=field)
    ax.axvline(.5, ls=":", color="#686868", label="默认阈值0.5")
    ax.set(xlabel="分类阈值 Threshold", ylabel="指标", xlim=(0, 1), ylim=(0, 1.03),
           title="同一UCI模型：改变阈值后的分类指标")
    rates(ax, x=False)
    ax.legend(loc="lower right")
    finish(fig, path)


def plot_f1_threshold(table, path=None):
    precision = table["Precision"].to_numpy(dtype=float)
    recall = table["Recall"].to_numpy(dtype=float)
    denom = precision + recall
    f1 = np.where(denom > 0, 2 * precision * recall / np.where(denom > 0, denom, 1.0), 0.0)
    thresholds = table["阈值"].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(7.2, 4.6), layout="constrained")
    ax.plot(thresholds, f1, color="#245D8C", lw=2.2, label="F1 = 2PR/(P+R)")
    for t, color, offset in [(0.5, "#B66C25", (8, -22)), (0.3, "#23756C", (10, -30)), (0.1, "#8f401f", (-4, -34))]:
        i = int(np.argmin(np.abs(thresholds - t)))
        ax.scatter([thresholds[i]], [f1[i]], color=color, zorder=3, s=48)
        ax.annotate(f"t={t:g}\nF1={f1[i]:.2f}", (thresholds[i], f1[i]),
                    textcoords="offset points", xytext=offset, fontsize=11, color=color)
    best = int(np.argmax(f1))
    ax.scatter([thresholds[best]], [f1[best]], marker="*", s=240, color="#B8860B", zorder=4)
    ax.annotate(f"全扫描最大 t={thresholds[best]:.2f}，F1={f1[best]:.3f}",
                (thresholds[best], f1[best]), textcoords="offset points",
                xytext=(14, 10), fontsize=11, color="#7d650b")
    ax.set(xlabel="分类阈值 Threshold", ylabel="F1", xlim=(0, 1), ylim=(0, 1.06),
           title="同一UCI模型：F1 随阈值的完整形状")
    rates(ax, y=False)
    ax.legend(loc="lower center")
    finish(fig, path)


def plot_monotonic(p, changed, table, path=None):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.9), layout="constrained")
    order = np.argsort(p, kind="stable")
    axes[0].plot(p[order], changed[order], color=COLORS["单调变换"], lw=2)
    axes[0].plot([0, 1], [0, 1], ":", color="#686868")
    axes[0].set(xlabel="原概率 p", ylabel="变换后概率", title="严格单调：排序与并列保持", xlim=(0, 1), ylim=(0, 1))
    rates(axes[0])
    labels = ["ROC-AUC\n越大越好 ↑", "AP\n越大越好 ↑", "Brier\n越小越好 ↓", "Log loss\n越小越好 ↓"]
    positions = np.arange(4)
    for offset, name, hatch in [(-.18, "LR", ""), (.18, "单调变换", "//")]:
        values = table.loc[name, ["roc_auc", "ap", "brier", "logloss"]].to_numpy(dtype=float)
        bars = axes[1].bar(positions + offset, values, width=.34, color=COLORS[name], label=DISPLAY_NAMES[name], hatch=hatch)
        axes[1].bar_label(bars, labels=[f"{v:.3f}" for v in values], padding=4, fontsize=13, rotation=90)
    axes[1].set_xticks(positions, labels)
    axes[1].set(ylim=(0, 1), ylabel="指标数值", title="排序指标不变，概率损失可改变")
    axes[1].legend(loc="upper right")
    axes[1].grid(axis="y", alpha=.15)
    finish(fig, path)


def plot_calibration(tables, path=None):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.1), layout="constrained")
    for offset, (name, table) in zip([-.021, .021], tables.items()):
        present = table.n > 0
        axes[0].plot(table.loc[present, "meanp"], table.loc[present, "observed"],
                     marker="o" if name == "LR" else "s", ls=STYLES[name], color=COLORS[name], label=DISPLAY_NAMES[name])
        axes[1].bar(np.arange(.05, 1, .1) + offset, table.n, width=.04, color=COLORS[name],
                    hatch="" if name == "LR" else "//", label=DISPLAY_NAMES[name])
    axes[0].plot([0, 1], [0, 1], ":", color="#686868", label="理想参考")
    axes[0].set(xlim=(0, 1), ylim=(0, 1.03), xlabel="箱内平均预测概率 meanp",
                ylabel="箱内实际正类比例 observed", title="可靠性图｜10 个等宽概率箱")
    axes[1].set(xlim=(0, 1), xlabel="概率箱中心", ylabel="箱内人数 n", title="每箱样本量｜不是置信区间")
    rates(axes[0])
    rates(axes[1], y=False)
    axes[0].legend(loc="upper left")
    axes[1].legend(loc="upper right")
    finish(fig, path)


def plot_base_rate(table, path=None):
    fig, ax = plt.subplots(figsize=(8.5, 5.0), layout="constrained")
    bars = ax.bar(np.arange(len(table)), table.precision, width=.5, color="#245D8C")
    ax.bar_label(bars, labels=[f"{v:.2%}" for v in table.precision], padding=6)
    ax.set_xticks(np.arange(len(table)), [f"正类率 π={v:.0%}" for v in table.pi])
    ax.set(ylim=(0, 1), ylabel="被选中者中的正类比例（查准率）",
           title="基本率思想实验｜固定 TPR=80%、FPR=10%")
    rates(ax, x=False)
    fig.supxlabel("假设场景，不是 UCI 真实部署结果", fontsize=15)
    finish(fig, path)


def plot_capacity(table, path=None):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.1), layout="constrained")
    for name, group in table.groupby("model", sort=False):
        for ax, field in zip(axes, ["precision_at_k", "recall_at_k"]):
            ax.plot(group.k, group[field], marker="o", color=COLORS[name], ls=STYLES[name], label=DISPLAY_NAMES[name])
    for ax, label in zip(axes, ["前 K 名查准率 Precision@K", "前 K 名召回率 Recall@K"]):
        ax.axvline(600, color="#686868", ls=":", lw=1)
        ax.set(xlabel="核查名额 K（验证集 6,000 人）", ylabel=label, ylim=(0, 1), xticks=sorted(table.k.unique()))
        rates(ax, x=False)
    axes[0].legend(loc="upper right")
    fig.suptitle("固定容量比较｜并列按验证行顺序；不表示因果收益")
    finish(fig, path)


def plot_cost(table, best, path=None):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.8), layout="constrained")
    for ax, r in zip(axes, [1, 4, 10]):
        group = table.loc[table.r == r]
        row = best.loc[best.r == r].iloc[0]
        ax.plot(group.threshold, group.cost, "-o", color="#245D8C", markersize=4)
        ax.scatter([row.threshold], [row.cost], color="#B66C25", marker="s", s=70, zorder=3)
        ax.set(xlabel="候选阈值", ylabel=f"验证代价 FP + {r}FN", title=f"r={r}：最低 {row.cost:.0f}\n候选阈值 {row.threshold:.2f}",
               xlim=(0, 1), ylim=(0, group.cost.max() * 1.1))
        ax.grid(alpha=.15)
    fig.suptitle("Logistic 验证探索｜各 r 独立纵轴，不作跨 r 代价排名")
    finish(fig, path)


def plot_slide_views(p, changed, calibration_tables, capacity, asset_dir):
    """One panel per slide; retain the full multi-panel figures in the notebook."""
    fig, ax = plt.subplots(figsize=(6.8, 5.2), layout="constrained")
    order = np.argsort(p, kind="stable")
    ax.plot(p[order], changed[order], color=COLORS["单调变换"], lw=2)
    ax.plot([0, 1], [0, 1], ":", color="#686868", label="q=p 参考")
    ax.scatter([.5], [.5], color=COLORS["LR"], s=45)
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="原概率 p", ylabel="变换后概率 q", title="单调变换｜顺序保持，刻度改变")
    rates(ax); ax.legend()
    finish(fig, asset_dir / "lab05-slide-monotonic.png")

    fig, ax = plt.subplots(figsize=(6.8, 5.2), layout="constrained")
    for name, table in {"LR": calibration_tables["LR"]}.items():
        present = table.n > 0
        ax.plot(table.loc[present, "meanp"], table.loc[present, "observed"], marker="o" if name == "LR" else "s",
                ls=STYLES[name], color=COLORS[name], label=DISPLAY_NAMES[name])
    lr = calibration_tables["LR"]
    for number, (index, offset) in enumerate([(2, (8, -24)), (7, (-30, 20)), (9, (-105, -26))], 1):
        row = lr.iloc[index]
        ax.scatter(row.meanp, row.observed, s=65, color="#c05835", zorder=5)
        circled = "①②③"[number - 1]
        ax.annotate(f"{circled}: n={int(row.n)}", (row.meanp, row.observed), xytext=offset,
                    textcoords="offset points", fontsize=14,
                    arrowprops={"arrowstyle": "-", "color": "#52657a", "lw": .8})
    ax.plot([0, 1], [0, 1], ":", color="#686868", label="理想参考")
    ax.set(xlim=(0, 1), ylim=(0, 1.04), xticks=np.arange(0, 1.01, .1), xlabel="箱内平均预测违约概率", ylabel="箱内实际违约比例",
           title=f"UCI信用卡：{len(p):,}名验证客户\nLogistic可靠性图（10个等宽箱）")
    rates(ax); ax.legend(loc="upper left")
    finish(fig, asset_dir / "lab05-slide-calibration.png")

    fig, ax = plt.subplots(figsize=(6.8, 5.2), layout="constrained")
    for name, group in capacity.groupby("model", sort=False):
        ax.plot(group.k, group.precision_at_k, marker="o", markersize=3.5,
                color=COLORS[name], ls=STYLES[name], label=DISPLAY_NAMES[name])
    ax.axvline(300, color="#a1aab4", ls="--", lw=1)
    ax.axvline(600, color="#686868", ls=":")
    ax.set(ylim=(0, 1), xticks=[50, 300, 600, 900, 1200], xlabel="复核名额 K",
           ylabel="前K名查准率 P@K", title="复核量变化：每50人计算一次")
    rates(ax, x=False); ax.legend(loc="upper right")
    finish(fig, asset_dir / "lab05-slide-capacity.png")

def plot_capacity_cost(costs, path=None, capacity=600):
    """Compare actual candidate costs, retaining only capacity-feasible choices."""
    group = costs.loc[costs.r == 4].sort_values("threshold").copy()
    group["reported"] = group.TP + group.FP
    feasible = group.reported <= capacity
    unrestricted = group.loc[group.cost.idxmin()]
    constrained = group.loc[feasible].sort_values("cost").iloc[0]
    fig, ax = plt.subplots(figsize=(7.2, 5.2), layout="constrained")
    counts = ax.twinx()
    counts.spines["right"].set_visible(True)
    counts.plot(group.threshold, group.reported, "--", color="#B66C25", lw=1.8,
                label="报出人数（右轴）", zorder=1)
    counts.axhline(capacity, color="#B66C25", ls=":", lw=1.4)
    counts.text(.98, capacity + 100, "600人上限", transform=counts.get_yaxis_transform(),
                ha="right", va="bottom", fontsize=12, color="#B66C25")
    counts.set(ylim=(0, 6500), ylabel="报出人数 TP + FP（右轴）")
    counts.tick_params(axis="y", colors="#B66C25")
    counts.yaxis.label.set_color("#B66C25")
    ax.plot(group.threshold, group.cost, color="#bbc2c9", lw=1.5, zorder=1)
    ax.scatter(group.loc[~feasible, "threshold"], group.loc[~feasible, "cost"],
               color="#8c969f", marker="x", s=45, label="超过600人：不可选", zorder=3)
    ax.scatter(group.loc[feasible, "threshold"], group.loc[feasible, "cost"],
               color=COLORS["LR"], s=35, label="不超过600人：可选", zorder=3)
    for row, color, position, label in [
        (unrestricted, "#687681", (.48, .94), "不限制人数时最低"),
        (constrained, COLORS["LR"], (.43, .43), "满足容量时最低"),
    ]:
        ax.scatter(row.threshold, row.cost, s=125, facecolors="white", edgecolors=color,
                   linewidths=2, zorder=4)
        ax.annotate(f"{label}\nt={row.threshold:.2f}，代价{row.cost:,.0f}\n报出{row.reported:,.0f}人",
                    (row.threshold, row.cost), xytext=position, textcoords="axes fraction",
                    fontsize=13, color=color, va="top",
                    bbox=None if label == "不限制人数时最低" else {"facecolor": "white", "edgecolor": "none", "alpha": .95},
                    arrowprops={"arrowstyle": "->", "color": color, "lw": 1.2})
    ax.set(xlim=(0, 1), ylim=(0, group.cost.max()*1.22), xlabel="分类阈值 t",
           ylabel="总代价 FP + 4FN", title="r=4｜最多复核600人")
    handles, labels = ax.get_legend_handles_labels()
    count_handles, count_labels = counts.get_legend_handles_labels()
    ax.legend(handles + count_handles, labels + count_labels, loc="upper left", frameon=False,
              fontsize=11)
    ax.grid(alpha=.15)
    finish(fig, path)


def plot_confusion_counts(tp, fn, fp, tn, path=None):
    """Display the already computed counts; do not fit or score a model."""
    from matplotlib.patches import Rectangle
    # 用代码把同一组四格计数画成课堂图：行是真实类别，列是预测类别。
    counts = np.array([[tp, fn], [fp, tn]])
    cell_labels = [["TP · 真正例", "FN · 漏报"], ["FP · 误报", "TN · 真负例"]]
    cell_colors = [["#DCEBE8", "#F8E3D8"], ["#F6E7D0", "#E4EDF7"]]
    fig, ax = plt.subplots(figsize=(12.2, 7.0), dpi=180)
    ax.set_xlim(-1.75, 3.05)
    ax.set_ylim(2.55, -1.55)
    ax.axis("off")
    fig.suptitle("Logistic 回归 · 阈值 0.5：混淆矩阵", fontsize=20, fontweight=plt.rcParams["figure.titleweight"], color="#192B41", y=0.98)
    ax.text(0.5, -1.12, "列 = 模型预测\n列合计 = 报出人数", ha="center", va="center", fontsize=13, color="#255A91",
            bbox=dict(boxstyle="round,pad=0.35", fc="#EEF4FB", ec="#6B97C4", lw=1.5))
    ax.text(-1.4, 0.55, "行 = 真实类别\n行合计 = 实际人数", ha="center", va="center", fontsize=13, color="#6A4A1F", rotation=90,
            bbox=dict(boxstyle="round,pad=0.35", fc="#FBF2E5", ec="#C28B4B", lw=1.5))
    for j, label in enumerate(["预测违约\n（正类）", "预测未违约\n（负类）"]):
        ax.text(j, -0.62, label, ha="center", va="center", fontsize=14, fontweight=plt.rcParams["figure.titleweight"], color="#192B41")
    for i, label in enumerate(["实际违约\n（正类）", "实际未违约\n（负类）"]):
        ax.text(-0.62, i, label, ha="center", va="center", fontsize=13, fontweight=plt.rcParams["figure.titleweight"], color="#192B41")
    for i in range(2):
        for j in range(2):
            ax.add_patch(Rectangle((j-0.43, i-0.43), 0.86, 0.86, facecolor=cell_colors[i][j], edgecolor="white", lw=4))
            ax.text(j, i, f"{cell_labels[i][j]}\n{counts[i, j]:,}", ha="center", va="center", fontsize=13, fontweight=plt.rcParams["figure.titleweight"], color="#192B41", linespacing=1.35)
    for i, total in enumerate(counts.sum(axis=1)):
        ax.text(2.03, i, f"{total:,}", ha="center", va="center", fontsize=15, fontweight=plt.rcParams["figure.titleweight"], color="#6A4A1F",
                bbox=dict(boxstyle="round,pad=0.22", fc="#FBF2E5", ec="#C28B4B", lw=1.3))
    for j, total in enumerate(counts.sum(axis=0)):
        ax.text(j, 1.63, f"{total:,}", ha="center", va="center", fontsize=15, fontweight=plt.rcParams["figure.titleweight"], color="#255A91",
                bbox=dict(boxstyle="round,pad=0.22", fc="#EEF4FB", ec="#6B97C4", lw=1.3))
    ax.text(2.03, 1.63, "6,000", ha="center", va="center", fontsize=14, fontweight=plt.rcParams["figure.titleweight"], color="#192B41",
            bbox=dict(boxstyle="round,pad=0.22", fc="#F2F4F6", ec="#9AA6B2", lw=1.2))
    ax.text(2.03, -0.62, "行合计", ha="center", va="center", fontsize=12, color="#6A4A1F")
    ax.text(0.5, 1.94, "列合计", ha="center", va="center", fontsize=12, color="#255A91")
    ax.text(2.03, 2.02, "全部样本", ha="center", va="center", fontsize=11, color="#5D6B78")
    if path is not None:
        fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.show()
