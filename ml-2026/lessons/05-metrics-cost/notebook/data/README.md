# 第 5 讲：UCI 信用卡客户违约数据

数据与第 4 讲相同：[UCI Default of Credit Card Clients，ID 350](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients)。30,000 个样本、23 个原始特征；课程选择同样的 8 个特征，标签 1=下个月违约，0=未违约。

Notebook 优先识别本章或第 4 讲已有 CSV；也能转换已有 XLS/ZIP。没有缓存时自动获取 [UCI 官方较小的 CSV](https://archive.ics.uci.edu/static/public/350/data.csv)，校验后转换为课程的 UTF-8 CSV 列名和两行表头，保留原始数值与样本顺序。首次获取需联网，之后可以离线复用。读取 XLS 的 `xlrd==2.0.2` 已列入课程依赖；独立运行缺失时会自动安装。

许可：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。学生材料附带本章 CSV 和本说明，可独立离线运行；若遗漏 CSV，则首次运行自动获取。数据集引用：Yeh, I. (2009). *Default of Credit Card Clients* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H。

数据记录 2005 年的账单与还款情况，只用于教学复现，不代表当前信贷决策效果。完整来源说明见第 4 讲 `notebook/data/README.md`。核查日期：2026-10-04。
