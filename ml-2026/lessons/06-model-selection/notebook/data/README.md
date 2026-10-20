# Lesson6实验数据

## MNIST

- 作者：Yann LeCun、Corinna Cortes、Christopher J. C. Burges；手写数字0–9，28×28灰度图。
- 原始说明：http://yann.lecun.com/exdb/mnist/ 。下载说明与许可核查：https://keras.io/api/datasets/mnist/ ，2026-10-19。
- 缓存：`mnist/mnist.npz`，约11 MB，Keras官方公开文件：https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz 。
- SHA-256：`731c5ac602752760c8e48fbffcf8c3b850d9dc2a2aedcf2cc48468fc17b673d1`，与Keras上游`keras/src/datasets/mnist.py`一致。
- MNIST许可按Keras官方说明为CC BY-SA 3.0：https://creativecommons.org/licenses/by-sa/3.0/ 。保留作者归属；课堂图是原图的平移/排版改编，图像部分遵循相同许可。
- `helpers/mnist_data.py`先检查本地缓存，缺失则自动下载并校验，不要求学生手工下载；离线时复制经校验的缓存文件及本说明到同一位置即可。不安装TensorFlow/Keras。
- 课堂实验只返回官方60,000条训练部分；seed=42分层取5,000训练与2,000开发验证。其余记录和官方10,000条测试均不评分。训练原图、变体与验证按原图ID隔离。
- 参考案例：《Hands-On Machine Learning》第3章Data Augmentation，https://github.com/ageron/handson-ml3/blob/main/03_classification.ipynb 。课程独立实现整数平移，缩小样本量以便课堂执行；模型规则沿用4近邻、距离加权，不重复参数搜索。本机课堂结果与作者全量结果分别标注，不混用数字。

## 其他数据

Bike Sharing保留在`bike-sharing/`及其原始Readme中。Iris、digits、Diabetes来自scikit-learn内置数据。策略讨论页的Fashion-MNIST和CIFAR-10样本说明见`README-image-augmentation.md`。
