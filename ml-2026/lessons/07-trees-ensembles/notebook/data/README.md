# 第7讲的数据

本讲统一使用[UCI Bike Sharing](https://doi.org/10.24432/C5W894)的每日数据day.csv，共731天。复用第6讲本地文件：

`lessons/06-model-selection/notebook/data/bike-sharing/day.csv`

Notebook从项目根目录定位该文件，不另下载Titanic或Iris。前611天为开发数据，其中前491天拟合、随后120天开发验证；末120天不用于本轮选参与评价。cnt为每日租赁次数，casual与registered不作为输入。高需求cnt≥4000为课内派生标签。
