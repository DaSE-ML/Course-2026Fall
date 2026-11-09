"""第6讲三类分布变化的受控概率示意；无真实数据或模型成绩。"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from course_plot_style import course_font_settings

BLUE, ORANGE = '#2876a3', '#c87435'

def density(x, mean, std):
    values = np.exp(-.5*((x-mean)/std)**2)
    return values / np.trapezoid(values, x)

def posterior(x, threshold):
    return 1/(1+np.exp(-10*(x-threshold)))

def setup():
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 7.5))
    for ax in axes:
        ax.spines[['top','right']].set_visible(False)
        ax.grid(alpha=.14)
        ax.tick_params(labelsize=13)
    return fig, axes

def save(fig, path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fig.tight_layout(h_pad=2.1)
    fig.savefig(path, bbox_inches='tight')
    fig.savefig(path.with_suffix('.png'), dpi=260, bbox_inches='tight')
    plt.close(fig)

def pair(ax, x, old, new):
    ax.plot(x,old,color=BLUE,lw=2.5,label='参考分布')
    ax.plot(x,new,color=ORANGE,lw=2.5,ls='--',label='部署分布')
    ax.legend(frameon=False,fontsize=13)
    ax.set_xlim(0,1)

def covariate(x, old, new, risk, path):
    with plt.rc_context(course_font_settings()):
        fig,(top,bottom)=setup()
        pair(top,x,old,new)
        top.set(title='输入分布变了',xlabel='缺陷分数 X',ylabel='概率密度')
        pair(bottom,x,risk,risk)
        bottom.set(title='同一分数对应的不合格概率不变',xlabel='缺陷分数 X',ylabel='P(Y=1 | X)',ylim=(-.04,1.04))
        bottom.text(.08,.79,'实线与虚线重合',fontsize=15,color='#52657a')
        save(fig,path)

def label_shift(x, class0, class1, priors, path):
    with plt.rc_context(course_font_settings()):
        fig,(top,bottom)=setup()
        positions=np.arange(2)
        for prior,offset,color,label in zip(priors,[-.17,.17],[BLUE,ORANGE],['参考分布','部署分布']):
            bars=top.bar(positions+offset,[1-prior,prior],width=.32,color=color,label=label)
            for bar,value in zip(bars,[1-prior,prior]):
                top.text(bar.get_x()+bar.get_width()/2,value+.025,f'{value:.0%}',ha='center',fontsize=15)
        top.set_xticks(positions,['合格 Y=0','不合格 Y=1'])
        top.set(title='类别占比改变：不合格率10% → 40%',ylabel='类别概率',ylim=(0,1.15))
        top.legend(frameon=False,fontsize=13,loc='upper right')
        pair(bottom,x,class0,class0)
        bottom.plot(x,class1,color=BLUE,lw=2.5)
        bottom.plot(x,class1,color=ORANGE,lw=2.5,ls='--')
        bottom.set(title='每类内部的特征分布不变',xlabel='缺陷分数 X',ylabel='条件概率密度')
        bottom.text(.30,max(class0)+.15,'合格类',ha='center',fontsize=14)
        bottom.text(.70,max(class1)+.15,'不合格类',ha='center',fontsize=14)
        bottom.set_ylim(0,max(class0)*1.28)
        save(fig,path)

def concept(x, input_density, old_risk, new_risk, path):
    with plt.rc_context(course_font_settings()):
        fig,(top,bottom)=setup()
        pair(top,x,input_density,input_density)
        top.set(title='本示意保持输入分布不变',xlabel='缺陷分数 X',ylabel='概率密度')
        top.text(.10,max(input_density)*.82,'实线与虚线重合',fontsize=15,color='#52657a')
        pair(bottom,x,old_risk,new_risk)
        bottom.set(title='同一缺陷分数，判为不合格的概率变了',xlabel='缺陷分数 X',ylabel='P(Y=1 | X)',ylim=(-.04,1.04))
        j=int(np.argmin(abs(x-.5)))
        bottom.axvline(x[j],color='#99a8b4',lw=1,ls=':')
        bottom.scatter([x[j],x[j]],[old_risk[j],new_risk[j]],color=[BLUE,ORANGE],s=38,zorder=4)
        bottom.annotate('',xy=(x[j],new_risk[j]-.02),xytext=(x[j],old_risk[j]+.02),arrowprops={'arrowstyle':'<->','color':'#657786'})
        bottom.text(.57,.48,f'X=0.5：{old_risk[j]:.0%} → {new_risk[j]:.0%}',fontsize=14)
        save(fig,path)
