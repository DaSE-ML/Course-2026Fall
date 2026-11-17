"""Lesson08 绘图与序列化；不训练模型，不跨章导入。"""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import patheffects
from IPython.display import display
from .l8_plot_style import chinese_plot, course_font_settings

COLORS = ['#2476ad', '#d65b30']
BG = ListedColormap(['#e5f1f8', '#fcece4'])
ASSETS = Path(__file__).resolve().parents[2] / 'assets'
MANIFEST = {}


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def write_results(results):
    (ASSETS / 'l8-results.json').write_text(
        json.dumps(plain(results), ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def save(fig, name):
    ASSETS.mkdir(exist_ok=True)
    fig.savefig(ASSETS / f'{name}.svg', bbox_inches='tight')
    fig.savefig(ASSETS / f'{name}.png', dpi=240, bbox_inches='tight')
    MANIFEST[name] = {'svg': f'{name}.svg', 'png': f'{name}.png',
                      'png_dpi': 240, 'svg_fonttype': 'path'}
    display(fig)
    plt.close(fig)


def limits(X):
    lo, hi = X.min(axis=0), X.max(axis=0)
    pad = np.maximum((hi - lo) * .16, (hi - lo).max() * .08)
    return lo - pad, hi + pad


def mesh(X):
    lo, hi = limits(X)
    xx, yy = np.meshgrid(np.linspace(lo[0], hi[0], 240),
                         np.linspace(lo[1], hi[1], 220))
    return xx, yy, np.c_[xx.ravel(), yy.ravel()]


def points(ax, X, y, numbered=False, removed=None):
    active = np.ones(len(X), dtype=bool)
    if removed is not None:
        active[removed] = False
    for k, marker in [(0, 'o'), (1, '^')]:
        ax.scatter(*X[(y == k) & active].T, c=COLORS[k], marker=marker, s=58 if len(X)<25 else 23,
                   edgecolors='white', linewidths=.7, zorder=4, label=f'类别 {k}')
    if numbered:
        offsets = {4:(-13,-14), 5:(-18,-8), 7:(5,10), 10:(8,8), 11:(-14,4)}
        for i, xy in enumerate(X):
            if not active[i]:
                continue
            ax.annotate(str(i + 1), xy, xytext=offsets.get(i,(5,5)), textcoords='offset points',
                        fontsize=11, zorder=6)
    if removed is not None:
        ax.scatter(*X[removed], marker='x', c='#92979c', s=65, zorder=8)
        ax.annotate(f'移除 #{removed+1}', X[removed], xytext=(8,-24),
                    textcoords='offset points', fontsize=12, color='#666666')
    lo, hi = limits(X)
    ax.set_aspect('equal', adjustable='box')
    ax.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), xlabel='$x_1$', ylabel='$x_2$')
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=12)


def boundary(ax, X, y, model, title, support=None, transform=None, numbered=False, removed=None, mark_errors=True, show_levels=True, color_margins=False):
    xx, yy, grid = mesh(X)
    z = model.decision_function(grid if transform is None else transform(grid)).reshape(xx.shape)
    ax.contourf(xx, yy, z > 0, levels=[-.5, .5, 1.5], cmap=BG, alpha=.85)
    margin_colors = ('#176483', '#8b3d70') if color_margins else ('#657a86', '#657a86')
    colors = [margin_colors[0], '#253f4e', margin_colors[1]] if show_levels else ['#657a86']
    ax.contour(xx, yy, z, levels=[-1, 0, 1] if show_levels else [0], colors=colors,
               linestyles=['--', '-', '--'] if show_levels else 'solid',
               linewidths=[1.1, 1.8, 1.1] if show_levels else 1.8)
    points(ax, X, y, numbered, removed)
    if support is None and hasattr(model, 'support_'):
        support = model.support_
    if support is not None and len(support):
        ax.scatter(*X[np.asarray(support)].T, s=175 if len(X)<25 else 64, facecolors='none',
                   edgecolors='#273847', linewidths=1.2 if len(X)<25 else .8, zorder=5)
    pred = model.predict(X if transform is None else transform(X))
    wrong = (pred != y) & mark_errors
    if removed is not None:
        wrong[removed] = False
    ax.scatter(*X[wrong].T, marker='x', c='#151515', s=92 if len(X)<25 else 45, linewidths=1.8 if len(X)<25 else 1.1, zorder=7)
    ax.set_title(title, fontsize=16, pad=12)


@chinese_plot
def candidate_plot(X, y, rows):
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.1), layout='compressed')
    feet = []
    for ax, row in zip(axes, rows):
        points(ax, X, y, numbered=True)
        w, b = np.array(row['w']), row['b']
        xx, yy, grid = mesh(X)
        field = (grid @ w + b).reshape(xx.shape)
        ax.contour(xx, yy, field, levels=[0], colors='#243f50')
        scores = X @ w + b
        distances = np.abs(scores) / np.linalg.norm(w)
        for k, color in enumerate(COLORS):
            nearest = (y == k) & np.isclose(distances, distances[y == k].min())
            ax.contour(xx, yy, field, levels=[scores[nearest][0]], colors=[color],
                       linestyles='dashed', linewidths=1.4)
            for point, score in zip(X[nearest], scores[nearest]):
                foot = point - score * w / (w @ w)
                feet.append(foot)
                ax.plot(*np.array([point, foot]).T, color=color, linewidth=2.3)
                ax.scatter(*point, s=125, facecolors='none', edgecolors=color, zorder=5)
        ax.set_title(f"{row['name']}\n两侧距离取较小值：{row['min_distance']:.3f}", fontsize=16)
    # 三幅图使用相同范围，并包含两侧的垂足。
    lo, hi = limits(np.vstack([X, feet]))
    for ax in axes:
        ax.set(xlim=(lo[0],hi[0]), ylim=(lo[1],hi[1]))
    save(fig, 'l8-candidate-lines')


@chinese_plot
def margin_plot(X, y, model):
    fig, ax = plt.subplots(figsize=(10.3, 6.5), layout='compressed')
    boundary(ax, X, y, model, '', numbered=True)
    ax.collections[1].set_linewidth([2.2, 3.0, 2.2])
    for number in ax.texts:
        number.set_fontsize(15)
    ax.tick_params(labelsize=16)
    ax.xaxis.label.set_size(20)
    ax.yaxis.label.set_size(20)
    w, b = model.coef_[0], model.intercept_[0]
    top = ax.get_ylim()[1]
    for level, label in [(-1, r'$f=-1$'), (0, r'$f=0$'), (1, r'$f=+1$')]:
        x = (level - b - w[1] * top) / w[0]
        ax.annotate(label, (x, top), xytext=(0, 5), textcoords='offset points',
                    ha='center', va='bottom', fontsize=22, color='#253f4e')
    n = w / np.linalg.norm(w)
    half = 1 / np.linalg.norm(w)
    # 选择避开点群的切向位置，在相同直线之间标垂距。
    tangent = np.array([-n[1], n[0]])
    step = np.ptp(X, axis=0).min() * .3
    center = X.mean(axis=0) - (w @ X.mean(axis=0) + b) * w / (w @ w) - step * tangent
    color = '#7048a0'
    label_box = {'boxstyle': 'round,pad=0.12', 'facecolor': 'white', 'edgecolor': 'none'}
    end = center + half * n
    ax.annotate('', end, center, arrowprops={'arrowstyle': '->', 'color': color, 'lw': 3})
    left_end = center - half * n
    ax.annotate('', left_end, center, arrowprops={'arrowstyle': '->', 'color': color, 'lw': 3})
    ax.annotate(fr'$t_-=-{half:.3f}$', (center + left_end) / 2, xytext=(-13, 18),
                textcoords='offset points', ha='center', color=color, fontsize=21, bbox=label_box)
    ax.annotate(r'$-u$', (center + left_end) / 2, xytext=(0, -25),
                textcoords='offset points', ha='center', color=color, fontsize=18)
    ax.scatter(*center, color=color, s=24, zorder=6)
    ax.annotate(r'$\mathbf{x}_0$', center, xytext=(0, -34), textcoords='offset points',
                ha='center', color=color, fontsize=22, zorder=8,
                bbox={'boxstyle': 'round,pad=0.16', 'facecolor': 'white', 'edgecolor': 'none'})
    ax.annotate(fr'$t_+={half:.3f}$', (center + end) / 2, xytext=(13, 18),
                textcoords='offset points', ha='center', color=color, fontsize=21, bbox=label_box)
    ax.annotate(r'$u$', (center + end) / 2, xytext=(0, -25),
                textcoords='offset points', ha='center', color=color, fontsize=18)
    # 两点沿分界线移动，分数都保持为零。
    for point, label in [(center + 1.15 * step * tangent, r'$\mathbf{x}_1$'),
                         (center + .55 * step * tangent, r'$\mathbf{x}_2$')]:
        ax.scatter(*point, color='#253f4e', s=30, zorder=6)
        ax.annotate(label, point, xytext=(-12, 0), textcoords='offset points',
                    ha='right', va='center', fontsize=20, color='#253f4e', bbox=label_box)
    wide_center = center + 1.85 * step * tangent
    ax.annotate('', wide_center + half * n, wide_center - half * n,
                arrowprops={'arrowstyle': '<->', 'color': 'black', 'lw': 3})
    ax.annotate(fr'$d=t_+ - t_- \approx {2 * half:.3f}$', wide_center, xytext=(0, 16),
                textcoords='offset points', ha='center', fontsize=21, color="black", bbox=label_box)
    save(fig, 'l8-margin')


@chinese_plot
def panels(name, X, y, models, titles, supports=None, transforms=None, shape=None, numbered=False, removed=None, mark_errors=True, show_levels=True, validation_scores=None):
    if shape is None:
        shape = (1, len(models))
    rows, cols = shape
    matrix = name == 'l8-c-gamma-grid'
    fig, axes = plt.subplots(rows, cols, figsize=(5.5 * cols, 3.3 * rows if matrix else 4.9 * rows),
                             layout='compressed', squeeze=False)
    for i, (ax, model, title) in enumerate(zip(axes.flat, models, titles)):
        boundary(ax, X, y, model, title,
                 None if supports is None else supports[i],
                 None if transforms is None else transforms[i], numbered,
                 None if removed is None else removed[i], mark_errors, show_levels,
                 color_margins=name == "l8-gamma-sweep")
        if name in ('l8-c-sweep', 'l8-gamma-sweep'):
            ax.set_xlabel(r'$x_1$', labelpad=-4 if name == 'l8-gamma-sweep' else -1)
        if matrix:
            # 九联图用行列标题表达参数，避免重复小字挤占图面。
            row, col = divmod(i, cols)
            ax.set_title(f'gamma = {[.01, 1, 10][col]:g}' if row == 0 else '', fontsize=24, pad=12)
            ax.set_xlabel('')
            ax.set_ylabel(f'C = {[.1, 1, 10][row]:g}' if col == 0 else '', fontsize=24, labelpad=12)
            ax.set_xticks([]); ax.set_yticks([])
            accuracy = model.score(X, y)
            score_label = f'训练 {accuracy:.1%}'
            if validation_scores is not None:
                score_label += f'\n验证 {validation_scores[i]:.1%}'
            ax.text(.98, .035, score_label, transform=ax.transAxes, ha='right',
                    fontsize=17, color='#192b41', bbox={'facecolor':'white', 'alpha':.85, 'edgecolor':'none', 'pad':2})
    if not show_levels:
        for ax in axes.flat:
            ax.set(xlabel='左右不对称度', ylabel='上部笔迹强度')
        axes.flat[0].legend(frameon=False, labels=['数字 1', '数字 7'])
    if name == 'l8-gamma-sweep':
        from matplotlib.lines import Line2D

        fig.legend(handles=[
            Line2D([], [], color='#253f4e', label=r'分类边界 $f(x)=0$'),
            Line2D([], [], color='#176483', linestyle='--', label=r'间隔线 $f(x)=-1$'),
            Line2D([], [], color='#8b3d70', linestyle='--', label=r'间隔线 $f(x)=+1$'),
        ], loc='outside upper center', ncol=3, frameon=False, fontsize=15)
    save(fig, name)


@chinese_plot
def noise_plot(X, y, Xn, yn, clean, noisy):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.3), layout='compressed')
    boundary(axes[0], X, y, clean, '原 16 点：训练可分', numbered=True)
    boundary(axes[1], Xn, yn, noisy, '新增 #17：与 #1 同位置、标签相反', numbered=False)
    offsets = {4:(-13,-14), 5:(-18,-8), 7:(5,10), 10:(8,8), 11:(-14,4)}
    for i, p in enumerate(X):
        if i:
            axes[1].annotate(str(i + 1), p, xytext=offsets.get(i,(5,5)), textcoords='offset points', fontsize=11)
    axes[1].scatter(*Xn[-1], s=290, facecolors='none', edgecolors='#784ca3', lw=2.3, zorder=8)
    axes[1].annotate('#1 / #17 冲突', Xn[-1], xytext=(-135, -38), textcoords='offset points',
                     fontsize=14, color='#7048a0', arrowprops={'arrowstyle':'->'})
    save(fig, 'l8-noise')


@chinese_plot
def hinge_plot(s, loss):
    fig, ax = plt.subplots(figsize=(9.5, 5.7), layout='compressed')
    xx = np.linspace(-1.2, 2.8, 400)
    ax.plot(xx, np.maximum(0, 1 - xx), color='#2476ad', lw=3)
    for label, x, val, offset in zip('ABC', s, loss, [(0, 22), (30, 20), (25, 20)]):
        ax.scatter(x, val, s=90, color='#d65b30', zorder=4)
        ax.annotate(f'{label}：s={x:g}\n损失={val:g}', (x, val), xytext=offset,
                    textcoords='offset points', fontsize=16, ha='center')
    ax.axvline(1, color='#87939c', ls='--')
    ax.set(xlabel=r'$s_i=y_i f(x_i)$', ylabel=r'$\max(0,1-s_i)$', ylim=(-.18, 2.5),
           title='分对但 s<1，仍然产生合页损失')
    ax.spines[['top','right']].set_visible(False)
    save(fig, 'l8-hinge')


@chinese_plot
def xor_plot(X, y, model, phi):
    fig = plt.figure(figsize=(13.5, 5.8), layout='compressed')
    left = fig.add_subplot(1, 2, 1)
    right = fig.add_subplot(1, 2, 2, projection='3d')
    boundary(left, X, y, model, '0/1 四点 XOR：映射后模型的原空间边界',
             transform=phi, numbered=True)
    Z = phi(X)
    for k, marker in [(0,'o'),(1,'^')]:
        right.scatter(*Z[y==k].T, c=COLORS[k], marker=marker, s=90,
                      edgecolors='white', depthshade=False)
    for i, xyz in enumerate(Z):
        right.text(*(xyz + np.array([.035,.035,.04])), f'#{i+1}', fontsize=13)
    w, b = model.coef_[0], model.intercept_[0]
    u, v = np.meshgrid(np.linspace(-.1,1.1,18),np.linspace(-.1,1.1,18))
    phi2 = -(w[0]*u + w[2]*v + b)/w[1]
    right.plot_surface(u, phi2, v, color='#8a78a6', alpha=.24, edgecolor='none')
    right.set(xlabel=r'$\phi_1=x_1^2$', ylabel=r'$\phi_2=\sqrt{2}x_1x_2$',
              zlabel=r'$\phi_3=x_2^2$', title='同一映射：三维空间中的分界平面')
    right.tick_params(labelsize=11)
    right.set_xticks([0,1]); right.set_yticks([0,1]); right.set_zticks([0,1])
    right.view_init(elev=23, azim=-54)
    right.set_box_aspect((1,1.25,1))
    save(fig, 'l8-xor-map')


@chinese_plot
def rbf_plot(gammas):
    fig, ax = plt.subplots(figsize=(10.1, 5.6), layout='compressed')
    d = np.linspace(0, 4, 400)
    for gamma, color in zip(gammas, ['#2476ad', '#d65b30', '#784ca3']):
        ax.plot(d, np.exp(-gamma * d*d), lw=2.8, c=color, label=rf'$\gamma={gamma:g}$')
        value = np.exp(-gamma)
        ax.scatter(1, value, c=color, s=65)
        ax.annotate(f'{value:.3g}', (1, value), xytext=(14, 5), textcoords='offset points', c=color)
    ax.axvline(1, color='#888888', ls=':', lw=1)
    ax.set(xlabel='标准化坐标中的距离 d', ylabel=r'$K=\exp(-\gamma d^2)$',
           title='同一距离 d=1：gamma 越大，相似度越低', ylim=(-.05, 1.09))
    ax.legend(frameon=False)
    ax.spines[['top','right']].set_visible(False)
    save(fig, 'l8-rbf-similarity')


@chinese_plot
def heatmap(c_values, gamma_values, scores, selected):
    fig, ax = plt.subplots(figsize=(10, 7), layout='compressed')
    values = np.asarray(scores).reshape(len(c_values), len(gamma_values))
    image = ax.imshow(values, cmap='Blues', vmin=max(0, float(values.min())-.02), vmax=float(values.max()), aspect='auto')
    for i in range(len(c_values)):
        for j in range(len(gamma_values)):
            ax.text(j, i, f'{values[i,j]:.3f}', ha='center', va='center', fontsize=18,
                    color='white' if values[i,j] > (values.min()+values.max())/2 else '#1d3244')
    i, j = divmod(selected, len(gamma_values))
    ax.add_patch(plt.Rectangle((j-.48, i-.48), .96, .96, fill=False, ec='#e0a128', lw=3))
    ax.set(xticks=np.arange(len(gamma_values)), xticklabels=[f'{x:g}' for x in gamma_values],
           yticks=np.arange(len(c_values)), yticklabels=[f'{x:g}' for x in c_values],
           xlabel='gamma', ylabel='C', title='五折平衡准确率，金框为最高均值')
    fig.colorbar(image, ax=ax, label='平衡准确率')
    save(fig, 'l8-cv-heatmap')


@chinese_plot
def real_cv_plot(models):
    fig, (ax, delta_ax) = plt.subplots(2, 1, figsize=(10, 8), layout='constrained',
                                         gridspec_kw={'height_ratios': [1, 1]})
    names = ['多数类基线', 'Logistic回归', 'LinearSVC', 'RBF SVC']
    for i, row in enumerate(models.values()):
        scores = row['cv']['balanced_accuracy']['fold_scores']
        ax.scatter(scores, np.full(5, i) + np.linspace(-.12, .12, 5),
                   s=60, color=COLORS[i % 2], alpha=.8)
        mean = row['cv']['balanced_accuracy']['mean']
        ax.scatter(mean, i, s=110, color='#243f50', marker='|', linewidths=3, zorder=5)
        ax.annotate(f'{mean:.2%}', (mean, i), xytext=(0, 11),
                    textcoords='offset points', ha='center', fontsize=14)
    ax.set(yticks=range(len(names)), yticklabels=names, xlim=(.46, 1.04),
           xlabel='开发集平衡准确率（点为各折，竖线为均值）', ylim=(-.55, 3.65))
    ax.xaxis.set_major_formatter('{x:.0%}')

    logistic = models['LogisticRegression']['cv']['balanced_accuracy']['fold_scores']
    rbf = models['RBF SVC']['cv']['balanced_accuracy']['fold_scores']
    diff = 100 * (np.asarray(rbf) - logistic)
    folds = np.arange(1, len(diff) + 1)
    delta_ax.axhline(0, color='#52657a', lw=1)
    delta_ax.vlines(folds, 0, diff, color='#7f98a8', lw=2)
    delta_ax.scatter(folds, diff, s=85, color='#2476ad', zorder=3)
    for fold, value in zip(folds, diff):
        label = f'{value:+.2f}' if value else '0.00'
        delta_ax.annotate(label, (fold, value), xytext=(0, 8 if value >= 0 else -8),
                          textcoords='offset points', ha='center',
                          va='bottom' if value >= 0 else 'top', fontsize=15)
    delta_ax.set(xticks=folds, xticklabels=[f'第{i}折' for i in folds],
                 xlim=(.55, len(folds) + .45), ylim=(-3.2, 2.6),
                 ylabel='百分点', title='同一验证折：RBF减Logistic')
    for panel in (ax, delta_ax):
        panel.spines[['top', 'right']].set_visible(False)
    save(fig, 'l8-real-cv')



def search_rows(search, metric_names):
    """保留每一候选、每一折的分数；不重新训练。"""
    cv = search.cv_results_
    rows = []
    for i, params in enumerate(cv['params']):
        metrics = {}
        for metric in metric_names:
            suffix = 'score' if metric == 'score' else metric
            folds = [float(cv[f'split{k}_test_{suffix}'][i]) for k in range(search.n_splits_)]
            metrics[metric] = {'mean': float(cv[f'mean_test_{suffix}'][i]),
                               'std': float(cv[f'std_test_{suffix}'][i]),
                               'fold_scores': folds}
        rows.append({'params': params, 'cv': metrics})
    return plain(rows)


def linear_record(model, X, y):
    w = model.coef_[0]
    score = model.decision_function(X)
    return plain({'C': model.C, 'w': w, 'b': model.intercept_[0],
                  'support_indices': model.support_, 'n_support': model.n_support_,
                  'train_accuracy': model.score(X, y), 'errors': np.sum(model.predict(X) != y),
                  'signed_scores': (2 * y - 1) * score, 'one_sided_margin': 1 / np.linalg.norm(w),
                  'two_sided_margin': 2 / np.linalg.norm(w)})

@chinese_plot
def digit_features(images, features, pairs, labels):
    fig, axes = plt.subplots(2, len(pairs), figsize=(14, 4.8), layout='constrained')
    fig.get_layout_engine().set(hspace=.08)
    for ax, idx in zip(axes.flat, pairs.T.flat):
        ax.imshow(images[idx], cmap='Greys', vmin=0, vmax=1)
        ax.axhline(2.5, color='#d65b30', lw=1.6)
        ax.axvline(3.5, color='#075b9b', lw=2.2, ls=(0, (4, 3)),
                   path_effects=[patheffects.withStroke(linewidth=3.5, foreground='white')])
        a, t = features[idx]
        ax.set_title(f'数字 {labels[idx]} · #{idx}', fontsize=13)
        ax.set_xlabel(fr'$x_1$ = {a:.3f}    $x_2$ = {t:.3f}', fontsize=12)
        ax.set_xticks([]); ax.set_yticks([])
    save(fig, 'l8-digit-features')


def digit_conflict_subset(X, y, all_X, all_y):
    from scipy.spatial import Delaunay

    inside = Delaunay(X[y == 1]).find_simplex(all_X) >= 0
    added = all_X[(all_y == 0) & inside][:3]
    assert len(added) == 3
    return np.vstack((X, added)), np.r_[y, np.zeros(len(added), dtype=y.dtype)]


@chinese_plot
def digit_overlap(X, y, all_X, all_y):
    middle_X, middle_y = digit_conflict_subset(X, y, all_X, all_y)
    added = middle_X[len(X):]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2), layout='constrained')
    lo, hi = limits(all_X)
    panels = [(X, y, '沿用前面的 12 张'),
              (middle_X, middle_y, '放回 3 张难分的「1」'),
              (all_X, all_y, '全部 289 张开发图像')]
    for ax, (values, labels, title) in zip(axes, panels):
        points(ax, values, labels)
        ax.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), title=title,
               xlabel=r'$x_1$ 左右不对称度', ylabel=r'$x_2$ 上部笔迹强度')
    axes[0].legend(frameon=False, labels=["数字 1", "数字 7"], loc='upper right')
    axes[1].scatter(*added.T, marker='s', s=140, facecolors='none',
                    edgecolors='#7048a0', linewidths=1.7, zorder=6)
    from matplotlib.patches import Ellipse
    axes[2].add_patch(Ellipse((.252, .346), .151, .174, fill=False,
                             edgecolor='#7048a0', linestyle='--', linewidth=1.8))
    axes[2].annotate('两类交错', (.304, .285), (.43, .145), ha='center', color='#7048a0', zorder=8,
                     arrowprops={'arrowstyle': '->', 'color': '#7048a0'})
    save(fig, 'l8-noise')


@chinese_plot
def digit_cv(rows):
    fig, ax = plt.subplots(figsize=(10, 5), layout='constrained')
    offsets = np.arange(len(rows))
    for key, shift, color in [('线性', -.16, COLORS[0]), ('RBF', .16, COLORS[1])]:
        vals = [100 * row[key] for row in rows]
        bars = ax.barh(offsets + shift, vals, height=.28, label=key, color=color)
        ax.bar_label(bars, fmt='%.2f%%', padding=4, fontsize=14)
    ax.set(yticks=offsets, yticklabels=[row['任务'] for row in rows],
           xlim=(0, 112), xlabel='五折平衡准确率（%）')
    ax.set_xticks(np.arange(0, 101, 20))
    ax.invert_yaxis()
    ax.legend(loc='lower center', bbox_to_anchor=(.5, 1), ncol=2, frameon=False)
    ax.spines[['top', 'right']].set_visible(False)
    save(fig, 'l8-real-cv')
