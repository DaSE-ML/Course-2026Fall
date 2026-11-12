# Lesson 7 · AI Slop科研检测器

设计并验证 AI Slop 论文分类模型。比较 AI Slop 论文与人类撰写的论文，提炼有辨别价值的特征。

## 41 基本要求

1. **收集数据**　收集相关论文，比较两类论文的异同，并提炼可能有辨别价值的特征。
2. **设计模型**　构建单分类器版和 Boosting 版，自行设计实验，比较两者的分类表现。
3. **验证模型**　用两个模型分别在 SciSlopBench 和 [OpenReview 9 篇案例论文](#openreview-cases)上验证，按数据集分别报告结果。
4. **提交成果**　提交 3 页 A4 PDF 分析报告和可复现的 Jupyter Notebook。报告说明数据来源、特征设计、实验结果和主要发现。

## 43 加分项

1. **估计 AI Slop 比例**　用检测器估计 ICLR 2027 公开撤回投稿中的 AI Slop 比例，可抽样。提交一份 1 页 PDF 分析报告。
2. **开发降低 AI 率 Skill**　用 Skill 修订一篇 AI Slop 论文，比较修订前后的检测结果。提交 Skill、原稿和修订稿。

## 47 可用资源

- [Science or Slop?: Benchmarking and Mitigating Scientific Slop in AI-Generated Papers](https://arxiv.org/abs/2610.00531)
- [Measuring AI “Slop” in Text](https://arxiv.org/abs/2509.19163)
- [SciSlopBench 数据集](https://huggingface.co/datasets/yerim0210/Scientific_Slop)
- [ICLR 2027 公开撤回投稿入口](https://openreview.net/group?id=ICLR.cc%2F2027%2FConference) · [OpenReview 数据获取说明](https://docs.openreview.net/how-to-guides/data-retrieval-and-modification/how-to-get-all-notes-for-submissions-reviews-rebuttals-etc)
- [RAID](https://github.com/liamdugan/raid)

<a name="openreview-cases"></a>

### OpenReview 9 篇案例论文

以下为实验指定的 9 篇 ICLR 2027 撤回投稿。请通过 OpenReview 原页面获取材料，课程仓库仅提供链接。

1. [Learning Task-Conditioned Utilities for Topological Errors in Thin-Structure Segmentation](https://openreview.net/forum?id=6FmE0opsyf)
2. [Endpoint-Consistent Continual Learning Under Evolving Label Ontologies](https://openreview.net/forum?id=sN0bg9oSVd)
3. [Cross-Scale Consistency on Common Nyquist Support](https://openreview.net/forum?id=FcGKAYiLO7)
4. [Residual-Guided Adaptive Function-Space Projection for Replay-Free Continual Learning](https://openreview.net/forum?id=eg3S0j93tQ)
5. [Identifiability of a Shared Continuous Condition from Incompatible Ordinal Standards](https://openreview.net/forum?id=pvkx3rRGpj)
6. [When Can Graph Conformal Sets Transfer? Selective Diagnostics Under Unlabeled Topology Shift](https://openreview.net/forum?id=KNB2QkdGft)
7. [Drift-Conditioned Value of Information for Costly Multi-Label Streams with Delayed Labels](https://openreview.net/forum?id=yhKIgoY1uZ)
8. [Invariance Is Sample-Conditional: Risk-Controlled Consistency for Transformation–Example Pairs](https://openreview.net/forum?id=zc5WUOCnSj)
9. [Boundary-Action Equivariant Neural Operators for Sparse-Sensor PDE Inversion](https://openreview.net/forum?id=hltbEhJKud)

## 53 补充说明

1. 可用自然语言处理（NLP）方法或 AI 工具寻找特征。检测器可结合分类器输出和 AI 分析结果作出判断。
2. 客观呈现数据和检测结果，认识到任何检测方法都存在偏差，尊重研究对象。

## 提交方式

按组提交到各组私有仓库 `ML26-XX` 根目录下的 `lab07/` 文件夹。将分析报告和 Notebook 放在该目录，复现所需的数据与材料可注明来源和获取方式。完成加分项的同学附上相应成果。
