"""MNIST自动缓存：使用Keras官方同一文件，不依赖TensorFlow/Keras。"""
from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen

import numpy as np

MNIST_URL = "https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz"
MNIST_SHA256 = "731c5ac602752760c8e48fbffcf8c3b850d9dc2a2aedcf2cc48468fc17b673d1"


def load_mnist_training(data_dir):
    """优先读取已下载文件；缺失时自动下载，只返回官方训练部分。"""
    folder = Path(data_dir) / "mnist"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "mnist.npz"
    if not path.exists():
        print("首次下载MNIST（约11 MB）；后续运行使用本地缓存。")
        with urlopen(MNIST_URL, timeout=120) as response:
            payload = response.read()
        if sha256(payload).hexdigest() != MNIST_SHA256:
            raise ValueError("MNIST下载校验失败，未保存文件；请稍后重新运行。")
        path.write_bytes(payload)
    if sha256(path.read_bytes()).hexdigest() != MNIST_SHA256:
        raise ValueError(f"MNIST缓存校验失败：{path}；请将该文件移走后重试。")
    with np.load(path, allow_pickle=False) as data:
        images, labels = data["x_train"], data["y_train"]
    assert images.shape == (60000, 28, 28) and labels.shape == (60000,)
    return images, labels
