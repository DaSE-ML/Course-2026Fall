# Lesson 4：六个比赛 Top-3 方案与代码核对

核对日期：2026-10-27。以下按各比赛最终 **Private Leaderboard** 名次整理，未将顺延后的方案重新编号。M5 对应 **Accuracy** 赛道，March Mania 对应 **2025** 年比赛，华佗对应 WiDS Datathon 2021，已替换 MSK。

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

## 华佗：WiDS Datathon 2021

| 私榜名次 | 队伍 | 方案与代码提供情况 |
| --- | --- | --- |
| 1 | Dihydrogen Oxide / H2O.ai | [冠军方案](https://www.kaggle.com/competitions/widsdatathon2021/writeups/dihydrogen-oxide-h2o-ai-first-place-solution)可公开阅读。正文介绍特征工程与 stacking，评论补充目标编码、调参与 AutoML 细节；**暂未找到完整冠军代码或独立代码仓库**，不能标为完整代码已公开。 |
| 2 | EPFL | [亚军方案](https://www.kaggle.com/competitions/widsdatathon2021/writeups/epfl-2nd-place-solution)可公开阅读，并提供 [Google Drive Notebook 附件](https://drive.google.com/file/d/1JZGqsTgmCpdAzMiLcu5rGLrqNSYfjMRE/view)。文件页可访问，显示 single-lgbm-wids2021[public=87553][private=0.8770].ipynb；本次下载未成功，未核验代码内容。作者称其为单模型思路示例，最终提交为多个模型的集成，不能直接当作完整亚军流程。 |
| 3 | scientificmind（官方获奖公告称 .IL） | [季军方案](https://www.kaggle.com/competitions/widsdatathon2021/writeups/scientificmind-3rd-place-solution)可公开阅读，详细介绍特征工程、特征选择、插补、验证、约 120 个模型及逻辑回归集成；**正文及已显示评论未找到独立最终代码链接**。 |

前三名及方法另可参照[主办方获奖者访谈汇总](https://www.widsworldwide.org/get-inspired/blog/learn-from-wids-datathon-2021-winners-including-a-kaggle-grandmaster/)。主办方[获奖公告](https://www.widsworldwide.org/get-inspired/blog/the-wids-datathon-phase-2-is-now-open-supporting-excellence-in-research/)确认三队获奖。

**适用性**：符合本实验“解读 Top-1、基于 Top-3 提出改进”的要求，不等于三甲代码全部开源。任务是利用进入 ICU 后前 24 小时的数据识别糖尿病，不是预测未来是否发病。赛后提交评分尚未通过登录后实际操作确认。

## 周瑜：March Machine Learning Mania 2025

| 私榜名次 | 作者 | 方案与代码提供情况 |
| --- | --- | --- |
| 1 | Mohammad Odeh（modeh7） | **已公开**：[方案说明](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/writeups/mohammad-odeh-first-place-solution)、[Final-Solution-NCAA-2025](https://www.kaggle.com/code/modeh7/final-solution-ncaa-2025)，可查看数据准备、特征工程、模型及预测文件生成代码。 |
| 2 | baellouf | [方案说明](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/writeups/baellouf-second-place-solution-the-raddar-prophecy)；**部分公开**：作者说明使用 goto 基线并手工调整 Florida 的预测，提供了 [goto_conversion 仓库](https://github.com/gotoConversion/goto_conversion)，暂未找到其最终获奖提交的完整独立代码。基线不能直接称为亚军完整代码。 |
| 3 | w007425y（cununn） | **已公开**：[方案说明](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/writeups/w007425y-3th-place-solution)、[NCAA2025 3th Place Solution](https://www.kaggle.com/code/w007425y/ncaa2025-3th-place-solution)，可查看概率输入、人工调整及提交生成代码。 |

回到[Kaggle 比赛链接和详细规则](lab04-kaggle.md)。
