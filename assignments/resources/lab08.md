# Lesson 8 · 集智成谋

用集成学习设计 Agent Workflow。把 Agent 当作基学习器，探索经典集成思想能怎样指导多个 Agent 协作。

[查看任务海报](../lab08-poster.jpg)

## 01 基本要求

1. **选择任务**　自选任务与数据，明确评价方式。
2. **设计协作**　将 Agent 作为基学习器（Base Learner），借鉴 Bagging、Boosting、随机森林或 Stacking 等思想，设计并实现一个动态工作流（Dynamic Workflow）。
3. **实验探索**　比较集成工作流与单 Agent 的任务表现，分析集成协作的作用。
4. **提交成果**　提交 3 页 A4 PDF 分析报告、可运行的工作流代码与配置、工作流图及实验结果。报告说明设计借鉴了哪些集成学习思想，并分析实验结果。

## 02 加分项

1. **挑战强者**　比较“弱 Agent＋工作流”与单个“强 Agent”的任务表现和调用开销。
2. **增益与代价**　以单 Agent 为基线，评估集成方法每单位性能提升所需的额外开销。若性能持平或下降，报告性能差值和实际开销，说明结果。

## 03 可用资源

### 海报上的五篇论文

- 多路径采样与聚合 · [Self-Consistency（ICLR’23）](https://arxiv.org/abs/2203.11171)
- 错误反馈与迭代改进 · [Boosting of Thoughts（ICLR’24）](https://arxiv.org/abs/2402.11140)
- 分层协作与结果融合 · [Mixture-of-Agents（ICLR’25）](https://arxiv.org/abs/2406.04692)
- 工作流自动优化 · [AFlow（ICLR’25，Oral）](https://arxiv.org/abs/2410.10762)
- 性能与推理开销 · [Large Language Monkeys（arXiv’24）](https://arxiv.org/abs/2407.21787)

### 延伸阅读

- 推理树的选择与协作 · [Forest-of-Thought（ICML’25）](https://proceedings.mlr.press/v267/bi25a.html)
- 模型输出的排序与融合 · [LLM-Blender（ACL’23）](https://aclanthology.org/2023.acl-long.792/)
- 将 Agent 编排为可优化的图 · [GPTSwarm（ICML’24）](https://proceedings.mlr.press/v235/zhuge24a.html)
- 增加调用次数对性能有什么影响 · [Are More LLM Calls All You Need?（NeurIPS’24）](https://proceedings.neurips.cc/paper_files/paper/2024/hash/51173cf34c5faac9796a47dc2fdd3a71-Abstract-Conference.html)
- 工作流代码参考 · [Mixture-of-Agents](https://github.com/togethercomputer/moa) · [AFlow](https://github.com/FoundationAgents/AFlow)

### 可选评测数据

- 数学应用题 · [GSM8K](https://github.com/openai/grade-school-math) · [MGSM（含中文）](https://huggingface.co/datasets/juletxara/mgsm)
- 多学科选择题 · [MMLU-Pro](https://github.com/TIGER-AI-Lab/MMLU-Pro)
- 复用前序实验任务 · [Lab 07 的 SciSlopBench 入口](lab07.md)

## 04 补充说明

1. 模型、工具、模态与实现语言不限。多个 Agent 可使用同一模型，也可使用不同模型。
2. 可借鉴一种或多种集成思想。
3. 不要求实现性能提升，重点考察分析与推理过程。

## 提交方式

按组将成果放到各组私有仓库 `ML26-XX` 根目录下的 `lab08/` 文件夹。完成加分项的组附上对应的分析与结果。
