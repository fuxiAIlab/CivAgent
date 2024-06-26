# CivAgent: Large Language Models based Human-like Agent

English | [中文](README_chinese.md) |
<p align="center" width="100%">

[![Demo Video](https://res.cloudinary.com/marcomontalbano/image/upload/v1719391630/video_to_markdown/images/youtube--AapuuHgzXqE-c05b58ac6eb4c4700831b2b3070cd403.jpg)](https://www.youtube.com/watch?v=AapuuHgzXqE "Demo Video")

CivAgent is an LLM-based Human-like Agent acting as a Digital Player within the strategy game [Unciv](https://github.com/yairm210/Unciv).
The project aims to address the difficulty of players not being able to find human playmates, 
and seeks to construct a low-cost data flywheel to aid in the research of LLM-based Agents. 
By deeply integrating Large Language Models (LLMs) with core gameplay, 
we believe this is exactly an AI Native Game. All glory are attributed to Unciv.



Native Unciv: https://github.com/yairm210/Unciv

Unciv Wiki: https://civilization.fandom.com/wiki/Unciv

Unciv We Used Download (released in early July)

Unciv We Used (source code): https://github.com/asdqsczser/Unciv/tree/release/fuxi_ver

Paper: https://openreview.net/forum?id=AuT65qKLrr

Appendix: https://github.com/fuxiAIlab/CivAgent/blob/main/paper_appendix.pdf

YouTube: https://www.youtube.com/playlist?list=PL9G00-od8ezYNblsqMca7urrLoHSZ7Vs3

## News
![new](/assets/new.gif) **06/20/2024**: Code for benchmark reproduction (developer version) of research paper is open-sourced. The version for players is expected to be released in early July.

**06/09/2024**: The paper is submitted to NeurIPS 2024 Track Datasets and Benchmarks, [Under Review](https://openreview.net/forum?id=AuT65qKLrr).


## 👨‍💻 Developers
Please refer to [Documentation](/docs/README_for_developer_chinese.md).

## ⚡ How to play
The AI service can only be used in the multiplayer game mode and is only supported on the Windows and Mac platform.


**Note that your save files and chat data will be collected by the server (no personally identifiable data) and used for non-commercial purposes (AI effect improvement for this project).**
### Step 1. Download the game client
Released in early July.


### Step 2. Set the server address
Open the game, navigate to the 'Options' and 'Multiplayer' interface, adjust the synchronization frequency to 3 seconds, modify the server address to http://sl.office.fuxi.netease.com:44952 and test the link.

### Step 3. Start a new game
Open the 'Start new game' interface, check the 'Online Multiplayer' option in the bottom left corner. It is recommended to begin with the 'Medieval era'. On the right, please click on 'Set current user', and select a civilization from the following civilizations: China, Mongolia, Egypt, Aztecs, Rome, or Greece.

### Step 4. Copy the GameId
After creating the game, the GameId will be automatically copied to your clipboard, or you can find the GameId of the game you created in the multiplayer game interface.

### Step 5. Chat with civilizations on the Discord
[CivAgent Discord](https://discord.com/channels/@me/1196286976639369297)

### Step 6 (optional). Enhancing AI experience using LLMs such as GPT-4
The current default AI service utilizes the free large-scale model. For an enhanced gaming experience, you may consider subscribing to OPENAI's GPT-4 service.






## 🙋 Motivation & Discussion
### To Fans of Strategy Games
In strategy games, the experience of multiplayer gameplay is much better than that of computer AI, primarily due to the fact that human players make more rational strategic decisions, have a flexible diplomatic strategy, and can employ natural language for negotiation and deception.
A typical example is when the emergence of a new conqueror, Country C, after a prolonged war between Country A and Country B, may potentially prompt peace between A and B.
Furthermore, if Country B, which has been declared war upon by Country C, is willing to surrender to Country A at a certain cost, and whether Country A is wise enough to relinquish stringent demands.
However, for players of strategy games where every match can last for dozens of hours or even days, finding friends for multiplayer gaming is exceptionally challenging.
In this project, we were drawn to the excellent open-source game Unciv and are honored to attempt to construct a digital player based on LLM as a substitute for human opponents.
You can refer to the tutorial to join our game server and engage in diplomatic negotiations with the civilization in your game on Discord.


### To Developer/Researcher of LLM-based Agent
One of LLM-based Agent exciting prospect is their application across various industries as domain-specific human-like proxies,commonly referred to as “digital employees”. However, it is hard for non-commercial researchers to establish a data flywheel for their agent.
In this project, we introduce the CivSim environment, which is based on the Unciv game. CivSim allows researcher to develop their own agent and invite players to join their AI server. This provides the potential for creating a low-cost data flywheel to iteratively improve agents.
Please refer to our research paper and developer documentation for more details.


### To game developers interested in AI Native Game:
The advent of Generative Agents has sparked a discourse within the gaming industry regarding AI-native games. Beyond equipping NPCs with conversational abilities, Large Language Models (LLMs) have also been considered for game design purposes (i.e., LLMs for gameplay). Concepts such as "AI-powered games capable of infinite content creation" and "AI NPCs that understand everything" have gained significant attention.
After more than a year of exploration, several findings have emerged:
1. Not all games necessitate the presence of AI NPCs. Players often prioritize high-quality characters, boss battles, and main storylines; moreover, online multiplayer games already provide ample opportunities for interaction among human players.
2. While NPC chat functions (character dialogues) usually not be central to gameplay mechanics, there is an expectation for AI NPCs to demonstrate advanced intelligence in decision-making processes. Although LLMs can encode anything and decode reasonably, they are constrained by the finite resource of games—particularly when it comes to art resources limitations. For instance, if an NPC intends to poison another character but the game lacks both poisoning functionality and corresponding animation assets;
3. Within AI NPC decision-making (reaction) systems, LLMs could potentially replace manual configuration excels and behavior trees used by designers. However, when decision spaces are limited, employing large models becomes less meaningful or necessary. We haven't even considered the cost of LLMs yet. Open-world experiences like those found in GTA V, Red Dead Redemption 2, or Baldur's Gate III rely on extensively crafted content.
   Only when both decision and state spaces become so vast that human efforts fall short—and after addressing art resource constraints—would LLMs serve as essential engines for common sense reasoning and NPC decision-making.

We posit that sandbox games are the ideal platform for creating true AI Native Games, while SLG (Simulation & Strategy Game) games are better for several reasons:
1. First, The best news for LLM usage are the scarcity of NPCs and the criticality of NPC decision-making in SLG games. Concurrently, most decisions within these games do not necessitate immediate responses. These characteristics mitigate some of the primary limitations associated with current LLM implementations.
2. The state and decision space in SLG strategy games is too large to designing a proficient rule-based AI; for instance, "Europa Universalis IV" features over twenty types of diplomatic decisions. Strategy games inherently have lower artistic resource requirements—sometimes only a status bar is needed.
3. With an expanded decision space comes increased difficulty in managing "emergent gameplay" due to intersecting mechanisms and maintaining controllable experiences. However, SLGs naturally facilitate emergence; in "Civilization", military prowess, scientific research, culture, and religion can all interconvert. And in strategic decision-making, Deceptive strategies such as "the elimination of a nation that has granted military passage rights without vigilance" can be achieved through a sequence decisions involving declaration of war, request for military access, and surprise attack.
4. Free dialogue holds special significance in SLGs—a feature previously only achievable by human players. Without dialogue, gameplay involving persuasion, deception, threats cannot be fully realized.
5. AI-native gaming necessitates co-creation with players where LLMs and agents require user feedback data to build a data flywheel (akin to Stable Diffusion). Sandbox games are conducive to secondary creation (modding), viral marketing campaigns, and ease of adding new game rules/elements during development phases. In the future, AI could automatically generate behavior trees or game code (rules for sandbox worlds).



## 🌐 Community
| Channel  | Link |
|:---------|:-|
| Unciv    | [GitHub](https://github.com/yairm210/Unciv) |
| Paper    | [Paper](https://openreview.net/forum?id=AuT65qKLrr) |
| Mail     | [Mail](asdqsczser@gmail.com) |
| Issues   | [GitHub Issues](https://github.com/fuxiAIlab/CivAgent/issues) |
| FUXI Lab | [Fuxi HomePage](https://fuxi.163.com/en/) |
| Our Team | [Open-project](https://fuxi-up-research.gitbook.io/open-project/) |


## 📖 Authors and Citation

**Authors:** [Wang Kai](https://scholar.google.com/citations?user=nrKSdzcAAAAJ&hl=en) (AI Researcher, Netease Fuxi Lab) and [Wang Jiawei](https://scholar.google.com/citations?user=pOxT1NAAAAAJ&hl=zh-CN) (master candidate at the University of Chinese Academy of Sciences, completed during internship)

Welcome to cite our paper.

```
@misc{
anonymous2024digitalplayer,
title={Digital Player: Evaluating Large Language Models based Human-like Agent in Games},
author={Jiawei Wang and Kai Wang and Runze Wu and Bihan Xu and Lingeng Jiang and Shiwei Zhao and Renyu Zhu and Haoyu Liu and Zhipeng Hu and Zhong Fan and LILE and Tangjie Lv and Changjie Fan},
year={2024},
url={https://openreview.net/forum?id=AuT65qKLrr}
}
```