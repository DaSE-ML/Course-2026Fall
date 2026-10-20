"""第 6 讲：真实图像样本上的增强策略讨论。

本模块只读取/缓存少量公开样本并绘图，不训练模型，也不报告增强收益。
"""

from __future__ import annotations

import gzip
import hashlib
import struct
from pathlib import Path
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from course_plot_style import chinese_plot, course_font_settings


FASHION_BASE = "https://storage.googleapis.com/tensorflow/tf-keras-datasets/"
FASHION_FILES = {
    "images": ("train-images-idx3-ubyte.gz", "8d4fb7e6c68d591d4c3dfef9ec88bf0d"),
    "labels": ("train-labels-idx1-ubyte.gz", "25c81989df183df01b3e8a0aad5dffbe"),
}
CIFAR_SAMPLES = {
    "automobile": "https://cave.cs.toronto.edu/kriz/cifar-10-sample/automobile1.png",
    "horse": "https://cave.cs.toronto.edu/kriz/cifar-10-sample/horse1.png",
}
FASHION_NAMES = {7: "运动鞋（7）", 9: "踝靴（9）"}
CIFAR_NAMES = {"automobile": "汽车", "horse": "马"}


def _download_cached(url, path, md5=None):
    path = Path(path)
    if path.exists():
        payload = path.read_bytes()
    else:
        print(f"首次下载样本：{path.name}")
        with urlopen(url, timeout=120) as response:
            payload = response.read()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    if md5 and hashlib.md5(payload).hexdigest() != md5:
        raise ValueError(f"缓存校验失败：{path}")
    return path


def _read_idx_gzip(path, expected_magic):
    with gzip.open(path, "rb") as stream:
        magic, = struct.unpack(">I", stream.read(4))
        if magic != expected_magic:
            raise ValueError(f"IDX magic number错误：{path}")
        count, = struct.unpack(">I", stream.read(4))
        if expected_magic == 2051:
            rows, cols = struct.unpack(">II", stream.read(8))
            data = np.frombuffer(stream.read(), dtype=np.uint8)
            if data.size != count * rows * cols:
                raise ValueError(f"IDX图像长度错误：{path}")
            return data.reshape(count, rows, cols)
        data = np.frombuffer(stream.read(), dtype=np.uint8)
        if data.size != count:
            raise ValueError(f"IDX标签长度错误：{path}")
        return data


def _first_label(images, labels, label):
    indices = np.flatnonzero(np.asarray(labels) == label)
    if len(indices) == 0:
        raise ValueError(f"样本中找不到标签：{label}")
    index = int(indices[0])
    return np.asarray(images[index]), int(np.asarray(labels)[index])


def load_strategy_samples(data_dir, mnist_images, mnist_labels):
    """加载三类讨论样本；MNIST图像和标签由调用方传入，其他样本自动缓存。"""
    data_dir = Path(data_dir)
    fashion_dir = data_dir / "fashion-mnist"
    fashion_paths = {
        key: _download_cached(FASHION_BASE + filename, fashion_dir / filename, md5)
        for key, (filename, md5) in FASHION_FILES.items()
    }
    fashion_images = _read_idx_gzip(fashion_paths["images"], 2051)
    fashion_labels = _read_idx_gzip(fashion_paths["labels"], 2049)
    fashion_samples = [_first_label(fashion_images, fashion_labels, label) for label in (7, 9)]

    cifar_dir = data_dir / "cifar-10-sample"
    cifar_samples = []
    for name, url in CIFAR_SAMPLES.items():
        path = _download_cached(url, cifar_dir / f"{name}1.png")
        with Image.open(path) as image:
            cifar_samples.append((np.asarray(image.convert("RGB")), name))

    mnist_samples = [_first_label(mnist_images, mnist_labels, label) for label in (6, 9)]
    return {
        "mnist": {
            "images": np.stack([sample[0] for sample in mnist_samples]),
            "labels": np.asarray([sample[1] for sample in mnist_samples]),
            "source": "Keras官方MNIST训练集；由调用方传入并已缓存",
        },
        "fashion_mnist": {
            "images": np.stack([sample[0] for sample in fashion_samples]),
            "labels": np.asarray([sample[1] for sample in fashion_samples]),
            "source": "Keras官方Fashion-MNIST训练集（Zalando）",
        },
        "cifar10": {
            "images": np.stack([sample[0] for sample in cifar_samples]),
            "labels": np.asarray([sample[1] for sample in cifar_samples]),
            "source": "Toronto CIFAR-10 sample page（仅两张公开样本）",
        },
    }


def _horizontal_flip(image):
    return np.flip(image, axis=1)


def _rotate_180(image):
    return np.rot90(image, 2)


def _vertical_flip(image):
    return np.flip(image, axis=0)


def _brightness(image, amount=1.18):
    values = np.asarray(image, dtype=np.float32) * amount
    return np.clip(values, 0, 255).astype(np.uint8)


def _save(fig, assets_dir, stem):
    out = Path(assets_dir)
    out.mkdir(parents=True, exist_ok=True)
    family = course_font_settings()["font.family"][0]
    fig.canvas.draw()
    for text in fig.findobj(plt.Text):
        text.set_fontfamily(family)
    fig.savefig(out / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(out / f"{stem}.png", dpi=300, bbox_inches="tight")


@chinese_plot
def plot_strategy_samples(samples, assets_dir):
    """绘制MNIST、Fashion-MNIST、CIFAR-10三行真实样本与候选变体。"""
    required = {"mnist", "fashion_mnist", "cifar10"}
    if set(samples) != required:
        raise ValueError(f"samples必须包含：{sorted(required)}")
    fig, axes = plt.subplots(3, 4, figsize=(12.8, 9.7))
    rows = [
        ("MNIST", samples["mnist"], ["6 原图", "9 原图", "水平翻转", "旋转180°"]),
        ("Fashion-MNIST", samples["fashion_mnist"], ["运动鞋 原图", "踝靴 原图", "水平翻转", "上下翻转"]),
        ("CIFAR-10", samples["cifar10"], ["汽车 原图", "马 原图", "马水平翻转", "汽车轻微增亮"]),
    ]
    for row_index, (dataset_name, group, titles) in enumerate(rows):
        images = group["images"]
        if dataset_name == "MNIST":
            variants = [images[0], images[1], _horizontal_flip(images[0]), _rotate_180(images[1])]
            cmap, vmin, vmax = "gray", 0, 255
        elif dataset_name == "Fashion-MNIST":
            variants = [images[0], images[1], _horizontal_flip(images[0]), _vertical_flip(images[1])]
            cmap, vmin, vmax = "gray", 0, 255
        else:
            variants = [images[0], images[1], _horizontal_flip(images[1]), _brightness(images[0])]
            cmap, vmin, vmax = None, 0, 255
        for col, (image, title) in enumerate(zip(variants, titles)):
            ax = axes[row_index, col]
            ax.imshow(image, cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
            ax.set_title(title, fontsize=14, pad=7)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            if col == 0:
                ax.set_ylabel(dataset_name, fontsize=16, labelpad=12)
    fig.suptitle("真实样本：哪些变化可能保持标签？", fontsize=23, color="#26364a", y=0.98)
    fig.text(0.5, 0.018, "比较原图与变体：哪些变化符合类别与使用场景？", ha="center", fontsize=15, color="#52657a")
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.88, wspace=0.15, hspace=0.38)
    _save(fig, assets_dir, "l6-augmentation-strategies")
    return fig

