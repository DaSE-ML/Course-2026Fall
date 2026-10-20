"""MNIST增强示例图；变换与模型训练均由Notebook完成。"""
import matplotlib.pyplot as plt
from course_plot_style import chinese_plot
from augmentation_resampling_plots import _save


@chinese_plot
def plot_mnist_augmentation(panels, labels, assets_dir):
    fig, axes = plt.subplots(2, 5, figsize=(12, 6.5))
    names = ["原图", "A：左移1 px", "A：右移1 px", "B：逆时针10°", "B：顺时针10°"]
    for row, label in enumerate(labels):
        for col, (images, name) in enumerate(zip(panels, names)):
            ax = axes[row, col]
            ax.imshow(images[row], cmap="gray", vmin=0, vmax=255, interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([])
            ax.set_title(name, fontsize=18, pad=9)
            ax.spines[:].set_visible(False)
            if col == 0:
                ax.set_ylabel(f"数字 {label}", fontsize=18, labelpad=10)
    fig.suptitle("MNIST：A水平平移，B小角度旋转", fontsize=23, color="#26364a", y=.98)
    fig.text(.5, .025, "A+B合并两组变体，原图只保留一份；画布28×28，边缘填0", ha="center", fontsize=16, color="#52657a")
    fig.subplots_adjust(left=.075, right=.99, top=.84, bottom=.11, wspace=.15, hspace=.33)
    _save(fig, assets_dir, "l6-augmentation-mnist")
    return fig
