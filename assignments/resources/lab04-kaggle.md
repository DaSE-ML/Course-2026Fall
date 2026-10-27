# Lesson 4：群雄逐鹿：Kaggle 初出茅庐

> [!IMPORTANT]
> **Kaggle 方案须注明小组编号**
>
> 参与 **“实战出征”** 或 **“榜上争锋”** 加分项时，须在 Kaggle 的 **Solution** 中注明本组编号 **`ML26-XX`**（如 `ML26-01`），便于核对提交与排名。

领取一张人物卡，研习获胜兵法。[查看任务海报](../lab04-poster.jpg)。

## 1. 实验要求

### 基本要求

1. **选将出征**：查看人物卡对应的 Kaggle 比赛。
2. **知己知彼**：了解比赛任务、数据和评价指标。
3. **研习兵法**：找到比赛的 Top-1 方案，详细解读其数据处理、特征工程、模型方法与制胜关键。不要求完整复现冠军代码。
4. **战报呈上**：提交方案解读文档，附比赛及 Top-1 方案来源链接。

### 加分项

- **实战出征**：在 Kaggle 提交 Submission，附提交链接；
  **或者 另出奇谋**：基于 Top-3 方案提出改进思路，并解释其作用。
- **榜上争锋**：在比赛中取得高排名，附排名截图或链接。

### 提交方式

按组提交到各组私有仓库 `ML26-XX` 根目录下的 **`lab04/` 文件夹**，直接 push。

基本交付物为方案解读文档，附比赛及 Top-1 方案来源链接。参与加分项的同学同时附上对应提交链接、改进方案或排名截图／链接。

## 2. 比赛入口

| 人物牌 | 比赛 | Kaggle 入口 | 方案与代码 |
| --- | --- | --- | --- |
| 国渊 | IEEE-CIS 欺诈检测 | [比赛主页](https://www.kaggle.com/competitions/ieee-fraud-detection) | [查看](#国渊ieee-cis-欺诈检测) |
| 荀彧 | M5 销量预测（Accuracy） | [比赛主页](https://www.kaggle.com/competitions/m5-forecasting-accuracy) | [查看](#荀彧m5-销量预测) |
| 诸葛亮 | ASHRAE 能耗预测 | [比赛主页](https://www.kaggle.com/competitions/ashrae-energy-prediction) | [查看](#诸葛亮ashrae-能耗预测) |
| 管辂 | LANL 地震预测 | [比赛主页](https://www.kaggle.com/competitions/LANL-Earthquake-Prediction) | [查看](#管辂lanl-地震预测) |
| 华佗 | WiDS 糖尿病识别（2021） | [比赛主页](https://www.kaggle.com/competitions/widsdatathon2021) | [查看](#华佗wids-糖尿病识别) |
| 周瑜 | March Mania 胜负预测（2025） | [比赛主页](https://www.kaggle.com/competitions/march-machine-learning-mania-2025) | [查看](#周瑜march-mania-胜负预测) |

## 3. 补充说明与排名规则

- **不能照搬任一支队伍的方案（Red Line）。**
- 可以使用“机器学习邪道锦囊”。
- **排名口径**：Top-1、Top-3 均以最终 **Private Leaderboard** 为准；若对应队伍未公开 Solution，则按该榜单排名依次顺延，并在作业中注明实际采用的队伍、名次与来源链接。
- **在线提交与排名**：以平台当前开放情况及比赛规则为准。

## 4. Top-3 方案与代码

以下保留原始私榜名次，不将顺延后的方案重新编号。可在比赛的 **Discussion / Writeups** 查找方案说明，在 **Code** 查找 Notebook。

**代码状态说明**：“已公开”表示找到作者代码或主办方归档，未验证当前环境可运行或能复现获奖分数；“部分公开”表示仅有关键组件、片段或引用基线；“暂未找到”不等于从未公开。核对日期：2026-10-27。

### 国渊：IEEE-CIS 欺诈检测

| 私榜名次 | 队伍／作者 | 方案说明 | 代码提供情况 |
| --- | --- | --- | --- |
| 1 | FraudSquad | [方案](https://www.kaggle.com/competitions/ieee-fraud-detection/writeups/fraudsquad-1st-place-solution-part-2) | 部分公开：[XGBoost](https://www.kaggle.com/code/cdeotte/xgb-fraud-with-magic-0-9600)、[LightGBM 特征工程](https://www.kaggle.com/kyakovlev/ieee-fe-for-local-test)；属于冠军集成的组件 |
| 2 | 2 uncles and 3 puppies | [CPMP](https://www.kaggle.com/competitions/ieee-fraud-detection/writeups/2-uncles-and-3-puppies-2nd-solution-cpmp-view) / [sggpls](https://www.kaggle.com/competitions/ieee-fraud-detection/discussion/111554) | 部分公开：UID 与聚合特征代码片段，未确认完整集成代码 |
| 3 | Young for you | 暂未找到 | 暂未找到；[私榜入口](https://www.kaggle.com/competitions/ieee-fraud-detection/leaderboard) |

### 荀彧：M5 销量预测

| 私榜名次 | 队伍／作者 | 方案说明 | 代码提供情况 |
| --- | --- | --- | --- |
| 1 | YeonJun In / YJ_STU | [方案](https://www.kaggle.com/competitions/m5-forecasting-accuracy/writeups/yeonjun-in-stu-1st-place-solution) | 已公开：[官方 A1 代码](https://github.com/Mcompetitions/M5-methods/tree/master/Code%20of%20Winning%20Methods/A1) |
| 2 | Matthias Anderer | [方案](https://www.kaggle.com/competitions/m5-forecasting-accuracy/writeups/matthias-2nd-place-solution) | 已公开：[官方 A2 代码](https://github.com/Mcompetitions/M5-methods/tree/master/Code%20of%20Winning%20Methods/A2) |
| 3 | mf / mofl | [仓库说明](https://github.com/devmofl/M5_Accuracy_3rd) | 已公开：[作者代码](https://github.com/devmofl/M5_Accuracy_3rd) |

注意：这里是 **Accuracy** 赛道，不是 Uncertainty。

### 诸葛亮：ASHRAE 能耗预测

| 私榜名次 | 队伍／作者 | 方案说明 | 代码提供情况 |
| --- | --- | --- | --- |
| 1 | 第 1 名 | [目录内说明](https://github.com/buds-lab/ashrae-great-energy-predictor-3-solution-analysis/tree/master/solutions/rank-1) | 已公开：[官方 rank-1 代码](https://github.com/buds-lab/ashrae-great-energy-predictor-3-solution-analysis/tree/master/solutions/rank-1) |
| 2 | 第 2 名 | [目录内说明](https://github.com/buds-lab/ashrae-great-energy-predictor-3-solution-analysis/tree/master/solutions/rank-2) | 已公开：[官方 rank-2 代码](https://github.com/buds-lab/ashrae-great-energy-predictor-3-solution-analysis/tree/master/solutions/rank-2) |
| 3 | 第 3 名 | [目录内说明](https://github.com/buds-lab/ashrae-great-energy-predictor-3-solution-analysis/tree/master/solutions/rank-3) | 已公开：[官方 rank-3 代码](https://github.com/buds-lab/ashrae-great-energy-predictor-3-solution-analysis/tree/master/solutions/rank-3) |

[主办方论文 §8.1](https://arxiv.org/html/2007.06933v1)介绍了获奖方案、原始代码与运行指南的归档。

### 管辂：LANL 地震预测

| 私榜名次 | 队伍／作者 | 方案说明 | 代码提供情况 |
| --- | --- | --- | --- |
| 1 | Pascal Pfeiffer | [方案](https://www.kaggle.com/competitions/LANL-Earthquake-Prediction/discussion/94390) | 已公开：[LightGBM Notebook](https://www.kaggle.com/code/ilu000/1-private-lb-kernel-lanl-lgbm) |
| 2 | Jun Koda | [方案](https://www.kaggle.com/competitions/LANL-Earthquake-Prediction/writeups/jun-koda-2nd-place-solution) | 暂未找到完整训练与预测代码 |
| 3 | currypurin / hmdhmd | [方案](https://www.kaggle.com/competitions/LANL-Earthquake-Prediction/writeups/character-ranking-3rd-place-memo) | 部分公开：目标值调整代码与 LightGBM 参数 |

### 华佗：WiDS 糖尿病识别

| 私榜名次 | 队伍／作者 | 方案说明 | 代码提供情况 |
| --- | --- | --- | --- |
| 1 | Dihydrogen Oxide / H2O.ai | [方案](https://www.kaggle.com/competitions/widsdatathon2021/writeups/dihydrogen-oxide-h2o-ai-first-place-solution) | 暂未找到完整代码；方法及实现细节见正文和评论 |
| 2 | EPFL | [方案](https://www.kaggle.com/competitions/widsdatathon2021/writeups/epfl-2nd-place-solution) | 提供[单模型 Notebook 附件](https://drive.google.com/file/d/1JZGqsTgmCpdAzMiLcu5rGLrqNSYfjMRE/view)；文件页可访问，下载及代码内容未核验，不等同完整获奖集成 |
| 3 | scientificmind（.IL） | [方案](https://www.kaggle.com/competitions/widsdatathon2021/writeups/scientificmind-3rd-place-solution) | 暂未找到独立最终代码链接 |

任务：使用**进入 ICU 后前 24 小时**的临床数据识别糖尿病，指标为 **ROC-AUC**。三份方案均可公开阅读；另有[主办方获奖者访谈](https://www.widsworldwide.org/get-inspired/blog/learn-from-wids-datathon-2021-winners-including-a-kaggle-grandmaster/)。

参赛规则：原比赛每队最多 4 人，至少半数成员为女性；赛后在线提交评分尚未确认。

### 周瑜：March Mania 胜负预测

| 私榜名次 | 队伍／作者 | 方案说明 | 代码提供情况 |
| --- | --- | --- | --- |
| 1 | Mohammad Odeh（modeh7） | [方案](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/writeups/mohammad-odeh-first-place-solution) | 已公开：[最终 Notebook](https://www.kaggle.com/code/modeh7/final-solution-ncaa-2025) |
| 2 | baellouf | [方案](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/writeups/baellouf-second-place-solution-the-raddar-prophecy) | 部分公开：引用[goto_conversion 基线](https://github.com/gotoConversion/goto_conversion)，未找到其完整最终代码 |
| 3 | w007425y（cununn） | [方案](https://www.kaggle.com/competitions/march-machine-learning-mania-2025/writeups/w007425y-3th-place-solution) | 已公开：[最终 Notebook](https://www.kaggle.com/code/w007425y/ncaa2025-3th-place-solution) |

注意：这里对应 **2025** 年比赛。
