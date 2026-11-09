"""Lesson 07 Bike Sharing figures. Each function uses local Matplotlib settings."""
from pathlib import Path
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import font_manager
import matplotlib.dates as mdates


def _font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for candidate in ("PingFang SC", "PingFang HK", "Heiti TC", "Microsoft YaHei", "Noto Sans CJK SC"):
        if candidate in names:
            path = font_manager.findfont(candidate, fallback_to_default=False)
            face = font_manager.ft2font.FT2Font(path)
            required = "每日租赁次数温度预测叶子−0123"
            if all(face.get_char_index(ord(char)) for char in required):
                return candidate
    raise RuntimeError("缺少中文绘图字体，请安装苹方、微软雅黑或 Noto Sans CJK SC。")


def _save(fig, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with matplotlib.rc_context({"svg.fonttype": "path"}):
        fig.savefig(path, format="svg", bbox_inches="tight")
        fig.savefig(path.with_suffix(".png"), dpi=260, bbox_inches="tight")
    plt.close(fig)


def _base():
    return matplotlib.rc_context({
        "font.family": _font(), "font.size": 15, "axes.titlesize": 22,
        "axes.labelsize": 18, "xtick.labelsize": 13, "ytick.labelsize": 13,
        "legend.fontsize": 13, "axes.unicode_minus": False,
        "figure.facecolor": "white", "axes.facecolor": "#fbfcfe",
        "axes.spines.top": False, "axes.spines.right": False,
    })


def timeline(dates, y, path):
    import pandas as pd
    dates = pd.DatetimeIndex(dates)
    values = pd.Series(np.asarray(y), index=dates)
    smooth = values.rolling(30, min_periods=30).mean()
    with _base():
        fig, ax = plt.subplots(figsize=(16.8, 5.4))
        ax.plot(dates, values, color="#2377b5", linewidth=1.2, alpha=.58,
                label="每日实际租赁次数")
        ax.plot(dates, smooth, color="#b85d24", linewidth=2.8,
                label="30日滑动均值（含当日及之前29天）")
        for year in (2011, 2012):
            ax.axvspan(pd.Timestamp(year, 5, 1), pd.Timestamp(year, 9, 1),
                       color="#e8b779", alpha=.16, linewidth=0)
        ax.axvspan(pd.Timestamp(2011, 12, 1), pd.Timestamp(2012, 3, 1),
                   color="#a9c9e5", alpha=.18, linewidth=0)
        annotations = [
            ("暖季需求较高", "2011-07-15", "2011-05-15", 7000),
            ("冬季回落", "2012-01-15", "2011-12-05", 5100),
            ("第二年暖季整体更高", "2012-07-15", "2012-04-20", 9600),
        ]
        for label, anchor, label_date, label_y in annotations:
            day = pd.Timestamp(anchor)
            ax.annotate(label, xy=(day, smooth.loc[day]),
                        xytext=(pd.Timestamp(label_date), label_y), fontsize=17,
                        color="#273e50", ha="center", va="center",
                        arrowprops={"arrowstyle":"->", "color":"#586b78", "lw":1.3})
        ax.set(xlabel="日期", ylabel="每日租赁总次数 cnt", ylim=(0, 10100),
               xlim=(dates.min(), dates.max()))
        ticks = list(pd.date_range(dates.min(), dates.max(), freq="2MS"))
        ticks.append(dates.max())
        ax.set_xticks(ticks)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.tick_params(axis="both", labelsize=15)
        ax.legend(loc="upper left", frameon=False, fontsize=14)
        ax.grid(axis="y", alpha=.18)
        fig.tight_layout(pad=.7)
        _save(fig, path)


def scatter(x, y, path, title="气温指标与每日租赁次数", cuts=(), leaf_values=(), highlight=None, observations=False):
    with _base():
        fig, ax = plt.subplots(figsize=(16.8, 5.4))
        ax.scatter(x, y, s=30, alpha=.64, color="#3579a8", edgecolors="white", linewidths=.35, label="开发样本")
        if highlight is not None:
            ax.scatter([x[highlight]], [y[highlight]], marker="*", s=250, color="#e36c36", edgecolor="white", linewidth=1.2, zorder=4, label="高亮记录")
        if cuts:
            bounds = [-.02, *cuts, 1.02]
            colors = ["#f3d8bd", "#d9e9f4", "#d9ead3"]
            # 保持原0.419阈值为橙红色，新增的左侧阈值用紫色。
            cut_colors = ["#c45238"] if len(cuts) == 1 else ["#8060a8", "#c45238"]
            for i, cut in enumerate(cuts):
                ax.axvline(cut, color=cut_colors[i % len(cut_colors)], linewidth=2.5, linestyle="--", label=f"切分阈值 {cut:.3f}")
            if leaf_values:
                for i, value in enumerate(leaf_values):
                    left, right = bounds[i], bounds[i+1]
                    ax.axvspan(left, right, color=colors[i], alpha=.26, zorder=0)
                    ax.hlines(value, left, right, color="#263746", linewidth=3, label="叶子预测（区间均值）" if i == 0 else None)
        ax.set(xlim=(0, 1), ylim=(0, 9800), title="", xlabel="气温指标 temp（原始归一化值；越大越暖）", ylabel="每日租赁次数 cnt")
        ax.tick_params(axis="both", labelsize=15)
        if observations:
            x, y = np.asarray(x), np.asarray(y)
            # 按气温排序，每41个相邻样本取均值，仅用于观察趋势。
            order = np.argsort(x, kind="stable")
            window = np.ones(41) / 41
            mean_x = np.convolve(x[order], window, mode="valid")
            mean_y = np.convolve(y[order], window, mode="valid")
            ax.plot(mean_x, mean_y, color="#b85d24", linewidth=2.7,
                    label="按气温排序的41样本滑动均值", zorder=3)
            # 圈出气温接近0.5的两条真实记录，展示纵向差异。
            close = np.flatnonzero((x >= .49) & (x <= .51))
            pair = close[[np.argmin(y[close]), np.argmax(y[close])]]
            ax.scatter(x[pair], y[pair], s=125, facecolors="none",
                       edgecolors="#b85d24", linewidths=1.7, zorder=5)
            arrow_x = float(np.mean(x[pair]))
            for sample in pair:
                ax.plot([x[sample], arrow_x], [y[sample], y[sample]],
                        color="#b85d24", linewidth=1.3, zorder=4)
            ax.annotate("", xy=(arrow_x, y[pair[0]]), xytext=(arrow_x, y[pair[1]]),
                        arrowprops={"arrowstyle":"<->", "color":"#b85d24", "lw":1.6,
                                    "shrinkA":5, "shrinkB":5})
            def representative(mask):
                ids = np.flatnonzero(mask)
                return ids[np.argmin(np.abs(y[ids] - np.median(y[ids])))]
            low, high = representative(x < .25), representative(x > .79)
            labels = [
                ("低温区：租赁量通常较少", (x[low], y[low]), (.15, 6100)),
                ("相近气温，租赁量仍有明显差异", (arrow_x, y[pair[1]]), (.47, 9100)),
                ("高温端未持续上升", (x[high], y[high]), (.84, 7600)),
            ]
            for text, anchor, label in labels:
                ax.annotate(text, xy=anchor, xytext=label, fontsize=18,
                            color="#273e50", ha="center", va="center",
                            bbox={"facecolor":"white", "edgecolor":"none", "alpha":.88, "pad":3},
                            arrowprops={"arrowstyle":"->", "color":"#586b78", "lw":1.3})
            ax.set(title="", ylim=(0, 9800), xlim=(0, 1))
            ax.tick_params(axis="both", labelsize=15)
        ax.grid(alpha=.18); ax.legend(frameon=False, loc="lower right" if observations else "best")
        fig.tight_layout(); _save(fig, path)


def tree_diagram(tree, feature_names, path, highlight_leaf=None, highlight_path=(), highlight_text=None):
    from sklearn.tree import _tree
    t = tree.tree_
    positions = {}
    def place(node, depth, x0, x1):
        if t.children_left[node] == _tree.TREE_LEAF:
            positions[node] = ((x0+x1)/2, -depth)
            return
        mid = (x0+x1)/2
        place(t.children_left[node], depth+1, x0, mid)
        place(t.children_right[node], depth+1, mid, x1)
        positions[node] = (mid, -depth)
    place(0, 0, 0, 1)
    with _base():
        fig, ax = plt.subplots(figsize=(12, 5.3))
        for node in range(t.node_count):
            x0, y0 = positions[node]
            for child, label in ((t.children_left[node], "是"), (t.children_right[node], "否")):
                if child != _tree.TREE_LEAF or child in positions:
                    if child in positions:
                        x1, y1 = positions[child]
                        on_path = node in highlight_path and child in highlight_path
                        ax.plot([x0,x1],[y0-.06,y1+.12],color="#dd7049" if on_path else "#657786",lw=3.2 if on_path else 1.7,zorder=1)
                        ax.text((x0+x1)/2,(y0+y1)/2,label,ha="center",va="center",fontsize=12,color="#52616d")
            value=float(t.value[node].reshape(-1)[0]); count=int(t.n_node_samples[node])
            if t.children_left[node] == _tree.TREE_LEAF:
                text=f"预测 {value:,.0f} 次\n{count} 条日记录"
                color="#dcebd7"; w=.17
            else:
                text=f"{feature_names[t.feature[node]]} ≤ {t.threshold[node]:.3f}"
                color="#dce9f4"; w=.25
            x,y=positions[node]
            ax.text(x,y,text,ha="center",va="center",fontsize=13,
                    bbox={"boxstyle":"round,pad=.55","fc":color,"ec":"#637887","lw":1.2},zorder=3)
        if highlight_leaf is not None and highlight_leaf in positions:
            x,y=positions[highlight_leaf]
            ax.scatter([x+.105],[y],marker="*",s=210,color="#e36c36",edgecolor="white",zorder=5)
        root_x, root_y = positions[0]
        ax.annotate("根节点（root node）", xy=(root_x + .04, root_y + .08),
                    xytext=(.80, .42), fontsize=15, ha="center", color="#273e50",
                    arrowprops={"arrowstyle":"->", "color":"#657786", "lw":1.3})
        for depth in range(tree.get_depth() + 1):
            ax.text(-.13, -depth, f"深度 {depth}", ha="center", va="center",
                    fontsize=14, color="#657384")
        ax.text(.84, -tree.get_depth()-.4, f"树深度 = {tree.get_depth()}\n根到最深叶的边数",
                ha="center", va="center", fontsize=14, color="#273e50")
        ax.set_title("同一棵三叶树：从根节点沿条件走到叶节点")
        if highlight_text:
            ax.text(.5,-max(1,tree.get_depth())-.68,highlight_text,ha="center",va="center",fontsize=13,color="#9b4e35")
        ax.set_xlim(-.23,1.12); ax.set_ylim(-max(1,tree.get_depth())-1.0,.65); ax.axis("off")
        fig.tight_layout(); _save(fig,path)


def leaf_mean(x, y, mask, mean, path):
    with _base():
        fig, axes = plt.subplots(2, 1, figsize=(10.8, 8.0), gridspec_kw={"height_ratios":[1, 1.1]})
        ax, loss_ax = axes
        values = np.asarray(y)[mask]
        ax.scatter(np.asarray(x)[mask], values, s=38, alpha=.72, color="#3579a8", edgecolor="white", linewidth=.5)
        ax.axhline(mean, color="#c45238", lw=2.5, label=f"叶均值 = {mean:,.1f} 次")
        ax.set(title=f"固定同一叶子的 {len(values)} 条记录", xlabel="气温指标 temp", ylabel="实际租赁次数")
        ax.grid(alpha=.18); ax.legend(frameon=False, fontsize=14)
        candidates = np.linspace(mean-2500, mean+2500, 301)
        losses = np.sum((values[:, None]-candidates[None, :])**2, axis=0)
        minimum = float(np.sum((values-mean)**2))
        loss_ax.plot(candidates, losses/1e6, color="#3579a8", lw=2.4)
        loss_ax.scatter([mean], [minimum/1e6], color="#c45238", s=75, zorder=5)
        loss_ax.axvline(mean, color="#c45238", lw=1.3, ls="--")
        loss_ax.annotate(f"最低点：c = 均值 ≈ {mean:,.1f}\nSSE ≈ {minimum/1e6:,.1f} 百万次²",
                         xy=(mean, minimum/1e6), xytext=(mean+550, minimum/1e6+450),
                         fontsize=14, color="#273e50", arrowprops={"arrowstyle":"->", "color":"#657786"})
        loss_ax.set(title="改变候选预测值 c，比较误差平方和", xlabel="叶子共用的候选预测值 c（次）", ylabel="SSE（百万次²）")
        loss_ax.grid(alpha=.18)
        fig.tight_layout(pad=1.0, h_pad=2.0); _save(fig, path)


def split_sse(candidates, sse, best, path):
    with _base():
        fig,ax=plt.subplots(figsize=(11,5.6))
        ax.plot(candidates,sse,color="#4180a8",lw=1.5)
        ax.scatter(candidates,sse,s=13,color="#4180a8",alpha=.55)
        ax.scatter([candidates[best]],[sse[best]],s=150,color="#d85f3f",zorder=4,label=f"最优阈值 {candidates[best]:.3f}；SSE {sse[best]:,.0f}")
        ax.set(title="枚举温度中点：选择切分后 SSE 最小的位置",xlabel="候选温度阈值",ylabel="切分后总平方误差 SSE（次²）")
        ax.grid(alpha=.2);ax.legend(frameon=False);fig.tight_layout();_save(fig,path)


def complexity(depths, train, folds, path, leaf_sizes=None, leaf_train=None, leaf_folds=None):
    with _base():
        fig,axes=plt.subplots(1,2,figsize=(14.5,5.6),sharey=True)
        cases=[(axes[0],["1","2","3","5","8","不限制"],train,folds,
                "改变最大深度\n固定 min_samples_leaf=1","max_depth"),
               (axes[1],[str(n) for n in leaf_sizes],leaf_train,leaf_folds,
                "改变叶子最少样本数\n固定 max_depth=None","min_samples_leaf")]
        for ax,labels,training,validation,title,xlabel in cases:
            positions=np.arange(len(labels))
            for j,values in enumerate(validation):
                ax.scatter(np.repeat(j,len(values)),np.asarray(values)/1e6,s=35,alpha=.65,color="#81a9bf",label="各折验证结果" if j==0 else None)
            ax.plot(positions,np.mean(validation,axis=1)/1e6,"o-",lw=2.7,color="#cf633f",label="验证均值")
            ax.plot(positions,np.asarray(training)/1e6,"s--",lw=2,color="#496d8a",label="训练均值")
            ax.set_xticks(positions,labels);ax.tick_params(labelsize=15)
            ax.set_title(title,fontsize=18);ax.set_xlabel(xlabel,fontsize=18);ax.grid(alpha=.18)
        axes[0].set_ylabel("MSE（百万次²）",fontsize=18)
        handles,labels=axes[0].get_legend_handles_labels()
        fig.legend(handles,labels,loc="lower center",ncol=3,frameon=False,fontsize=14,bbox_to_anchor=(.5,-.01))
        fig.tight_layout(rect=(0,.09,1,1),w_pad=2);_save(fig,path)


def curves(xgrid, curves, average, path, title, ylabel="预测租赁次数"):
    with _base():
        fig,ax=plt.subplots(figsize=(10.8,5.7))
        for row in curves: ax.plot(xgrid,row,color="#6d9ab0",alpha=.28,lw=1.15)
        if average is not None: ax.plot(xgrid,average,color="#d45d3f",lw=3,label="平均预测");ax.legend(frameon=False)
        ax.set(title=title,xlabel="气温指标 temp（0 到 1）",ylabel=ylabel);ax.grid(alpha=.2);fig.tight_layout();_save(fig,path)






def bagging_overview(points=None, mean=None, path=None, comparison=None):
    """左侧展示抽样与汇总，右侧可比较单树与不同树数的平均预测。"""
    from matplotlib.patches import FancyBboxPatch
    with _base():
        fig, (flow, ax) = plt.subplots(1, 2, figsize=(16.5, 4.9),
                                      gridspec_kw={'width_ratios': [1, 1.35]})
        flow.set(xlim=(0, 1), ylim=(0, 1)); flow.axis('off')
        def box(x, y, width, height, text, fill='#edf4f9'):
            flow.add_patch(FancyBboxPatch((x, y), width, height,
                boxstyle='round,pad=.009', facecolor=fill, edgecolor='#3c6583', linewidth=1.3))
            flow.text(x+width/2, y+height/2, text, ha='center', va='center', fontsize=16)
        def arrow(start, end):
            flow.annotate('', xy=end, xytext=start,
                arrowprops={'arrowstyle':'->', 'color':'#5c7f96', 'lw':1.4})
        box(.23, .79, .54, .16, '训练记录\nA  B  C  D')
        for x, sample, name in zip([.015, .355, .695],
                                  ['A A C D', 'B C C D', 'A B B D'], ['树1', '树2', '树B']):
            arrow((.5, .78), (x+.145, .64))
            box(x, .47, .29, .16, sample+'\n有放回抽样')
            arrow((x+.145, .46), (x+.145, .37))
            box(x, .24, .29, .12, name+'：拟合', '#fcf0e4')
            arrow((x+.145, .23), (.5, .15))
        box(.21, .02, .58, .12, '汇总各树预测')
        flow.set_title('重抽样本，各棵树分别训练', fontsize=20, pad=14)
        if comparison is None:
            ax.scatter(np.arange(1, len(points)+1), points, color='#4383a7', s=42,
                       label='单棵树预测', zorder=3)
            ax.axhline(mean, color='#c75c30', lw=2.5,
                       label=f'{len(points)} 棵平均：{mean:,.0f} 次')
            ax.set(xlabel='树编号', ylabel='预测租赁次数')
            ax.set_title('UCI同一天：逐树预测与平均', fontsize=20, pad=14)
        elif 'valid_dates' in comparison:
            import pandas as pd
            number = comparison['display_n']
            dates = pd.to_datetime(comparison['valid_dates'][:number])
            ax.plot(dates, comparison['valid_y'][:number], color='#7b8794',
                    marker='o', markersize=3.5, lw=1.4, alpha=.8, label='真实次数')
            for name, color, style, width in [('单树', '#447d9f', '--', 1.5),
                                             ('Bagging 10棵', '#cd6638', '-', 2.2)]:
                ax.plot(dates, comparison['valid_predictions'][name][:number],
                        color=color, linestyle=style, lw=width,
                        label=f"{name}：MAE {comparison['mae'][name]:,.0f}")
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.set(xlabel='验证日期（前30天）', ylabel='每日租赁次数')
            ax.set_title('同一验证日期：单树与10棵平均', fontsize=20, pad=14)
        else:
            ax.scatter(comparison['valid_temp'], comparison['valid_y'],
                       s=15, color='#98a4af', alpha=.45, edgecolors='none', zorder=1)
            for name, color, style, width in [('单树', '#394754', '--', 1.6),
                    ('Bagging 3棵', '#4489b8', '-', 1.4), ('Bagging 5棵', '#8462a6', '-', 1.4),
                    ('Bagging 10棵', '#cd6638', '-', 2.1)]:
                if name not in comparison['curves']:
                    continue
                ax.plot(comparison['grid_temp'], comparison['curves'][name],
                        color=color, linestyle=style, lw=width, zorder=3,
                        label=f"{name}：MAE {comparison['mae'][name]:,.0f}")
            ax.set(xlabel='气温指标 temp', ylabel='租赁次数')
            ax.set_title('单树与Bagging：相同气温的预测', fontsize=20, pad=14)
            ax.text(.02, .97, '灰点：后续120天真实记录', transform=ax.transAxes,
                    va='top', fontsize=13, color='#596b7c')
        ax.grid(axis='y', alpha=.18)
        if comparison is None:
            ax.legend(frameon=False, fontsize=13, loc='lower right', ncol=2)
        else:
            ax.legend(frameon=False, fontsize=12, loc='upper center',
                      ncol=3 if 'valid_dates' in comparison else 2,
                      bbox_to_anchor=(.5, -.24), borderaxespad=0)
        fig.subplots_adjust(left=.01, right=.99, bottom=.17, top=.85, wspace=.22)
        if comparison is not None:
            position = ax.get_position()
            ax.set_position([position.x0, position.y0+.10, position.width, position.height-.10])
        _save(fig, path)








def residual_stages(x, y, residual0, grid, h1_grid, initial, pred1_grid, path, pred1_samples):
    with _base():
        fig,axs=plt.subplots(1,3,figsize=(16,5.1),sharex=True)
        # 竖向虚线连接初始预测与真实值，长度对应残差的绝对值。
        axs[0].vlines(x, initial, y, color="#638e70", linewidth=1.9,
                      linestyles="--", alpha=.9, label="残差（竖虚线）", zorder=2)
        axs[0].scatter(x,y,s=42,color="#347da6",alpha=.78,label="真实 cnt",zorder=3)
        axs[0].axhline(initial,color="#dc7652",lw=2.3,label="初始均值 F₀")
        axs[0].set_title("① 真实 cnt 与初始 F₀");axs[0].set_ylabel("租赁次数 / 残差")
        axs[0].legend(frameon=False,fontsize=12,loc="lower right")
        axs[1].scatter(x,residual0,s=42,color="#638e70",alpha=.8,label="初始残差 r₀");axs[1].plot(grid,h1_grid,color="#dc7652",lw=2.6,label="浅树 h₁(temp)");axs[1].set_title("② r₀ 与第一棵浅树 h₁");axs[1].legend(frameon=False)
        # 使用样本处的真实模型预测作端点，不从绘图网格插值。
        axs[2].vlines(x, pred1_samples, y, color="#638e70", linewidth=1.9,
                      linestyles="--", alpha=.9, label="新残差（供下一轮拟合）", zorder=2)
        axs[2].scatter(x,y,s=42,color="#347da6",alpha=.78,label="真实 cnt",zorder=3)
        axs[2].plot(grid,pred1_grid,color="#dc7652",lw=2.6,label="F₁ = F₀ + ηh₁")
        axs[2].set_title("③ 第 1 轮累计预测 F₁")
        axs[2].legend(frameon=False,fontsize=12,loc="lower right")
        for ax in axs: ax.set_xlabel("气温指标 temp（0 到 1）");ax.grid(alpha=.16)
        fig.text(.5,.015,"散点摘自 491 天拟合段中的 6 天；曲线由全 491 天拟合的树在密集温度网格上预测",ha="center",fontsize=12)
        fig.tight_layout(rect=[0,.07,1,1]);_save(fig,path)


def boost_sum(y, show_idx, predictions, mses, path):
    with _base():
        fig,axs=plt.subplots(1,5,figsize=(20,5.8),sharex=True,sharey=True)
        ceiling=np.ceil(max(np.max(y),max(np.max(p) for p in predictions.values()))/1000)*1000
        for ax,stage in zip(axs,(0,1,5,20,40)):
            ax.plot([0,ceiling],[0,ceiling],ls="--",color="#87929d",lw=1.4,label="预测＝真实")
            ax.scatter(y[show_idx],predictions[stage][show_idx],s=38,color="#367fa7",alpha=.65,zorder=3)
            ax.set(title=f"第{stage}轮\n训练MSE={mses[stage]:,.0f}",xlabel="真实次数 cnt",
                   xlim=(0,ceiling),ylim=(0,ceiling))
            ax.set_xticks([0,3000,6000,9000]);ax.set_yticks([0,3000,6000,9000])
            ax.title.set_fontsize(16);ax.xaxis.label.set_fontsize(16);ax.tick_params(labelsize=13)
            ax.set_aspect("equal",adjustable="box");ax.grid(alpha=.16)
        axs[0].set_ylabel("预测租赁次数")
        axs[0].legend(frameon=False,fontsize=12,loc="upper left")
        fig.text(.5,.015,"同一组60天摘录；全部491天、8个特征拟合并计算训练MSE；树深度3，学习率0.5",ha="center",fontsize=12)
        fig.tight_layout(rect=[0,.14,1,1]);_save(fig,path)


def boost_prediction_slices(model, frame, features, initial, path):
    import pandas as pd
    with _base():
        # 其余六项固定为同一条真实训练记录，避免拼出不存在的日期组合。
        reference=frame.iloc[150]
        tx=np.linspace(frame.temp.min(),frame.temp.max(),130)
        hy=np.linspace(frame.hum.min(),frame.hum.max(),130)
        xx,yy=np.meshgrid(tx,hy)
        query=pd.DataFrame(np.repeat(reference[features].to_numpy()[None,:],xx.size,axis=0),columns=features).astype(float)
        query["temp"]=xx.ravel();query["hum"]=yy.ravel()
        surfaces={0:np.full(xx.size,initial)}
        for stage,pred in enumerate(model.staged_predict(query),start=1):
            if stage in (1,5,20,40):surfaces[stage]=pred
        low=min(p.min() for p in surfaces.values());high=max(p.max() for p in surfaces.values())
        fig,axs=plt.subplots(1,5,figsize=(20,5.1),sharex=True,sharey=True,layout="constrained")
        for ax,stage in zip(axs,(0,1,5,20,40)):
            img=ax.pcolormesh(xx,yy,surfaces[stage].reshape(xx.shape),cmap="YlOrRd",vmin=low,vmax=high,shading="auto",rasterized=True)
            ax.set(title=f"第{stage}轮预测分区",xlabel="气温指标 temp")
        axs[0].set_ylabel("湿度 hum")
        fig.colorbar(img,ax=axs,label="预测租赁次数",shrink=.8)
        fig.suptitle(f"八特征模型的二维切片：其余六项固定为{reference.dteday.date()}的记录",fontsize=17)
        _save(fig,path)


def boost_rates(stages, train_curves, valid_curves, rates, path):
    with _base():
        fig,axs=plt.subplots(1,2,figsize=(16,5.6),sharex=True,sharey=True)
        colors=["#347da6","#dc7652","#638e70","#9c6caf"]
        for i,(rate,tr,va,color) in enumerate(zip(rates,train_curves,valid_curves,colors)):
            ax=axs[0 if i<2 else 1]
            ax.plot(stages,np.array(tr)/1000000,lw=1.6,ls="--",color=color,alpha=.8)
            ax.plot(stages,np.array(va)/1000000,lw=2.1,color=color,label=f"η={rate:g}")
        for ax,title in zip(axs,("较小学习率：0.01、0.1","较大学习率：1.5、2")):
            ax.set(title=title,xlabel="提升轮数",ylabel="MSE（百万次²）",ylim=(0,None))
            ax.grid(alpha=.16);ax.legend(frameon=False,loc="upper right" if ax is axs[0] else "lower right")
        pick=rates.index(.1);best=int(np.argmin(valid_curves[pick]))
        axs[0].scatter(stages[best],valid_curves[pick][best]/1000000,color="#222222",s=40,zorder=5)
        axs[0].annotate(f"η=0.1验证最低\n第{stages[best]}轮",xy=(stages[best],valid_curves[pick][best]/1000000),
                        xytext=(110,3.5),fontsize=13,arrowprops={"arrowstyle":"->","color":"#555555"})
        fig.text(.5,.015,"同色为同一学习率：虚线训练、实线验证；8个特征，单树深度3；491天训练、随后120天验证。",ha="center",fontsize=12)
        fig.tight_layout(rect=[0,.085,1,1]);_save(fig,path)




def demand_tree_counts(tree, X, y, feature_names, path):
    from sklearn.tree import _tree
    t=tree.tree_; pos={}
    def place(n,d,a,b):
        if t.children_left[n]==_tree.TREE_LEAF: pos[n]=((a+b)/2,-d); return
        m=(a+b)/2; place(t.children_left[n],d+1,a,m); place(t.children_right[n],d+1,m,b); pos[n]=(m,-d)
    place(0,0,0,1); routes=tree.decision_path(X).toarray().astype(bool)
    with _base():
        fig,ax=plt.subplots(figsize=(12,5))
        for n in range(t.node_count):
            x0,y0=pos[n]; left,right=t.children_left[n],t.children_right[n]
            for child,label in ((left,"是"),(right,"否")):
                if child in pos:
                    x1,y1=pos[child]; ax.plot([x0,x1],[y0-.06,y1+.13],color="#657786",lw=1.6)
                    ax.text((x0+x1)/2,(y0+y1)/2,label,ha="center",fontsize=12)
            counts=[int(np.sum(routes[:,n]&(y==0))),int(np.sum(routes[:,n]&(y==1)))]
            if left==_tree.TREE_LEAF: label=f"叶：{sum(counts)} 天\n低/高需求 {counts}"; color="#dcebd7"
            else: label=f"{feature_names[t.feature[n]]} ≤ {t.threshold[n]:.3f}\n{int(t.n_node_samples[n])} 天"; color="#dce9f4"
            ax.text(x0,y0,label,ha="center",va="center",fontsize=16,bbox={"boxstyle":"round,pad=.5","fc":color,"ec":"#637887"},zorder=3)
        ax.set(title="浅分类树：节点中的低/高需求日计数",xlim=(-.15,1.15),ylim=(-tree.get_depth()-.55,.55)); ax.axis("off")
        fig.tight_layout(); _save(fig,path)














def criteria_comparison(x, y, models, path):
    labels = {"squared_error":"平方误差：叶子输出均值", "absolute_error":"绝对误差：叶子输出中位数", "poisson":"泊松偏差：叶子输出均值"}
    with _base():
        fig, axes = plt.subplots(1, 3, figsize=(17.8, 5.6), sharex=True, sharey=True)
        grid = np.linspace(0, 1, 1200)
        for ax, (criterion, model) in zip(axes, models.items()):
            ax.scatter(x, y, s=15, alpha=.35, color="#3579a8", edgecolors="none")
            ax.plot(grid, model.predict(grid[:, None]), color="#263746", lw=2.8)
            cuts = np.sort(model.tree_.threshold[model.tree_.feature >= 0])
            for cut, color in zip(cuts, ["#8060a8", "#c45238"]):
                ax.axvline(cut, color=color, ls="--", lw=1.9)
                ax.text(cut, 9000, f"{cut:.3f}", color=color, ha="center", fontsize=15,
                        bbox={"facecolor":"white", "edgecolor":"none", "pad":2})
            bounds = np.r_[0, cuts, 1]
            midpoints = (bounds[:-1] + bounds[1:]) / 2
            predictions = model.predict(midpoints[:, None])
            for midpoint, prediction in zip(midpoints, predictions):
                ax.text(midpoint, prediction+500, f"{prediction:,.0f}", ha="center", fontsize=14, color="#263746",
                        bbox={"facecolor":"white", "edgecolor":"none", "alpha":.8, "pad":1})
            ax.set(title=labels[criterion], xlabel="气温指标 temp", xlim=(0,1), ylim=(0,9800))
            ax.tick_params(labelsize=13)
            ax.set_xticks([0,.2,.4,.6,.8,1])
            ax.grid(alpha=.16)
        axes[0].set_ylabel("每日租赁次数 cnt")
        fig.tight_layout(w_pad=1.3)
        _save(fig, path)


def synthetic_criteria(x, y, models, path):
    labels={"squared_error":"平方误差：均值", "absolute_error":"绝对误差：中位数", "poisson":"泊松偏差：均值"}
    with _base():
        fig,axes=plt.subplots(1,3,figsize=(17.8,5.8),sharex=True,sharey=True)
        grid=np.linspace(0,1,1000)
        high=[np.argmin(abs(x-pos)) for pos in [.18,.32]]
        for ax,(criterion,model) in zip(axes,models.items()):
            ax.scatter(x,y,color="#3579a8",s=27,alpha=.65,edgecolors="white",linewidths=.3,zorder=3)
            ax.scatter(x[high],y[high],color="#d66b32",s=45,zorder=4)
            cuts=np.sort(model.tree_.threshold[model.tree_.feature>=0])
            for cut,color in zip(cuts,["#8060a8","#c45238"]):
                ax.axvline(cut,color=color,ls="--",lw=1.9)
                ax.text(cut,245,f"{cut:.3f}",color=color,ha="center",fontsize=15,
                        bbox={"facecolor":"white","edgecolor":"none","pad":2})
            ax.plot(grid,model.predict(grid[:,None]),color="#263746",lw=2.6)
            bounds=np.r_[0,cuts,1];mids=(bounds[:-1]+bounds[1:])/2
            for mid,value in zip(mids,model.predict(mids[:,None])):
                ax.text(mid,value+12,f"{value:.1f}",ha="center",fontsize=14,
                        bbox={"facecolor":"white","edgecolor":"none","alpha":.8,"pad":1})
            ax.set(title=labels[criterion],xlabel="合成特征 x",xlim=(0,1),ylim=(0,265))
            ax.set_xticks([0,.2,.4,.6,.8,1]);ax.grid(alpha=.16)
        axes[0].set_ylabel("合成目标 y（次数）")
        fig.tight_layout(w_pad=1.2);_save(fig,path)


def classification_score_flow(rows, sample, eta, first_update, path):
    with _base():
        fig,ax=plt.subplots(figsize=(8.2,6.7));ax.axis("off")
        ax.text(.5,.98,f"真实记录：{sample['date']}",ha="center",va="top",fontsize=22,transform=ax.transAxes)
        ax.text(.5,.88,f"cnt={sample['cnt']}，真实高需求 y={sample['y']}",ha="center",fontsize=18,transform=ax.transAxes)
        cells=[[str(r["round"]),"/" if r["tree_update"] is None else f"{r['tree_update']:+.4f}",f"{r['score']:+.4f}",f"{r['probability']:.4f}",str(r["predicted_class"])] for r in rows]
        table=ax.table(cellText=cells,colLabels=["轮次",r"树输出 $h_m(x)$","累计分数 F","概率 p","预测类"],cellLoc="center",bbox=[.01,.35,.98,.43],colWidths=[.10,.25,.25,.24,.16])
        table.auto_set_font_size(False);table.set_fontsize(18)
        for (ri,ci),cell in table.get_celld().items():
            cell.set_edgecolor("#d4dfe5");cell.set_facecolor("#eaf1f6" if ri==0 else "#ffffff")
            if ri>0 and ci==4:cell.set_facecolor("#fbeadf" if rows[ri-1]["predicted_class"]==1 else "#e6f1f8")
        ax.text(.5,.26,f"首棵树输出：h₁(x) = {first_update:.4f}",ha="center",fontsize=19,transform=ax.transAxes)
        ax.text(.5,.18,f"F₁：{rows[0]['score']:+.4f} + {eta:g} × {first_update:.4f} = {rows[1]['score']:+.4f}",ha="center",fontsize=18,transform=ax.transAxes)
        ax.text(.5,.07,f"概率 p ≥ {sample['threshold']:g} → 高需求；否则 → 低需求",ha="center",fontsize=16,transform=ax.transAxes)
        _save(fig,path)
