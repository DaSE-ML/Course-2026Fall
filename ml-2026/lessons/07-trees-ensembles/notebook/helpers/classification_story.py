"""分类树教学图：只负责绘图，模型拟合保留在Notebook。"""
from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch
from l7_bike_plots import _base, _save

LOW, HIGH = '#4b8ab5', '#df8150'


def boundary_partition(model, limits):
    """读取已经拟合的树，提取各节点区域内的切分线，不重新训练。"""
    segments, depths = [], []
    def visit(node, box, depth):
        if hasattr(model, 'tree_'):
            tree = model.tree_
            column, threshold = int(tree.feature[node]), float(tree.threshold[node])
            is_leaf = column < 0
            if not is_leaf:
                left, right = int(tree.children_left[node]), int(tree.children_right[node])
        else:
            is_leaf = 'column' not in node
            if not is_leaf:
                column, threshold = node['column'], node['threshold']
                left, right = node['left'], node['right']
        if is_leaf:
            depths.append(depth)
            return
        x0, x1, y0, y1 = box
        if column == 0:
            segments.append(((threshold, threshold), (y0, y1)))
            boxes = [(x0, threshold, y0, y1), (threshold, x1, y0, y1)]
        else:
            segments.append(((x0, x1), (threshold, threshold)))
            boxes = [(x0, x1, y0, threshold), (x0, x1, threshold, y1)]
        visit(left, boxes[0], depth+1)
        visit(right, boxes[1], depth+1)
    visit(0 if hasattr(model, 'tree_') else model, limits, 0)
    return segments, max(depths), len(depths)


def criterion_boundaries(frame, labels, mesh_x, mesh_y, predictions, captions, path, trees=None, macro_f1=None):
    """同一坐标、样本与复杂度下，显示三种评分的实际分类区域。"""
    from matplotlib.colors import ListedColormap
    from matplotlib.lines import Line2D
    with _base():
        fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.5), sharex=True, sharey=True)
        for index, (ax, prediction, caption) in enumerate(zip(axes, predictions, captions)):
            ax.pcolormesh(mesh_x, mesh_y, prediction.reshape(mesh_x.shape),
                          cmap=ListedColormap(['#e4eef7', '#fae9dc']),
                          vmin=0, vmax=1, shading='auto', rasterized=True)
            if trees is not None:
                lines, depth, leaves = boundary_partition(trees[index],
                    (mesh_x.min(), mesh_x.max(), mesh_y.min(), mesh_y.max()))
                for xs, ys in lines:
                    ax.plot(xs, ys, color='#6d7783', lw=.9, linestyle=(0, (4, 3)), alpha=.8)
                name = {'信息增益 IG': 'IG', '增益率 GR（评分示范）': 'GR（示范）'}.get(caption.split('\n')[0], caption.split('\n')[0])
                caption = name + f'：深度{depth}，内部节点{len(lines)}，叶节点{leaves}'
            ax.contour(mesh_x, mesh_y, prediction.reshape(mesh_x.shape),
                       levels=[.5], colors=['#384d60'], linewidths=1.6)
            for value, color, marker in [(0, LOW, 'o'), (1, HIGH, '^')]:
                selected = np.asarray(labels) == value
                ax.scatter(frame.loc[selected, 'temp'], frame.loc[selected, 'hum'],
                           c=color, marker=marker, s=24, alpha=.65,
                           edgecolors='white', linewidths=.25)
            ax.set(title=caption, xlabel='气温指标 temp',
                   xlim=(mesh_x.min(), mesh_x.max()), ylim=(mesh_y.min(), mesh_y.max()))
            ax.tick_params(labelsize=13)
            ax.set_xticks([.1, .3, .5, .7, .9])
            ax.set_yticks([.3, .5, .7, .9])
            ax.set_title(caption, fontsize=16, pad=12)
            if macro_f1 is not None:
                ax.text(.035, .96, f'训练 Macro-F1：{macro_f1[index]:.2%}',
                        transform=ax.transAxes, va='top', fontsize=14, color='#213c53',
                        bbox={'boxstyle':'round,pad=.3','facecolor':'white','edgecolor':'#bbc9d3','alpha':.95})
        axes[0].set_ylabel('湿度指标 hum')
        legend = [Line2D([], [], marker='o', linestyle='', color=LOW, label='低需求日：cnt < 4000'),
                  Line2D([], [], marker='^', linestyle='', color=HIGH, label='高需求日：cnt ≥ 4000'),
                  Line2D([], [], color='#384d60', label='类别边界（实线）')]
        if trees is not None:
            legend.append(Line2D([], [], color='#6d7783', linestyle='--', label='节点切分（虚线）'))
        fig.legend(handles=legend, loc='lower center', ncol=len(legend), frameon=False, fontsize=13)
        fig.subplots_adjust(left=.065, right=.99, top=.84, bottom=.22, wspace=.1)
        _save(fig, path)


def demand_scatter(frame, labels, path):
    with _base():
        fig, ax = plt.subplots(figsize=(9.5, 6.3))
        for k, name, color, marker in [(0, '低需求日：cnt < 4000', LOW, 'o'),
                                       (1, '高需求日：cnt ≥ 4000', HIGH, '^')]:
            mask = np.asarray(labels) == k
            ax.scatter(frame.loc[mask, 'temp'], frame.loc[mask, 'hum'],
                       s=35, alpha=.65, c=color, marker=marker, label=name, edgecolors='none')
        ax.set(xlabel='气温指标 temp', ylabel='湿度指标 hum', title='仍是同一批记录，目标改为高 / 低需求类别')
        ax.legend(frameon=False, fontsize=14, loc='upper left')
        ax.grid(alpha=.15)
        _save(fig, path)


def error_split(path):
    with _base():
        fig, ax = plt.subplots(figsize=(9.3, 6.6))
        ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
        def box(x, y, width, counts, title):
            ax.add_patch(FancyBboxPatch((x, y), width, .25, boxstyle='round,pad=.015',
                         facecolor='#f1f6fa', edgecolor='#91aabc', linewidth=1.6))
            ax.text(x+width/2, y+.21, title, ha='center', fontsize=18)
            colors = [HIGH]*counts[0]+[LOW]*counts[1]
            count = len(colors)
            # 每个小圆点是一条带标签的训练记录。
            for i, color in enumerate(colors):
                cols = 5; row, col = divmod(i, cols)
                cx = x + width/2 + (col-(min(count, cols)-1)/2)*width*.15
                ax.scatter(cx, y+.145-row*.047, color=color, s=120)
            ax.text(x+width/2, y+.035, f'{counts[0]}高 + {counts[1]}低', ha='center', fontsize=17)
        box(.26, .68, .48, (8, 2), '切分前：10条')
        box(.035, .22, .39, (5, 0), '左组：5条')
        box(.575, .22, .39, (3, 2), '右组：5条')
        for xx in (.23, .77):
            ax.annotate('', xy=(xx, .49), xytext=(.5, .66), arrowprops={'arrowstyle':'->','color':'#637b8e','lw':2})
        ax.text(.5, .565, '假设某个输入特征条件产生这次切分', ha='center', fontsize=15,
                bbox={'facecolor':'white','edgecolor':'none','pad':4})
        ax.text(.5, .97, '只数错分条数，会漏掉什么？', fontsize=22, ha='center', weight=600)
        ax.text(.5, .12, '前后都预测高需求：仍错2条，错分率仍为20%', ha='center', fontsize=19)
        ax.text(.5, .035, '但高需求比例已从80%变为：左组100%，右组60%', ha='center', fontsize=17, color='#385c79')
        _save(fig, path)


def gini_curve(path):
    with _base():
        fig, ax = plt.subplots(figsize=(8.7, 5.5))
        p = np.linspace(0, 1, 301)
        ax.plot(p, 2*p*(1-p), color=LOW, lw=3)
        for xx, yy, text, pos in [(0,0,'全为低需求：0',(.04,.065)),
                                  (.5,.5,'各半：0.5',(.32,.535)),
                                  (.8,.32,'80%高需求：0.32',(.59,.39)),
                                  (1,0,'全为高需求：0',(.64,.065))]:
            ax.scatter(xx, yy, color=HIGH, s=60, zorder=3)
            ax.annotate(text, (xx,yy), xytext=pos, fontsize=15,
                        arrowprops={'arrowstyle':'-','color':'#8da1ad'})
        ax.set(xlim=(-.025,1.025), ylim=(-.025,.59), xlabel='节点内高需求比例 p',
               ylabel='Gini 不纯度', title='两类越混杂，Gini越大')
        ax.grid(alpha=.15)
        _save(fig, path)


def formula(path, lines, width=10, height=2.0, fontsize=25, usetex=False, bold=False):
    import matplotlib
    with _base(), matplotlib.rc_context({"mathtext.fontset": "stix", "text.usetex": usetex,
                                            "text.latex.preamble": "",
                                            **({"font.family": "serif", "font.serif": ["Computer Modern Roman"]} if usetex else {})}):
        fig = plt.figure(figsize=(width, height))
        for i, line in enumerate(lines):
            expression = (r'\displaystyle ' if usetex else '') + line
            prefix = r'\boldmath ' if usetex and bold else ''
            fig.text(.025, 1-(i+.65)/len(lines), prefix+'$'+expression+'$', fontsize=fontsize, color='#173e67', va='center')
        _save(fig, path)


def sampling_pairs(path):
    """父节点8高2低，独立有放回抽两次，突出两种异类顺序。"""
    with _base():
        fig, ax = plt.subplots(figsize=(9.5, 6.8))
        ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
        def box(x, y, w, h, text, fill='#edf4f9', edge='#8aa6bb', size=17):
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=.012',
                         facecolor=fill, edgecolor=edge, linewidth=1.5))
            ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=size)
        def arrow(start, end, label, loc):
            ax.annotate('', xy=end, xytext=start,
                        arrowprops={'arrowstyle':'->','color':'#688297','lw':1.8})
            ax.text(*loc, label, ha='center', va='center', fontsize=15,
                    bbox={'facecolor':'white','edgecolor':'none','pad':2})
        ax.text(.5, .985, '每次抽出1条，放回后再抽1条', ha='center', va='top', fontsize=22)
        box(.28, .75, .44, .13, '父节点：8高 + 2低\n每次高0.8、低0.2',size=18)
        box(.09, .47, .29, .12, '第一次：高需求', fill='#fcf0e7')
        box(.62, .47, .29, .12, '第一次：低需求')
        arrow((.43,.74),(.235,.60),'0.8',(.30,.68))
        arrow((.57,.74),(.765,.60),'0.2',(.70,.68))
        outcomes=[(.025,'高 → 高\n0.8 × 0.8 = 0.64',False),
                  (.275,'高 → 低\n0.8 × 0.2 = 0.16',True),
                  (.525,'低 → 高\n0.2 × 0.8 = 0.16',True),
                  (.775,'低 → 低\n0.2 × 0.2 = 0.04',False)]
        for i,(x,text,different) in enumerate(outcomes):
            box(x,.16,.20,.17,text,fill='#e9f4e9' if different else '#f3f5f7',
                edge='#5d9462' if different else '#9aaab5',size=14)
            ax.text(x+.1,.115,'异类' if different else '同类',ha='center',fontsize=17,
                    color='#347542' if different else '#667988')
            parent=.235 if i<2 else .765
            prob=.8 if i%2==0 else .2
            arrow((parent,.46),(x+.1,.34),f'{prob:.1f}',((parent+x+.1)/2,.395))
        ax.text(.5,.035,'两种异类顺序相加：0.16 + 0.16 = 0.32',ha='center',fontsize=19,color='#347542')
        _save(fig,path)


def sampling_nodes(path):
    """沿用p14的圆点，把父节点及两个子节点的异类概率并排对照。"""
    with _base():
        fig, ax = plt.subplots(figsize=(9.5, 6.8))
        ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
        def node(x, y, w, high, low, title, score):
            ax.add_patch(FancyBboxPatch((x, y), w, .30, boxstyle='round,pad=.014',
                         facecolor='#f1f6fa', edgecolor='#91aabc', linewidth=1.6))
            ax.text(x+w/2, y+.255, title, ha='center', fontsize=18)
            colors = [HIGH]*high + [LOW]*low
            for i, color in enumerate(colors):
                row, col = divmod(i, 5)
                cx = x + w/2 + (col-(min(len(colors), 5)-1)/2)*w*.16
                ax.scatter(cx, y+.195-row*.055, color=color, s=125, zorder=3)
            count_y = y+.08 if len(colors)>5 else y+.115
            ax.text(x+w/2, count_y, f'{high}高 + {low}低', ha='center', fontsize=17)
            ax.text(x+w/2, y+.025, f'异类概率：{score:.2f}', ha='center', fontsize=17,
                    color='#316d45' if score==0 else '#254d70')
        ax.text(.5, .975, '每个节点内分别抽两次，比较标签', ha='center', fontsize=22)
        node(.26, .60, .48, 8, 2, '父节点：10条', .32)
        node(.035, .16, .40, 5, 0, '左子节点：5条', 0)
        node(.565, .16, .40, 3, 2, '右子节点：5条', .48)
        for xx in (.235, .765):
            ax.annotate('', xy=(xx,.475), xytext=(.5,.58),
                        arrowprops={'arrowstyle':'->','color':'#637b8e','lw':2})
        ax.text(.5,.52,'同一次特征条件切分',ha='center',fontsize=15,
                bbox={'facecolor':'white','edgecolor':'none','pad':4})
        ax.text(.5,.055,'按人数加权：0.5 × 0 + 0.5 × 0.48 = 0.24',
                ha='center',fontsize=19,color='#316d45')
        _save(fig,path)


def class_split_trees(cases, parent_counts, path):
    """两个候选各画一棵深度1的树；节点内标明真实类别计数及Gini。"""
    def impurity(counts):
        proportions = np.asarray(counts, dtype=float) / sum(counts)
        return float(1 - np.sum(proportions**2))
    parent_gini = impurity(parent_counts)
    with _base():
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        fig.subplots_adjust(left=.025, right=.975, top=.97, bottom=.025, hspace=.17)
        for ax, case in zip(axes, cases):
            ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
            left, right = case['class_counts_low_high']
            weighted = (sum(left)*impurity(left)+sum(right)*impurity(right))/sum(parent_counts)
            gain = parent_gini-weighted
            feature, threshold = case['feature'], case['threshold']
            title = 'A：气温条件（模型实际选择）' if feature=='temp' else 'B：湿度条件（人工对照）'
            ax.text(.5,.98,title,ha='center',va='top',fontsize=21)
            def node(x, y, width, height, text, fill):
                ax.add_patch(FancyBboxPatch((x,y),width,height,boxstyle='round,pad=.012',
                             facecolor=fill,edgecolor='#8ba0af',linewidth=1.5))
                ax.text(x+width/2,y+height/2,text,ha='center',va='center',fontsize=18,linespacing=1.35)
            root_text=f'{feature} ≤ {threshold:.3f}？\n低{parent_counts[0]} / 高{parent_counts[1]}（{sum(parent_counts)}天）\nGini = {parent_gini:.4f}'
            node(.25,.59,.50,.29,root_text,'#eef3f7')
            for x, counts, name in [(.025,left,'左'),(.555,right,'右')]:
                color = '#e7f1f8' if counts[0]>=counts[1] else '#fcf0e7'
                node(x,.13,.42,.29,
                     f'{name}：{sum(counts)}天\n低{counts[0]} / 高{counts[1]}\nGini = {impurity(counts):.4f}',color)
                cx=x+.21
                ax.annotate('',xy=(cx,.435),xytext=(.5,.575),
                            arrowprops={'arrowstyle':'->','color':'#688297','lw':1.7})
                ax.text((.5+cx)/2,.505,'是（≤）' if name=='左' else '否（>）',ha='center',fontsize=16,
                        bbox={'facecolor':'white','edgecolor':'none','pad':2})
            ax.text(.5,.035,f'子节点加权Gini = {weighted:.4f}；分裂收益 = {gain:.4f}',
                    ha='center',va='center',fontsize=18,
                    color='#347542' if feature=='temp' else '#596d7c')
        _save(fig,path)


def gini_search(candidate_table, features, path):
    """共同纵轴画出两个输入特征的全部合法阈值及其分裂收益。"""
    with _base():
        fig, axes = plt.subplots(2, 1, figsize=(9.8, 7.3), sharey=True)
        fig.subplots_adjust(hspace=.64, left=.13, right=.96, top=.92, bottom=.09)
        for ax, feature in zip(axes, features):
            rows = candidate_table[candidate_table['feature']==feature].sort_values('threshold')
            best = rows.loc[rows['gain'].idxmax()]
            ax.plot(rows.threshold, rows.gain, color=LOW, lw=1.5, marker='.', markersize=2)
            ax.scatter(best.threshold, best.gain, color=HIGH, s=80, zorder=3)
            ax.annotate(f'最佳阈值 {best.threshold:.7f}\n收益 {best.gain:.4f}',
                        xy=(best.threshold,best.gain),xytext=(.57,.74),textcoords='axes fraction',
                        fontsize=15,bbox={'facecolor':'white','edgecolor':'none','alpha':.9},
                        arrowprops={'arrowstyle':'->','color':'#8a6c53'})
            ax.set(xlabel=f'{feature} 候选阈值',ylabel='Gini下降量',ylim=(-.004,.205))
            ax.set_title(f'{feature}：{len(rows)}个合法候选',fontsize=20)
            ax.grid(alpha=.16)
        _save(fig,path)


def demand_tree_depth3(tree, X, labels, feature_names, path, example):
    """实际分类树，按叶子顺序布置节点，突出示例输入的真实预测路径。"""
    from sklearn.tree import _tree
    t=tree.tree_; positions={}; leaf_order=[]
    def place(node, depth):
        if t.children_left[node]==_tree.TREE_LEAF:
            positions[node]=(len(leaf_order),-depth); leaf_order.append(node)
        else:
            left,right=t.children_left[node],t.children_right[node]
            place(left,depth+1); place(right,depth+1)
            positions[node]=((positions[left][0]+positions[right][0])/2,-depth)
    place(0,0)
    routes=tree.decision_path(X).toarray().astype(bool)
    selected_path=tree.decision_path(example).indices.tolist()
    selected=set(selected_path)
    edge_steps={(a,b):str(i) for i,(a,b) in enumerate(zip(selected_path,selected_path[1:]),1)}
    target_leaf=int(tree.apply(example)[0])
    high_probability=float(tree.predict_proba(example)[0,list(tree.classes_).index(1)])
    with _base():
        fig,ax=plt.subplots(figsize=(12.8,7.1))
        for node in range(t.node_count):
            x,y=positions[node]
            for child,branch in [(t.children_left[node],'是'),(t.children_right[node],'否')]:
                if child==_tree.TREE_LEAF:continue
                xx,yy=positions[child]; active=node in selected and child in selected
                color='#d66b30' if active else '#91a1ae'
                ax.annotate('',xy=(xx,yy+(.34 if child==target_leaf else .22)),xytext=(x,y-.22),
                            arrowprops={'arrowstyle':'->','color':color,'lw':2.8 if active else 1.5},zorder=1)
                ax.text((x+xx)/2,(y+yy)/2,(edge_steps[(node,child)]+' '+branch) if active else branch,ha='center',va='center',fontsize=16,
                        color=color,bbox={'facecolor':'white','edgecolor':'none','pad':1},zorder=2)
            counts=[int(np.sum(routes[:,node] & (np.asarray(labels)==k))) for k in (0,1)]
            leaf=t.children_left[node]==_tree.TREE_LEAF
            if leaf:
                text=f'低 / 高\n{counts[0]} / {counts[1]}'
                fill='#e6f0e2'
            else:
                text=f'{feature_names[t.feature[node]]} ≤ {t.threshold[node]:.3f}\n{sum(counts)}天'
                fill='#e4eef7'
            if node in selected:fill='#fff0df'
            if node==target_leaf:
                text=f'低{counts[0]} / 高{counts[1]}\n高需求概率 {high_probability:.1%}\n预测：高需求'
            ax.text(x,y,text,ha='center',va='center',fontsize=17 if node==target_leaf else 20,linespacing=1.2,
                    bbox={'boxstyle':'round,pad=.32','facecolor':fill,
                          'edgecolor':'#d66b30' if node in selected else '#91a1ae',
                          'linewidth':2 if node in selected else 1.2},zorder=3)
        # 用矢量五角星标出落点，避免系统缺少彩色 emoji 字体。
        tx,ty=positions[target_leaf]
        ax.scatter([tx],[ty-.43],marker='*',s=420,c='#f5bc36',edgecolors='#a76b14',linewidths=1.2,zorder=5)
        ax.set(xlim=(-.6,len(leaf_order)-.4),ylim=(-tree.get_depth()-.65,.62),
               title=f'Gini分类树：深度{tree.get_depth()}，{tree.get_n_leaves()}个叶节点')
        ax.axis('off');fig.tight_layout(pad=.6)
        _save(fig,path)



def class_entropy(proportions):
    """节点经验类别分布的熵，使用以2为底的对数；零概率项贡献为0。"""
    positive=np.asarray(proportions,dtype=float)
    positive=positive[positive>0]
    return max(0.0, float(-np.sum(positive*np.log2(positive))))


def entropy_intro(path):
    """先看同类/混合点图，再看二分类熵随类别比例变化。"""
    with _base():
        fig=plt.figure(figsize=(9.3,7.1))
        dots=fig.add_axes([.04,.68,.92,.27]);dots.set(xlim=(0,3),ylim=(0,1));dots.axis('off')
        for j,high in enumerate([10,9,5]):
            dots.text(j+.5,.98,f'{high}高 / {10-high}低',ha='center',va='top',fontsize=19)
            for i in range(10):
                row,col=divmod(i,5)
                dots.scatter(j+.18+col*.16,.63-row*.23,s=135,color=HIGH if i<high else LOW)
            h=class_entropy([high/10,1-high/10])
            dots.text(j+.5,.06,f'H = {h:.3f}',ha='center',fontsize=18,color='#173e67')
        ax=fig.add_axes([.12,.14,.82,.46])
        p=np.linspace(0,1,401)
        h=np.array([class_entropy([v,1-v]) for v in p])
        ax.plot(p,h,color=LOW,lw=3)
        for x,label,xy in [(0,'全为低需求',(0.03,.10)),(.5,'各半：最不确定',(.40,1.10)),
                            (.9,'90%高需求',(.58,.57)),(1,'全为高需求',(.74,.10))]:
            y=class_entropy([x,1-x]);ax.scatter(x,y,c=HIGH,s=65,zorder=3)
            ax.annotate(label,(x,y),xytext=xy,fontsize=15,arrowprops={'arrowstyle':'-','color':'#8da1ad'})
        ax.set(xlim=(-.025,1.025),ylim=(-.035,1.20),xlabel='节点内高需求比例 p',ylabel='熵 H（bit）')
        ax.grid(alpha=.15)
        _save(fig,path)


def entropy_split(path):
    """沿用8高2低构造例子，计算人数加权子熵与信息增益。"""
    parent=class_entropy([.8,.2]);right=class_entropy([.6,.4]);after=.5*right
    with _base():
        fig,ax=plt.subplots(figsize=(9.3,6.3))
        ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
        def node(cx,y,high,low,title,width=.4):
            ax.add_patch(FancyBboxPatch((cx-width/2,y),width,.27,boxstyle='round,pad=.012',
                         facecolor='#edf4f9',edgecolor='#8aa6bb',linewidth=1.5))
            ax.text(cx,y+.225,title,ha='center',fontsize=18)
            for i in range(high+low):
                row,col=divmod(i,5)
                ax.scatter(cx+(col-2)*.045,y+.155-row*.057,s=105,color=HIGH if i<high else LOW)
            h=class_entropy([high/(high+low),low/(high+low)])
            ax.text(cx,y+.025,f'{high}高{low}低；H = {h:.3f}',ha='center',fontsize=17)
        node(.5,.67,8,2,'父节点：10条',width=.45)
        node(.24,.23,5,0,'左节点：5条')
        node(.76,.23,3,2,'右节点：5条')
        for x in [.24,.76]:
            ax.annotate('',xy=(x,.52),xytext=(.5,.65),arrowprops={'arrowstyle':'->','color':'#637b8e','lw':2})
        ax.text(.5,.57,'同一个特征条件切分，改用熵来评分',ha='center',fontsize=15,
                bbox={'facecolor':'white','edgecolor':'none','pad':3})
        ax.text(.5,.12,f'切分后：5/10 × 0 + 5/10 × {right:.4f} ≈ {after:.4f}',ha='center',fontsize=19)
        ax.text(.5,.025,f'信息增益：{parent:.4f} − {after:.4f} ≈ {parent-after:.4f}',ha='center',fontsize=21,color='#173e67')
        _save(fig,path)



def gain_ratio_example(path):
    """构造10天的同一批记录：天气有用，唯一编号可记忆训练标签。"""
    parent=class_entropy([.8,.2])
    weather_gain=parent-.4*class_entropy([.5,.5])
    weather_split=class_entropy([.6,.4])
    id_split=np.log2(10)
    with _base():
        fig,ax=plt.subplots(figsize=(10,7.3))
        ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
        ax.text(.5,.955,'按天气：分成2组',ha='center',fontsize=20,color='#173e67')
        for cx,high,low,name in [(.26,6,0,'晴天：6条'),(.74,2,2,'雨天：4条')]:
            ax.add_patch(FancyBboxPatch((cx-.21,.70),.42,.19,boxstyle='round,pad=.012',
                         facecolor='#edf4f9',edgecolor='#8aa6bb',linewidth=1.5))
            ax.text(cx,.85,name,ha='center',fontsize=18)
            for i in range(high+low):
                ax.scatter(cx+(i-(high+low-1)/2)*.05,.795,s=110,c=HIGH if i<high else LOW)
            ax.text(cx,.735,f'{high}高 / {low}低',ha='center',fontsize=17)
        ax.text(.5,.635,f'信息增益 {weather_gain:.3f}；分裂信息 {weather_split:.3f}',ha='center',fontsize=18)
        ax.text(.5,.56,f'增益率 {weather_gain/weather_split:.3f}',ha='center',fontsize=21,color='#173e67',weight=600)
        ax.plot([.02,.98],[.505,.505],color='#d9e2ea',lw=1)
        ax.text(.5,.435,'按唯一编号：分成10组，每组只有1条',ha='center',fontsize=20,color='#173e67')
        for i in range(10):
            x=.065+i*.097
            ax.add_patch(FancyBboxPatch((x-.035,.27),.07,.10,boxstyle='round,pad=.005',
                         facecolor='#f5f8fb',edgecolor='#9eafbc',linewidth=1))
            ax.scatter(x,.33,s=95,c=HIGH if i<8 else LOW)
            ax.text(x,.286,f'{i+1:02d}',ha='center',fontsize=13)
        ax.text(.5,.20,f'信息增益 {parent:.3f}；分裂信息 {id_split:.3f}',ha='center',fontsize=18)
        ax.text(.5,.125,f'增益率 {parent/id_split:.3f}',ha='center',fontsize=21,color='#173e67',weight=600)
        ax.text(.5,.035,'只比较增益率：天气评分更高',ha='center',fontsize=18)
        _save(fig,path)
