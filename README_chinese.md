# CivAgent: Large Language Models based Human-like Agent  

<p align="center" width="100%">

[![演示视频](https://res.cloudinary.com/marcomontalbano/image/upload/v1719391182/video_to_markdown/images/youtube--hD2flShjI0c-c05b58ac6eb4c4700831b2b3070cd403.jpg)](https://www.youtube.com/watch?v=hD2flShjI0c "演示视频")

CivAgent是针对开源战略游戏[Unciv](https://github.com/yairm210/Unciv)开发的智能体，基于大型语言模型(LLM)技术。 
该项目旨在解决玩家找不到陪玩的痛点，并构建数据飞轮以协助LLM-based Agent的研究。
将LLM与游戏核心玩法深度结合，我们认为这就是AI Native Game。

Native Unciv: https://github.com/yairm210/Unciv

Unciv Wiki: https://civilization.fandom.com/wiki/Unciv

Unciv We Used (source code): https://github.com/asdqsczser/Unciv/tree/release/fuxi_ver

游戏下载(7月初发布)

Paper: https://openreview.net/forum?id=AuT65qKLrr

Appendix: https://github.com/fuxiAIlab/CivAgent/blob/main/paper_appendix.pdf

YouTube: https://www.youtube.com/playlist?list=PL9G00-od8ezYNblsqMca7urrLoHSZ7Vs3

## 新闻
![new](/assets/new.gif) **06/20/2024**: 论文Benchmark复现代码开源. 面向非开发者的游玩版本预计在7月初发布. 

**06/09/2024**: 论文投稿NeurIPS 2024 Track Datasets and Benchmarks, [Under Review](https://openreview.net/forum?id=AuT65qKLrr).

## 👨‍💻 开发者文档
详见[开发者文档](/docs/README_for_developer_chinese.md)

## ⚡ 开始游戏
目前AI服务只能在多人游戏模式下使用，只支持Windows和Mac平台。

**注意您的存档和聊天数据将被服务器收集，并用于本项目的AI效果迭代(非商用目的)。**
### Step 1. 下载专用游戏客户端
目前只支持Windows平台，下载地址为: [Download]()

### Step 2. 设置服务器地址
打开游戏，在设置界面修改同步频率和服务器地址;修改后的服务器地址为:http://sl.office.fuxi.netease.com:44952

### Step 3. 设置游戏
在“Start new game”界面，勾选左下角的“Online Multiplayer”;建议从“中世纪”开始，请点击“设置为当前玩家”，点击右边的问号选择一个文明，可选文明有中华、蒙古、埃及、阿兹特克、罗马、希腊。

### Step 4. 复制GameId
创建游戏后，GameId将自动复制到您的粘贴板;或者你可以在多人游戏界面中看到你创建的游戏

### Step 5. 在Discord进行外交对话
[CivAgent Discord](https://discord.com/channels/@me/1196286976639369297)

### Step 6 (可选). 使用GPT4等大模型提升AI体验
目前默认的AI服务使用了免费的大模型服务，如果您想要更好的游戏体验，可以订阅OPENAI的GPT4服务。


## 🙋 开发动机&讨论
### 致策略游戏玩家
在策略游戏中，多人游戏的游戏体验和电脑AI不可同日而语，这是由于human players的战略决策更加合理，外交手段更加丰富，并可以运用自然语言进行谈判和欺骗。一个典型的例子是，当A国和B国在旷日持久的战争之后，一个新的征服者C国的出现是否可以促使A国和B国的和平。更进一步的，被C国宣战的B国是否愿意以一定代价向A国投降，而A国又是否有足够的智慧放弃苛刻的要求。然而,对一局比赛长达十几个小时甚至几天的策略游戏的玩家来说，寻找朋友进行多人游戏联机是非常困难的。在这个项目中，我们被完美的开源游戏Unciv所吸引，并非常荣幸地尝试为玩家构建基于LLM的数字玩家作为真人对手的替代。您可以阅读教程xx来接入我们的游戏服务器，并在飞书上和您游戏中的国家进行外交谈判。请参考游戏安装文档。


### 致LLM-based Agent研究者
One of LLM-based Agent exciting prospect is their application across various industries as domain-specific human-like proxies,commonly referred to as “digital employees”. However, it is hard for non-commercial researchers to establish a data flywheel for their agent. 在这个项目中，我们提供了基于Unciv游戏的环境CivSim，您可以开发您自己的Agent并邀请玩家接入您的服务器。这为构建低成本数据飞轮来不断迭代Agent提供了可能。请参考我们的论文和开发者文档。
基于大型语言模型(LLM)的智能体的一个令人兴奋的前景是它们作为特定领域的人类代理在各个行业中的应用，通常被称为“数字员工”。然而，非商业研究人员很难为他们的智能体建立数据飞轮的循环。在这个项目中，我们提供了基于Unciv游戏的环境CivSim，您可以开发您自己的Agent并邀请玩家接入您的服务器。这为构建低成本数据飞轮来不断迭代Agent提供了可能。请参考我们的论文和开发者文档。


### 致对AI Native Game感兴趣的游戏开发者:
Generative Agents(斯坦福小镇)引起了游戏工业界关于AI原生游戏的思考，除了为NPC提供对话功能，大语言模型（LLM）还能被用于游戏设计。一时间，“无限创造内容的 AI 游戏”、“理解一切的 AI NPC”等概念甚嚣尘上。
经过1年多的探索，人们发现
1.不是所有游戏都需要AI NPC。玩家更需要高质量的高星角色、boss战、主线剧情，另外网游中已经有足够多真人玩家互相交互。
2.NPC聊天功能(人设对话)往往并不涉及游戏的核心玩法，除了对话，AI NPC还需要在决策上体现出高度智能。然而，大模型在语意空间挥斥方遒，但游戏是有限的，特别是美术资源有瓶颈。NPC想下毒，但游戏没有下毒功能，更没有对应的动作动画；
3.AI NPC决策(反应)系统中，大模型可以替代策划配表和行为树。但当决策空间很有限时，大模型来做的意义不大。GTA、荒野大镖客2、博德之门3靠堆料实现开放世界。只有决策和状态空间大到人力不足(先解决美术资源问题)，才需要大模型作为常识和决策引擎。

我们认为沙盒游戏才能做出真正的AI Native Game，而SLG策略游戏更能适合当前的技术能力。
1.SLG策略游戏的状态和决策空间非常大，《欧陆风云4》的外交决策包括20多种。策略游戏天生对美术资源要求低，有时只需要一个状态栏。
2.决策空间多了以后，"涌现"的难点难于机制交叉和体验可控。而SLG天生便于涌现；《文明》的军事、科研、文化、宗教互相转化。声东击西=时空上的移动；合纵连横；假道灭虢=宣战+移动+承诺
3.自由对话恰好对SLG有特殊意义，以前只有真人玩家可以做到。没有对话，劝说、欺骗、威胁等玩法就体现不出来
4.AI原生游戏需要完成共创。大模型、Agent需要用户反馈数据，构建数据飞轮(如StableDiffusion文生图)。沙盒游戏适合二创、病毒营销、开发上容易增加游戏规则/元素。未来AI自动生成行为树、Lua代码(沙盒世界规则)。
欢迎来信讨论。



## 🌐 社区
| Channel  | Link |
|:---------|:-|
| Unciv    | [GitHub](https://github.com/yairm210/Unciv) |
| 论文       | [Paper](https://openreview.net/forum?id=AuT65qKLrr) |
| 邮箱       | [Mail](asdqsczser@gmail.com) |
| Issues   | [GitHub Issues](https://github.com/fuxiAIlab/CivAgent/issues) |
| 伏羲实验室    | [Fuxi HomePage](https://fuxi.163.com/en/) |
| Our Team | [Open-project](https://fuxi-up-research.gitbook.io/open-project/) |

 
## 📖 作者和引用

**Authors:** [王凯](https://scholar.google.com/citations?user=nrKSdzcAAAAJ&hl=en) (AI研究员, 网易伏羲实验室) 和 [王嘉伟](https://scholar.google.com/citations?user=pOxT1NAAAAAJ&hl=zh-CN) (中国科学院大学硕士在读, 实习期间完成)

欢迎引用我们的论文。

```
@misc{
anonymous2024digitalplayer,
title={Digital Player: Evaluating Large Language Models based Human-like Agent in Games},
author={Jiawei Wang and Kai Wang and Runze Wu and Bihan Xu and Lingeng Jiang and Shiwei Zhao and Renyu Zhu and Haoyu Liu and Zhipeng Hu and Zhong Fan and LILE and Tangjie Lv and Changjie Fan},
year={2024},
url={https://openreview.net/forum?id=AuT65qKLrr}
}
```