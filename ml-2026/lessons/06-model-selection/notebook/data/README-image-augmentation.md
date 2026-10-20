# 图像增强样本来源

本目录下的样本由 `helpers/image_augmentation_examples.py` 按需下载并缓存，仅供教师本地课堂展示；本页不训练模型、不报告增强收益。

- **MNIST**：由调用方传入课程已缓存的 Keras 官方训练图片与标签，取第一个 6 和 9。完整来源、校验和与缓存说明见本目录 `README.md` 与 `../helpers/mnist_data.py`。
- **Fashion-MNIST**：使用 Keras 官方存储中的训练图片/标签 IDX 压缩文件，代码按给定 MD5 校验。数据集由 Zalando Research 发布，采用 MIT 许可；再分发时应保留 Zalando 归属信息。样本 7 为 sneaker（运动鞋），9 为 ankle boot（踝靴）。
- **CIFAR-10**：只缓存 Toronto CIFAR-10 sample 页面公开的 `automobile1.png` 与 `horse1.png`，不下载完整数据集。原页面未明确给出可据此主张的再分发许可，因此本课程仅作教师本地教学展示；公开发布前需重新核查许可与归属。

Fashion-MNIST保留完整许可于`LICENSE-fashion-mnist.txt`；原文来源：https://github.com/zalandoresearch/fashion-mnist/blob/master/LICENSE 。本说明核查于2026-10-19。

面板中的变换名称不预先判断对错，供学生讨论。水平翻转、轻微增亮是候选假设；MNIST的镜像/180°旋转可能破坏数字语义，Fashion-MNIST的上下翻转可能偏离正常摆放分布。是否保持标签取决于任务与部署分布，不能从这张样本图推出泛化收益。
