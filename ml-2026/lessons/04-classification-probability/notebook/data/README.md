# UCI 信用卡客户违约数据

来源：UCI Machine Learning Repository，Default of Credit Card Clients，数据集 350。数据记录 2005 年 4 月至 9 月信用卡客户的账单与还款情况，标签为下个月是否违约。

- 样本数：30,000
- 原始特征数：23（另含 ID 和目标列）
- 许可：CC BY 4.0
- 论文引用：Yeh, I.-C., & Lien, C.-H. (2009). The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients. *Expert Systems with Applications*, 36(2), 2473–2480. DOI: 10.1016/j.eswa.2007.12.020.
- 数据集引用：Yeh, I. (2009). *Default of Credit Card Clients* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H.

`default of credit card clients.csv` 是随官方 XLS 文件转换得到的 UTF-8 逗号分隔副本，保留源列名；第一行为原始导出列名，第二行为数据字典列名，Notebook 使用 `header=1` 读取。课程主线只选用 `LIMIT_BAL`、`PAY_0`、`PAY_2`、`PAY_3`、`BILL_AMT1`、`BILL_AMT2`、`PAY_AMT1`、`PAY_AMT2` 八列，不使用 ID、性别、教育、婚姻、年龄。标签 `default payment next month` 中 1 表示违约、0 表示未违约。

原始 UCI 文件及转换副本均按 CC BY 4.0 随课程材料分发。完整数据用于可复现的教学实验；数据年代久远，不应用于当前客户或信贷决策。

## 自动准备与离线使用

Notebook 按顺序寻找课程 CSV、原始 XLS、ZIP；已有 XLS/ZIP 会自动转换。都不存在时，从 [UCI 官方 CSV 地址](https://archive.ics.uci.edu/static/public/350/data.csv) 自动获取较小的文件（约 2.8 MB），校验 SHA-256，并将 `X1`—`X23`、`Y` 转换成课程的列名和两行表头。这个地址来自 [UCI 官方数据 API](https://archive.ics.uci.edu/api/dataset?id=350)。也会识别已缓存的 `uci350-source.csv` 或 `data.csv`。无需学生手动下载或改表头。只改变文件格式，不改变实验数值、行序和样本数。

转换 XLS 使用 `xlrd==2.0.2`（已列入课程依赖；独立运行且缺失时自动安装）。首次获取数据或依赖需要联网；之后直接复用 `notebook/data/` 的缓存，可离线运行。第 5 讲可以复用第 4 讲缓存，也可以独立自动准备。下载中断会报错并清理不完整下载，不会改用合成数据。

学生公开材料一并提供体积较小的 CSV 和本说明（CC BY 4.0）；通常不需要联网。ZIP/XLS 不重复打包。若只下载了 Notebook、遗漏或删除了 CSV，自动下载会将缓存恢复到学生自己的电脑。核查日期：2026-10-04。
