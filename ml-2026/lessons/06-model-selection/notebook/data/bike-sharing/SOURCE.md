# UCI Bike Sharing：日租赁数据

- 作者：Hadi Fanaee-T；Fanaee-T, H. (2013). *Bike Sharing* [Dataset]. UCI Machine Learning Repository.
- DOI：https://doi.org/10.24432/C5W894
- 官方页面：https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset
- 官方下载：https://archive.ics.uci.edu/static/public/275/bike%2Bsharing%2Bdataset.zip
- 许可：CC BY 4.0（https://creativecommons.org/licenses/by/4.0/）；保留署名、来源及许可链接。
- 下载与核查：2026-10-18。本目录day.csv及Readme.txt直接从官方ZIP提取，未修改；无需联网即可运行课程示例。
- day.csv SHA-256：`a6bcf826782d3c0fbfdcbeead17cd0884185a0dafe8ff10cd48a874ee7ba18be`。
- 本课只使用day.csv的dteday与cnt：2011-01-01至2012-12-31的731条连续每日观测。cnt为每日租赁次数，并非去重人数。
- 课程改编：最后120天留作最终测试，前611天开发；一次留出、3轮扩展窗口、180天滑动窗口及7条记录间隔均为教学设计，不是UCI官方划分。
- 图中连续线连接真实每日观测，不是模型预测，不平滑或插补。本段仅演示划分协议，不报告性能；查看整条历史曲线用于教学不等于使用末段目标选参。
