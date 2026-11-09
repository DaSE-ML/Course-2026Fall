"""随机森林：动机、递归机制与真实树深度，只绘图不隐藏模型拟合。"""
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch
from l7_bike_plots import _base, _save


def root_choices(counts, path):
    selected = ['temp', 'season', 'mnth', 'hum']
    labels = ['气温 temp', '季节 season', '月份 mnth', '湿度 hum', '其余4个特征']
    values = np.vstack([np.r_[counts.loc[selected, name].to_numpy(),
                       counts.loc[~counts.index.isin(selected), name].sum()]
                       for name in counts.columns])
    with _base():
        fig, ax = plt.subplots(figsize=(9.8, 5.7))
        positions = np.arange(len(labels))
        for offset, numbers, color, name in zip([-.18, .18], values,
                ['#5488ac', '#cf7b49'], ['全部8个候选（Bagging式）', '每节点5个候选（RF）']):
            ax.barh(positions+offset, numbers, height=.32, color=color, label=name)
            for y, number in zip(positions+offset, numbers):
                ax.text(number+.6, y, str(int(number)), va='center', fontsize=16, color='#304c64')
        ax.set_yticks(positions, labels); ax.invert_yaxis()
        ax.set(xlim=(0, 55), xlabel='50棵树中，根节点选择该特征的棵数',
               title='重抽样本之后，根节点仍可能很相似')
        ax.grid(axis='x', alpha=.15); ax.legend(frameon=False, loc='lower right', fontsize=14)
        fig.tight_layout(); _save(fig, path)


def recursive_tree(path):
    with _base():
        fig, ax = plt.subplots(figsize=(10, 6.6))
        ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
        def box(x, y, width, height, text, fill='#edf4f9', size=17):
            ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle='round,pad=.01',
                facecolor=fill, edgecolor='#50778e', linewidth=1.5))
            ax.text(x+width/2, y+height/2, text, ha='center', va='center', fontsize=size)
        def arrow(start, end):
            ax.annotate('', xy=end, xytext=start,
                arrowprops={'arrowstyle':'->', 'color':'#6c8697', 'lw':1.5})
        ax.text(.5, .985, '树1：使用自己的一份Bootstrap样本', ha='center', va='top', fontsize=21)
        box(.28, .73, .44, .15, '根节点：随机抽5个候选\n再选最佳特征与阈值')
        for center, label in [(.24, '左子节点'), (.76, '右子节点')]:
            arrow((.5, .72), (center, .60))
            box(center-.215, .43, .43, .16, label+'：重新抽5个候选\n再选本节点的最佳切分', size=16)
        for center, parent, label, fill in [(.11,.24,'停止\n叶子报均值','#fceee1'),
                (.37,.24,'继续分裂\n…','#edf4f9'), (.63,.76,'继续分裂\n…','#edf4f9'),
                (.89,.76,'停止\n叶子报均值','#fceee1')]:
            arrow((parent,.42),(center,.31))
            box(center-.10,.14,.20,.16,label,fill=fill,size=16)
        ax.text(.5,.065,'子节点分别递归，路径可以继续加深',ha='center',fontsize=18,color='#315d7a')
        ax.text(.5,.005,'其他树分别拟合，最后汇总预测',ha='center',fontsize=17,color='#697b88')
        _save(fig,path)


def depth_histogram(depths, path):
    depths = np.asarray(depths)
    values, counts = np.unique(depths, return_counts=True)
    with _base():
        fig, ax = plt.subplots(figsize=(9.3, 5.5))
        ax.bar(values, counts, width=.65, color='#4f8ba9')
        for x, y in zip(values, counts): ax.text(x, y+.25, str(int(y)), ha='center', fontsize=16)
        ax.set(xticks=values, xlabel='单棵树的实际深度', ylabel='树的数量',
               title=f'{len(depths)}棵树：实际深度为{depths.min()}至{depths.max()}')
        ax.set_ylim(0, max(counts)+2); ax.grid(axis='y', alpha=.16)
        fig.tight_layout(); _save(fig,path)


def correlation_formula(path):
    from classification_story import formula
    formula(path, [r"\mathrm{Var}(\bar T)=\sigma^2\left[\rho+\frac{1-\rho}{B}\right]"],
            width=7, height=.85, fontsize=28)


def tuning_curves(summary, path):
    """同一输入下，不同节点候选数与树数的真实验证误差。"""
    with _base():
        fig, ax = plt.subplots(figsize=(10, 6.6))
        colors = ['#487ea1', '#d18a39', '#65905b', '#ae6585']
        for (count, group), color in zip(summary.groupby('候选特征数'), colors):
            group = group.sort_values('树数')
            ax.plot(group['树数'], group['MSE均值']/1e6, marker='o', ms=6,
                    lw=2.3, color=color, label=f'{int(count)}个候选')
        ax.set_xscale('log')
        ticks = sorted(summary['树数'].unique())
        ax.set_xticks(ticks, [str(t) for t in ticks])
        ax.set(xlabel='森林树数 n_estimators（对数刻度）',
               ylabel='验证 MSE（百万次²，越低越好）', title='树数与节点候选特征数，一起比较')
        ax.grid(alpha=.18); ax.legend(title='max_features', frameon=False, ncol=2,
                                      loc='upper right', fontsize=15, title_fontsize=16)
        fig.tight_layout(); _save(fig, path)


def parameter_effects(summary, baseline, path):
    """五项单因素实验，共用误差尺度，最后一格解释实验条件。"""
    specs = [('n_estimators', 'A 树数：有限集成的波动'),
             ('max_features', 'B 候选数：随机性与单树能力'),
             ('min_samples_leaf', 'C 叶子下限：越大越平滑'),
             ('min_samples_split', 'D 切分下限：限制小节点'),
             ('max_depth', 'E 深度上限：越大越灵活')]
    with _base():
        fig, axes = plt.subplots(2, 3, figsize=(18.2, 8.2), sharey=True)
        for ax, (parameter, title) in zip(axes.flat, specs):
            values = summary[summary['参数'] == parameter].sort_values('档位')
            x = np.arange(len(values))
            ax.plot(x, values['训练均值']/1e6, 'o-', color='#3f7fa5', lw=2, ms=5, label='训练均值')
            ax.plot(x, values['验证均值']/1e6, 'o-', color='#cc783d', lw=2, ms=5, label='验证均值')
            chosen = np.flatnonzero(values['参数值'].to_numpy() == str(baseline[parameter]))
            if len(chosen):
                index = chosen[0]
                ax.scatter([index], [values.iloc[index]['验证均值']/1e6],
                           s=105, facecolors='none', edgecolors='#263e50', lw=1.6, zorder=4)
            labels = ['不限' if value == 'None' else value for value in values['参数值']]
            ax.set_xticks(x, labels)
            ax.tick_params(axis='both', labelsize=14)
            ax.set_title(title+'\n'+parameter, fontsize=18, pad=9)
            ax.grid(alpha=.18)
            ax.set_ylim(bottom=0)
        for ax in (axes[0, 0], axes[1, 0]):
            ax.set_ylabel('MSE（百万次²）', fontsize=17)
        # 所有子图共用全体数据的范围，避免先设置下限后冻结自动缩放而裁掉后续曲线。
        ceiling = summary[['训练均值', '验证均值']].to_numpy().max()/1e6*1.08
        axes[0, 0].set_ylim(0, ceiling)
        key = axes[1, 2]; key.axis('off')
        key.text(.03, .96, '怎样比较？', fontsize=21, weight=600, va='top', transform=key.transAxes)
        key.plot([.04, .18], [.79, .79], color='#3f7fa5', lw=3, transform=key.transAxes)
        key.text(.23, .79, '训练误差', fontsize=18, va='center', transform=key.transAxes)
        key.plot([.53, .67], [.79, .79], color='#cc783d', lw=3, transform=key.transAxes)
        key.text(.72, .79, '验证误差', fontsize=18, va='center', transform=key.transAxes)
        key.text(.03, .64, '每次只改一项，黑圈标出同一基准', fontsize=16, va='top', transform=key.transAxes)
        key.text(.03, .49, '基准：50棵、5候选、叶子≥5\n节点≥20才切分，深度不限',
                 fontsize=17, va='top', linespacing=1.35, transform=key.transAxes)
        key.text(.03, .18, '相同3折时序验证 × 3种子，每点9项均值\n输入始终8列；横轴按候选档位排列',
                 fontsize=15, va='top', linespacing=1.35, color='#52657a', transform=key.transAxes)
        fig.subplots_adjust(left=.055, right=.99, bottom=.07, top=.91, wspace=.22, hspace=.45)
        _save(fig, path)


def boosting_motivation(path):
    """训练组织方式示意，不替代具体残差或权重更新算法。"""
    with _base():
        fig, ax = plt.subplots(figsize=(9.8, 6.6))
        ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
        def box(x, y, width, height, label, color='#edf4f9'):
            ax.add_patch(FancyBboxPatch((x, y), width, height,
                boxstyle='round,pad=.012', facecolor=color, edgecolor='#537b94', lw=1.5))
            ax.text(x+width/2, y+height/2, label, ha='center', va='center', fontsize=19)
        def arrow(start, end):
            ax.annotate('', xy=end, xytext=start,
                        arrowprops={'arrowstyle':'->', 'color':'#648197', 'lw':1.8})
        ax.text(.5, .97, 'Bagging / RF（回归）：分别拟合，再汇总', ha='center', va='top', fontsize=22)
        for center, label in [(.17, '树1'), (.5, '树2'), (.83, '树3')]:
            box(center-.12, .72, .24, .12, label)
            arrow((center, .70), (.5, .59))
        box(.33, .46, .34, .12, '平均数值预测', '#e5eef4')
        ax.text(.5, .37, '梯度提升：按当前不足，逐轮训练', ha='center', va='top', fontsize=22)
        for x, label in [(.03, '已有预测'), (.375, '学习修正'), (.72, '更新预测')]:
            box(x, .14, .25, .13, label, '#f9eddf')
        arrow((.29, .205), (.36, .205)); arrow((.64, .205), (.705, .205))
        ax.annotate('', xy=(.15, .12), xytext=(.845, .12),
                    arrowprops={'arrowstyle':'->', 'color':'#b58051', 'lw':1.6,
                                'connectionstyle':'angle,angleA=-90,angleB=180,rad=15'})
        ax.text(.5, .018, '再次检查不足，进入下一轮', ha='center', va='bottom', fontsize=18, color='#8b623d')
        fig.subplots_adjust(left=.015, right=.985, bottom=.02, top=.99)
        _save(fig, path)
