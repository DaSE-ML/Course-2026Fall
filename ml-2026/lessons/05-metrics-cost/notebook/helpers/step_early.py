"""课程可选绘图与原版对照辅助；训练主线留在 Notebook。"""
# Official comparison adapted from scikit-learn; BSD-3-Clause.
# https://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html
import matplotlib.pyplot as plt
import numpy as np
def plot_polynomials(X, y, models, cv_results):
    """只绘图：接收已训练模型与已有 CV 结果，不再训练。"""
    grid = np.linspace(0, 1, 100)
    fig, axes = plt.subplots(1, len(models), figsize=(14, 4))
    for ax, (degree, model) in zip(axes, models.items()):
        mean, std = cv_results[degree]
        ax.plot(grid, model.predict(grid[:, None]), label='Model')
        ax.plot(grid, np.cos(1.5*np.pi*grid), label='True function')
        ax.scatter(X, y, s=20, label='Samples')
        ax.set(xlim=(0,1), ylim=(-2,2), xlabel='x', ylabel='y',
               title=f'Degree {degree}: CV MSE={mean:.2e} ± {std:.2e}')
        ax.legend()
    plt.tight_layout(); plt.show()

def official_comparison():
    """可选附录：上游十种模型三组数据对照，非课堂主线。"""
    # Authors: The scikit-learn developers
    # SPDX-License-Identifier: BSD-3-Clause

    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import ListedColormap

    from sklearn.datasets import make_circles, make_classification, make_moons
    from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
    from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
    from sklearn.gaussian_process import GaussianProcessClassifier
    from sklearn.gaussian_process.kernels import RBF
    from sklearn.inspection import DecisionBoundaryDisplay
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import GaussianNB
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC
    from sklearn.tree import DecisionTreeClassifier

    names = [
        "Nearest Neighbors",
        "Linear SVM",
        "RBF SVM",
        "Gaussian Process",
        "Decision Tree",
        "Random Forest",
        "Neural Net",
        "AdaBoost",
        "Naive Bayes",
        "QDA",
    ]

    classifiers = [
        KNeighborsClassifier(3),
        SVC(kernel="linear", C=0.025, random_state=42),
        SVC(gamma=2, C=1, random_state=42),
        GaussianProcessClassifier(1.0 * RBF(1.0), optimizer=None, random_state=42),
        DecisionTreeClassifier(max_depth=5, random_state=42),
        RandomForestClassifier(
            max_depth=5, n_estimators=10, max_features=1, random_state=42
        ),
        MLPClassifier(alpha=1, max_iter=1000, random_state=42),
        AdaBoostClassifier(random_state=42),
        GaussianNB(),
        QuadraticDiscriminantAnalysis(),
    ]

    X, y = make_classification(
        n_features=2, n_redundant=0, n_informative=2, random_state=1, n_clusters_per_class=1
    )
    rng = np.random.RandomState(2)
    X += 2 * rng.uniform(size=X.shape)
    linearly_separable = (X, y)

    datasets = [
        make_moons(noise=0.3, random_state=0),
        make_circles(noise=0.2, factor=0.5, random_state=1),
        linearly_separable,
    ]

    figure = plt.figure(figsize=(27, 9))
    i = 1
    # 对每一类几何结构重复相同的比较流程。
    for ds_cnt, ds in enumerate(datasets):
        # 先划分再拟合；三种数据各用同一随机种子，保留 40% 作展示性留出评估。
        X, y = ds
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.4, random_state=42
        )

        x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
        y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5

        # 每行第一列只显示输入数据，便于和预测边界比较。
        cm = plt.cm.RdBu
        cm_bright = ListedColormap(["#FF0000", "#0000FF"])
        ax = plt.subplot(len(datasets), len(classifiers) + 1, i)
        if ds_cnt == 0:
            ax.set_title("Input data")
        # 训练样本用不透明点表示。
        ax.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cm_bright, edgecolors="k")
        # 测试样本用半透明点表示。
        ax.scatter(
            X_test[:, 0], X_test[:, 1], c=y_test, cmap=cm_bright, alpha=0.6, edgecolors="k"
        )
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xticks(())
        ax.set_yticks(())
        i += 1

        # 每列采用预先指定的分类器配置，不根据此图重新选择参数。
        for name, clf in zip(names, classifiers):
            ax = plt.subplot(len(datasets), len(classifiers) + 1, i)

            # 标准化在训练子集内拟合，避免测试统计量进入模型。
            clf = make_pipeline(StandardScaler(), clf)
            clf.fit(X_train, y_train)
            score = clf.score(X_test, y_test)
            # 背景来自估计器响应；不同分类器的颜色数值不可当作同尺度校准概率。
            DecisionBoundaryDisplay.from_estimator(
                clf, X, cmap=cm, alpha=0.8, ax=ax, eps=0.5
            )

            # 训练样本用不透明点表示。
            ax.scatter(
                X_train[:, 0], X_train[:, 1], c=y_train, cmap=cm_bright, edgecolors="k"
            )
            # 测试样本用半透明点表示。
            ax.scatter(
                X_test[:, 0],
                X_test[:, 1],
                c=y_test,
                cmap=cm_bright,
                edgecolors="k",
                alpha=0.6,
            )

            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.set_xticks(())
            ax.set_yticks(())
            if ds_cnt == 0:
                ax.set_title(name)
            ax.text(
                x_max - 0.3,
                y_min + 0.3,
                ("%.2f" % score).lstrip("0"),
                size=15,
                horizontalalignment="right",
            )
            i += 1

    plt.tight_layout()
    plt.show()

def export_comparison_assets(chosen, threshold_table, y_final, final_pred):
    """可选写文件：保存指标及旧课件三幅图，不参与选择模型。"""
    from pathlib import Path
    import json
    from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
    from sklearn.datasets import make_moons, make_circles, make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.naive_bayes import GaussianNB
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.inspection import DecisionBoundaryDisplay
    X, y = make_classification(n_features=2, n_redundant=0, n_informative=2, random_state=1, n_clusters_per_class=1)
    X += 2 * np.random.RandomState(2).uniform(size=X.shape)
    datasets = [make_moons(noise=0.3, random_state=0), make_circles(noise=0.2, factor=0.5, random_state=1), (X,y)]
    import json
    project_root = Path.cwd()
    if not (project_root / 'notebooks').exists():
        project_root = project_root.parent
    asset_dir = project_root / 'lessons' / 'assets'
    asset_dir.mkdir(parents=True, exist_ok=True)
    summary = {'validation_selected_threshold':chosen,'validation':threshold_table.to_dict(orient='records'),
     'test_precision':float(precision_score(y_final,final_pred)),'test_recall':float(recall_score(y_final,final_pred)),
     'test_f1':float(f1_score(y_final,final_pred)),'test_accuracy':float(accuracy_score(y_final,final_pred)),
     'confusion_matrix':confusion_matrix(y_final,final_pred).tolist()}
    (asset_dir/'lab03-summary.json').write_text(json.dumps(summary,indent=2))
    # 使用相同的官方数据与划分，导出便于投影的三分类器补充图。
    for dataset_name,(X_small,y_small) in zip(['moons','circles','linear'], datasets):
        a,b,c,d=train_test_split(X_small,y_small,test_size=0.4,random_state=42)
        fig,axes=plt.subplots(1,3,figsize=(12,3.6))
        for ax,(name,est) in zip(axes,[('Logistic',LogisticRegression(max_iter=1000)),('kNN',KNeighborsClassifier(3)),('Naive Bayes',GaussianNB())]):
            model=make_pipeline(StandardScaler(),est).fit(a,c)
            # 背景来自估计器响应；不同分类器的颜色数值不可当作同尺度校准概率。
            DecisionBoundaryDisplay.from_estimator(model,X_small,ax=ax,response_method='predict',alpha=0.25,cmap='RdBu')
            ax.scatter(a[:,0],a[:,1],c=c,cmap='RdBu',s=22,edgecolors='k')
            ax.scatter(b[:,0],b[:,1],c=d,cmap='RdBu',s=22,edgecolors='k',alpha=0.5)
            ax.set_title(f'{name} | holdout={model.score(b,d):.2f}')
        fig.suptitle(f'{dataset_name}: fixed settings, one split, no model ranking')
        fig.tight_layout();fig.savefig(asset_dir/f'lab03-{dataset_name}-compact.png',dpi=150);plt.show()
