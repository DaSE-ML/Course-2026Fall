"""二维AdaBoost过程图；训练与权重更新在Notebook中。"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
from l7_bike_plots import _base, _save


def plot_rounds(raw, y, scaler, candidates, rounds, path):
    low=raw.min(axis=0)-.04; high=raw.max(axis=0)+.04
    xx,yy=np.meshgrid(np.linspace(low[0],high[0],400),np.linspace(low[1],high[1],350))
    grid=scaler.transform(np.c_[xx.ravel(),yy.ravel()]); X=scaler.transform(raw)
    predict=lambda model,z: np.where(model[2]*(z@model[0]-model[1])>=0,1,-1)
    first=predict(candidates[rounds[0]['selected']],X)
    second=predict(candidates[rounds[1]['selected']],X)
    a=int(np.flatnonzero((first!=y)&(second==y))[0])
    with _base():
        fig,axes=plt.subplots(2,3,figsize=(17,7.5),sharex=True,sharey=True)
        fill=ListedColormap(['#e6eff9','#fbeae4']); colors=np.where(y==1,'#ba543b','#2879a5')
        cumulative=np.zeros(grid.shape[0])
        for col,r in enumerate(rounds):
            model=candidates[r['selected']];score=model[2]*(grid@model[0]-model[1]);new=predict(model,X)
            cumulative+=r['alpha']*predict(model,grid)
            ax=axes[0,col];size=r['weights']*len(y)*55
            wrong=new!=y
            ax.scatter(*raw.T,s=size,c=colors,edgecolors='white',linewidths=.5,zorder=3)
            # 按直径留固定间隙，外圈随真实圆点一起变大，避免固定面积差。
            ring_size=(np.sqrt(size[wrong])+4)**2
            ax.scatter(*raw[wrong].T,s=ring_size,facecolors='none',edgecolors='#182531',linewidths=1.3,zorder=4)
            ax.contour(xx,yy,score.reshape(xx.shape),levels=[0],colors=['#7846a3'],linewidths=2)
            ax.annotate('A',xy=raw[a],xytext=(6,7),textcoords='offset points',fontsize=15,fontweight=600,zorder=5)
            ax.set_title(f"第{r['round']}轮：分类器 "+rf"$h_{{{r['round']}}}$"+"\n"+rf"$\epsilon_{{{r['round']}}}={r['error']:.3f},\quad\alpha_{{{r['round']}}}={r['alpha']:.3f}$",fontsize=17,pad=7)
            ax=axes[1,col];predgrid=np.where(cumulative>=0,1,-1).reshape(xx.shape)
            ax.contourf(xx,yy,predgrid,levels=[-2,0,2],cmap=fill)
            ax.contour(xx,yy,predgrid,levels=[0],colors=['#303846'],linewidths=1.6)
            wrong=np.where(r['ensemble_score']>=0,1,-1)!=y
            ax.scatter(*raw.T,s=27,c=colors,edgecolors='white',linewidths=.4,zorder=3)
            ax.scatter(*raw[wrong].T,s=(np.sqrt(27)+4)**2,facecolors='none',edgecolors='#182531',linewidths=1.3,zorder=4)
            combination='+'.join(rf'\alpha_{{{j}}}h_{{{j}}}' for j in range(1,r['round']+1))
            ax.set_title('$'+combination+'$'+f"（错分{wrong.sum()}/{len(y)}）",fontsize=15,pad=7)
            ax.set_xlabel('气温指标 temp',fontsize=14)
        fig.text(.018,.695,'本轮分类器',rotation=90,ha='center',va='center',fontsize=17,fontweight=600,color='#63358c')
        fig.text(.018,.30,'累计组合结果',rotation=90,ha='center',va='center',fontsize=17,fontweight=600,color='#303846')
        for row in range(2):
            axes[row,0].set_ylabel('湿度指标 hum',fontsize=14)
            for ax in axes[row]:
                ax.set_xlim(low[0],high[0]);ax.set_ylim(low[1],high[1]);ax.tick_params(labelsize=12);ax.grid(alpha=.12)
        fig.legend(handles=[Line2D([0],[0],marker='o',color='none',markerfacecolor='#2879a5',label='低需求'),Line2D([0],[0],marker='o',color='none',markerfacecolor='#ba543b',label='高需求'),Line2D([0],[0],color='#7846a3',lw=2,label='本轮新直线'),Line2D([0],[0],marker='o',color='none',markeredgecolor='#242e38',label='各图错分')],ncol=4,loc='lower center',bbox_to_anchor=(.5,.005),fontsize=14,frameon=False)
        fig.subplots_adjust(left=.095,right=.99,top=.89,bottom=.13,hspace=.22,wspace=.14)
        _save(fig,path)
