# Lesson 4：六个比赛 Top-3 方案与代码核对

核对日期：2026-10-27。以下按各比赛最终 **Private Leaderboard** 名次整理，未将顺延后的方案重新编号。M5 对应 **Accuracy** 赛道，March Mania 对应 **2025** 年比赛，MSK 对应第二阶段最终榜单。

**“已公开”表示找到了可查看的作者代码或主办方归档，不表示已在当前环境运行成功或能完整复现获奖分数。**“部分公开”表示仅找到代码片段、关键组件或所引用的基线；“暂未找到”不等于作者从未公开。

## 国渊：IEEE-CIS Fraud Detection

| 私榜名次 | 队伍 | 方案与代码提供情况 |
| --- | --- | --- |
| 1 | FraudSquad | [方案说明](https://www.kaggle.com/competitions/ieee-fraud-detection/writeups/fraudsquad-1st-place-solution-part-2)；**已公开关键模型代码**：[XGBoost Notebook](https://www.kaggle.com/code/cdeotte/xgb-fraud-with-magic-0-9600)、[LightGBM 特征工程](https://www.kaggle.com/kyakovlev/ieee-fe-for-local-test)。XGBoost 是冠军集成的一个组件，不能将其单独视为全部冠军流程。 |
| 2 | 2 uncles and 3 puppies | [CPMP 方案说明](https://www.kaggle.com/competitions/ieee-fraud-detection/writeups/2-uncles-and-3-puppies-2nd-solution-cpmp-view)、[sggpls 方案说明](https://www.kaggle.com/competitions/ieee-fraud-detection/discussion/111554)；**部分公开**：CPMP 原帖提供 UID 与分组聚合代码片段，暂未确认完整最终集成代码入口。 |
| 3 | Young for you | 已在[最终私榜](https://www.kaggle.com/competitions/ieee-fraud-detection/leaderboard)核对队伍；**暂未找到可确认属于该队的公开方案及代码**。 |

## 荀彧：M5 Forecasting — Accuracy

| 私榜名次 | 作者／队伍 | 方案与代码提供情况 |
| --- | --- | --- |
| 1 | YeonJun In / YJ_STU | **已公开**：[方案说明](https://www.kaggle.com/competitions/m5-forecasting-accuracy/writeups/yeonjun-in-stu-1st-place-solution)、[主办方 A1 代码目录](https://github.com/Mcompetitions/M5-methods/tree/master/Code%20of%20Winning%20Methods/A1)，包括预处理、训练、预测及集成脚本。 |
| 2 | Matthias Anderer | **已公开**：[方案说明](https://www.kaggle.com/competitions/m5-forecasting-accuracy/writeups/matthias-2nd-place-solution)、[主办方 A2 代码目录](https://github.com/Mcompetitions/M5-methods/tree/master/Code%20of%20Winning%20Methods/A2)，包括 LightGBM、N-BEATS 与层级对齐代码。 |
| 3 | mf / mofl | **已公开**：[作者代码仓库](https://github.com/devmofl/M5_Accuracy_3rd)，含预处理、训练、预测和集成入口及环境说明。注意不是 Uncertainty 赛道的第三名仓库。 |

## 诸葛亮：ASHRAE — Great Energy Predictor III

| 私榜名次 | 方案与代码提供情况 |
| --- | --- |
| 1 | **已公开**：[主办方整理的 rank-1 目录](https://github.com/buds-lab/ashrae-great-energy-predictor-3-solution-analysis/tree/master/solutions/rank-1)，含训练、预测代码及说明。 |
| 2 | **已公开**：[主办方整理的 rank-2 目录](https://github.com/buds-lab/ashrae-great-energy-predictor-3-solution-analysis/tree/master/solutions/rank-2)，含模型与集成 Notebook。 |
| 3 | **已公开**：[主办方整理的 rank-3 目录](https://github.com/buds-lab/ashrae-great-energy-predictor-3-solution-analysis/tree/master/solutions/rank-3)，含数据生成、模型及集成 Notebook。 |

[主办方论文 §8.1](https://arxiv.org/html/2007.06933v1)说明，该仓库归档了获奖者提交的原始代码、方案摘要及运行指南。

## 管辂：LANL Earthquake Prediction

| 私榜名次 | 作者／队伍 | 方案与代码提供情况 |
| --- | --- | --- |
| 1 | Pascal Pfeiffer | **已公开**：[方案说明](https://www.kaggle.com/competitions/LANL-Earthquake-Prediction/discussion/94390)、[作者冠军 LightGBM Notebook](https://www.kaggle.com/code/ilu000/1-private-lb-kernel-lanl-lgbm)，可查看特征提取、训练与预测代码。 |
| 2 | Jun Koda | [方案说明](https://www.kaggle.com/competitions/LANL-Earthquake-Prediction/writeups/jun-koda-2nd-place-solution)公开了训练样本构造、32 个特征及 CatBoost 方法；**暂未找到完整的作者训练与预测代码**。 |
| 3 | currypurin / hmdhmd | [方案说明](https://www.kaggle.com/competitions/LANL-Earthquake-Prediction/writeups/character-ranking-3rd-place-memo)；**部分公开**：正文有目标值调整代码，作者评论提供 LightGBM 参数，暂未找到完整训练与预测流程。 |

## 华佗：Personalized Medicine — Redefining Cancer Treatment

| 私榜名次 | 队伍 | 方案与代码提供情况 |
| --- | --- | --- |
| 1 | ilmirashaim | **暂未找到可确认属于最终第一名的公开方案及代码**。 |
| 2 | Waterpls | **暂未找到可确认属于最终第二名的公开方案及代码**。 |
| 3 | Yang（jeffcao） | **暂未找到可确认属于最终第三名的公开方案及代码**。 |

三队名次已在[最终 Private Leaderboard](https://www.kaggle.com/competitions/msk-redefining-cancer-treatment/leaderboard)核对。本次同时检索了比赛讨论区的 Solution 相关帖子及队伍名，未将一般学习项目、第一阶段方案或主办方所说的“solution labels”（测试集标签）当成前三名代码。

该比赛有两个阶段，[主办方结赛说明](https://www.kaggle.com/competitions/msk-redefining-cancer-treatment/discussion/40676)也提到第二阶段标注人员和变异分布存在差异。**目前不能保证该题能直接找到符合本实验要求的 Top-1 公开方案，选题前需进一步确认。**

## 周瑜：March Machine Learning Mania 2025

| 私榜名次 | 作者 | 方案与代码提供情况 |
| --- | --- | --- |
| 1 | Mohammad Odeh（modeh7） | **已公开**：[方案说明](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/writeups/mohammad-odeh-first-place-solution)、[Final-Solution-NCAA-2025](https://www.kaggle.com/code/modeh7/final-solution-ncaa-2025)，可查看数据准备、特征工程、模型及预测文件生成代码。 |
| 2 | baellouf | [方案说明](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/writeups/baellouf-second-place-solution-the-raddar-prophecy)；**部分公开**：作者说明使用 goto 基线并手工调整 Florida 的预测，提供了 [goto_conversion 仓库](https://github.com/gotoConversion/goto_conversion)，暂未找到其最终获奖提交的完整独立代码。基线不能直接称为亚军完整代码。 |
| 3 | w007425y（cununn） | **已公开**：[方案说明](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/writeups/w007425y-3th-place-solution)、[NCAA2025 3th Place Solution](https://www.kaggle.com/code/w007425y/ncaa2025-3th-place-solution)，可查看概率输入、人工调整及提交生成代码。 |

回到[Kaggle 比赛链接和详细规则](lab04-kaggle.md)。
