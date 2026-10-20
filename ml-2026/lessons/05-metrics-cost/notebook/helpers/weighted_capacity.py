"""只负责阈值计数与绘图；模型训练代码保留在Notebook中。"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def threshold_candidates(y, score, cost_ratio=4):
    y, score = np.asarray(y), np.asarray(score)
    order = np.argsort(-score, kind='stable')
    sorted_score = score[order]
    cumulative = np.cumsum(y[order])
    ends = np.r_[np.flatnonzero(np.diff(sorted_score) != 0), len(y)-1]
    reported = ends+1
    tp = cumulative[ends]
    fp, fn = reported-tp, y.sum()-tp
    table = pd.DataFrame(dict(threshold=sorted_score[ends], reported=reported,
                              TP=tp, FP=fp, FN=fn, cost=fp+cost_ratio*fn))
    empty = pd.DataFrame([dict(threshold=1.000001, reported=0, TP=0, FP=0,
                               FN=int(y.sum()), cost=cost_ratio*int(y.sum()))])
    return pd.concat([empty,table], ignore_index=True)

def plot_weighted_capacity(curves, topk, path):
    fig, axes = plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    colors=['#245e97','#23756c','#c05835','#8b65a8']
    for (weight, curve), color in zip(curves.items(), colors):
        axes[0].plot(curve.threshold, curve.reported, color=color,label=f'正类权重 {weight}')
    axes[0].axhline(600,color='#52657a',ls='--',label='600人上限')
    axes[0].set(xlim=(0,1),ylim=(0,6000),xlabel='分类阈值',ylabel='报出人数',title='不同类别权重下的训练输出')
    axes[0].legend(fontsize=13)
    axes[1].bar([str(w) for w in topk.weight],topk.TP,color=colors)
    for j, row in topk.iterrows():
        axes[1].text(j,row.TP+7,str(int(row.TP)),ha='center',fontsize=13)
    axes[1].set(ylim=(0,600),xlabel='正类训练权重（负类固定为1）',ylabel='前600名命中人数',title='相同600名额，比较真实命中数')
    for ax in axes:
        ax.tick_params(labelsize=13)
        ax.xaxis.label.set_size(15)
        ax.yaxis.label.set_size(15)
        ax.title.set_fontsize(15)
        ax.grid(axis='y',alpha=.15)
        ax.spines[['top','right']].set_visible(False)
    fig.savefig(path,dpi=200,facecolor='white')
    # 两张课件图分别输出，投影时不缩成双面板。
    from pathlib import Path
    for panel, ax in enumerate(axes):
        box=ax.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.dpi_scale_trans.inverted())
        fig.savefig(Path(path).with_name(['lab05-weighted-threshold.png','lab05-weighted-topk.png'][panel]),
                    dpi=200,facecolor='white',bbox_inches=box.expanded(1.03,1.04))
    plt.show()
    # 课件双图纵排使用宽画幅，避免缩成狭小的方图。
    fig, ax = plt.subplots(figsize=(8.2,3.6),layout='constrained')
    for (weight, curve), color in zip(curves.items(), colors):
        ax.plot(curve.threshold,curve.reported,color=color,lw=2,label=f'权重{weight}')
    # 标出恰好报出600人的阈值，不混同于容量内最低代价阈值。
    positions=[(.22,.28),(.47,.42),(.65,.23),(.78,.37)]
    for (weight, curve), color, position in zip(curves.items(),colors,positions):
        point=curve.loc[curve.reported==600]
        assert not point.empty, '本实验每个模型必须存在恰报600人的阈值'
        threshold=float(point.iloc[0].threshold)
        ax.scatter(threshold,600,color=color,s=45,zorder=5)
        ax.vlines(threshold,0,600,color=color,ls=':',lw=1.2)
        ax.annotate(f'权重{weight}：t≈{threshold:.3f}',(threshold,600),
                    xytext=position,textcoords='axes fraction',fontsize=11,color=color,
                    bbox=dict(fc='white',ec='none',alpha=.9,pad=1),
                    arrowprops=dict(arrowstyle='->',color=color,lw=1.2))
    ax.axhline(600,color='#52657a',ls='--',label='600人上限')
    ax.set(xlim=(0,1),ylim=(0,6000),xlabel='分类阈值',ylabel='报出人数')
    ax.set_yticks([0,600,2000,4000,6000])
    ax.legend(fontsize=11,ncol=2)
    ax.tick_params(labelsize=11)
    ax.grid(axis='y',alpha=.15)
    ax.spines[['top','right']].set_visible(False)
    fig.savefig(Path(path).with_name('lab05-weighted-threshold.png'),dpi=200,facecolor='white')
    plt.show()

def plot_weighted_rates(results, path):
    """固定0.5阈值，对比各次训练后的指标；连线只引导读图。"""
    from matplotlib.ticker import PercentFormatter
    results=results.sort_values('weight')
    positions=results.weight.to_numpy()
    fig,ax=plt.subplots(figsize=(8.2,3.6),layout='constrained')
    for field, label, color, marker in [('precision','查准率 Precision','#245e97','o'),
                                         ('recall','召回率 Recall','#c05835','s')]:
        values=results[field].to_numpy()
        ax.plot(positions,values,color=color,marker=marker,lw=2.5,ms=4,label=label)
        for x,value in zip(positions,values):
            if x not in [1,2,4,8]:
                continue
            ax.annotate(f'{value:.1%}',(x,value),xytext=(0,10 if field=='recall' else -19),
                        textcoords='offset points',ha='center',fontsize=12,color=color)
    ax.set_xticks([1,2,4,6,8])
    ax.set(xlabel='正类训练权重 Class Weight（负类固定为1）',ylabel='指标值',
           ylim=(0,1.04),xlim=(positions.min()-.25,positions.max()+.25))
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.tick_params(labelsize=12)
    ax.xaxis.label.set_size(12)
    ax.yaxis.label.set_size(13)
    ax.legend(fontsize=12,loc='center right')
    ax.grid(axis='y',alpha=.15)
    ax.spines[['top','right']].set_visible(False)
    fig.savefig(path,dpi=200,facecolor='white')
    plt.show()

def evaluate_capacities(y, scores, capacities):
    y=np.asarray(y)
    baseline=np.argsort(-scores[1],kind='stable')
    top_rows,cost_rows=[],[]
    for weight,score in sorted(scores.items()):
        order=np.argsort(-score,kind='stable')
        curve=threshold_candidates(y,score,4)
        for k in capacities:
            selected,base=order[:k],baseline[:k]
            tp,base_tp=int(y[selected].sum()),int(y[base].sum())
            gained,lost=np.setdiff1d(selected,base),np.setdiff1d(base,selected)
            overlap=len(np.intersect1d(selected,base))
            top_rows.append(dict(weight=float(weight),K=k,TP=tp,P=tp/k,R=tp/y.sum(),
                delta_TP=tp-base_tp,overlap=overlap,overlap_rate=overlap/k,
                gained_positive=int(y[gained].sum()),lost_positive=int(y[lost].sum())))
            best=curve.query('reported <= @k').sort_values(['cost','reported','threshold'],ascending=[True,True,False]).iloc[0]
            cost_rows.append(dict(weight=float(weight),K=k,**best.to_dict()))
    return pd.DataFrame(top_rows),pd.DataFrame(cost_rows)

def plot_capacity_sweep(table,path):
    fig,ax=plt.subplots(figsize=(8,4.7),layout='constrained')
    for (k,g),color,marker in zip(table.groupby('K'),['#245e97','#23756c','#c05835','#8b65a8'],['o','s','^','D']):
        ax.plot(g.weight,g.delta_TP,color=color,marker=marker,ms=4,lw=2,label=f'K={k:,}')
    ax.axhline(0,color='#52657a',ls='--')
    ax.set(xlabel='正类训练权重（负类为1）',ylabel='命中人数差：相对未加权模型')
    ax.set_xticks([1,2,4,6,8]);ax.legend(fontsize=12)
    ax.grid(axis='y',alpha=.15)
    ax.spines[['top','right']].set_visible(False)
    fig.savefig(path,dpi=200,facecolor='white');plt.show()

def plot_weighted_cost_curves(curves, path, capacity=2000):
    """固定容量和业务代价，比较各模型阈值扫描；空心圆标容量内最低点。"""
    fig,ax=plt.subplots(figsize=(8,5),layout='constrained')
    colors=['#245e97','#23756c','#c05835','#8b65a8']
    for (weight,curve),color in zip(curves.items(),colors):
        curve=curve.sort_values('threshold')
        ax.plot(curve.threshold,curve.cost,color=color,lw=1.3,ls='--',alpha=.35)
        feasible=curve.loc[curve.reported<=capacity]
        ax.plot(feasible.threshold,feasible.cost,color=color,lw=2.4,label=f'权重{weight}')
        best=feasible.sort_values(['cost','reported','threshold'],ascending=[True,True,False]).iloc[0]
        ax.scatter(best.threshold,best.cost,facecolors='none',edgecolors=color,
                   marker='o',s=45,linewidths=1.2,zorder=5)
        if weight==4:
            ax.annotate(f'权重4：t≈{best.threshold:.3f}\n{best.reported:,.0f}人，代价{best.cost:,.0f}',
                        (best.threshold,best.cost),xytext=(.5,.18),textcoords='axes fraction',
                        color=color,fontsize=12,arrowprops=dict(arrowstyle='->',color=color))
    ax.set(xlim=(0,1),ylim=(3100,3350),xlabel='分类阈值',ylabel='错误代价 FP + 4FN（局部放大）')
    ax.set_yticks([3100,3150,3200,3250,3300,3350])
    ax.text(.03,.95,f'最多{capacity:,}人；虚线超容量，实线可选',transform=ax.transAxes,fontsize=11)
    ax.legend(loc='upper right',fontsize=12)
    ax.grid(axis='y',alpha=.15)
    ax.spines[['top','right']].set_visible(False)
    fig.savefig(path,dpi=200,facecolor='white');plt.show()
