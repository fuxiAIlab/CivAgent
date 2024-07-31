# 二次开发文档 

<p align="center" width="100%">

##   配置开发环境
### 安装jdk
这里推荐[temurin-21-jdk](https://adoptium.net/temurin/releases/)
如果您使用的是linux ubuntu系统，可以使用以下命令安装
```
apt install ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /etc/apt/keyrings/adoptium.gpg
chmod a+r /etc/apt/keyrings/adoptium.gpg
echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list
apt update -y
apt install temurin-21-jdk
```

### 安装Ollama
首先，下载最新版本的[Ollama](https://ollama.com/)。您可以使用下面提供的链接为您的系统下载Ollama。

Mac : [Please click here to download](https://ollama.com/download/Ollama-darwin.zip)


Windows : [Please click here to download](https://ollama.com/download/OllamaSetup.exe)

Linux:
```
curl -fsSL https://ollama.com/install.sh | sh
```

安装完成后，开启Ollama并下载实验用到的开源大模型:
```
ollama pull mistral
ollama pull llama3
ollama pull gemma
```

### 安装python相关包
我们在Python 3.9.12上测试了我们的环境。
```
pip install -r requirements.txt
pip install llama_index.embeddings.ollama
```

##   模型配置
这个游戏支持访问各种大型模型，我们提供两种方法来调用大型模型。1. 调用OpenAi的服务。2. 在本地部署大型模型。在这里，我们将介绍如何配置这两种方法。

###  使用OpenAI的服务
如果您需要调用OpenAI的服务，您只需要在`scripts/tasks/config.yaml`的API处填写您的密钥即可。[here](#step-4-configuration-model-information).
```
# config.yaml
LLM:
  openai_api_key: <Your-api-key>
```
###  使用Ollama部署本地模型
[Ollama](https://ollama.com/) 是一个轻量级的服务，可以轻松安装到所有平台，使开发人员在本地获得LLM变得轻而易举。介绍使用Ollama安装LLM的操作步骤。


### 在本地建立并运行大型语言模型

Ollama支持可用的模型: [ollama.com/library](https://ollama.com/library 'ollama model library'),
你可以转到查看你想要的模型的链接，然后在终端中输入以下命令来加载和运行模型。
```
ollama run <Your-model-name>
# example:
  ollama run mistral
  ollama run llama2
```
###  配置模型信息
下载并运行Ollama后，您需要配置项目中每个文明使用的模型信息，以便在游戏中正确使用模型。在`scripts/tasks/config.yaml`中输入模型名称。
```
# config.yaml
aztecs:
  model: <Your-model-name>
# example:
aztecs:
  #Use the OpenAI
    model: 'gpt-3.5-turbo-1106'
aztecs:
  #Use the Ollama
    model: 'mistral'
```

### 支持的模型参数
目前我们的benchmark支持以下模型型号:
```
OpenAI系列(含兼容):
  -  gpt-3.5-turbo-1106
  -  gpt-4-1106-preview
  -  deepseek
  -  其他兼容模型
  
Ollma本地大模型:
  -  Ollama所支持的所有开源大模型型号
```
欢迎大家使用deepseek来体验我们的benchmark(仅供测试,deepseek为中文大模型)。

##  运行实验

###  运行 Benchmark
注意，在本实验中，研究人员可以自由选择CivAgent使用的工作流配置。下面是参数和示例:

```
#parameters:
python3 <Path> <Mode> <GameInfo> <Turns> <key words> <Name> <Model> <Workflow> <Simulation> <Reflection> ......

#example:
python3 run_benchmark.py back ../reproductions/Autosave 50 declare_war aztecs gpt3.5 True True True greece gpt3.5 True True False rome gpt3.5 True False False egypt gpt3.5 False False False
```
具体参数见下表:

| Parameters| Introduction| 
|-------|-------|
| Path |  Experiment file path|
| Mode| Patterns of reflection (back or none) |
| GameInfo |Path to the game save |
| Turns | Maximum number of decision turns in the game（The decision is made once in five rounds）|
| Key words | Reflect on the keywords used|
| Name | The Name of Civilization |
| Model | The model used by the civilization |
| Workflow | Whether workflows are required |
| Simulation | Whether simulation are required |
| Reflection | Whether reflection are required |
###  运行 Bargain task
讨价还价任务的运行过程如下:
```
#parameters:
python3 <Path> <GameInfo> <Buyer name> <Buyer Model> <Seller name> <Seller Model>

#example:
python3 run_bargain_task.py ../reproductions/Autosave-China-60 rome gpt4 china gpt4
```
我们还提供了一个与人类对话的版本，只需重写文件路径并将模型改为human。下面是一个例子:
 ```
python3 run_bargain_task_speak.py ../reproductions/Autosave-China-60 rome gpt4 china human
```
具体参数见下表:

| Parameters   | Introduction| 
|--------------|-------|
| Path         |  Experiment file path|
| GameInfo     |Path to the game save |
| Buyer name   | The name of the buyer |
| Buyer Model  | The model used by the buyer |
| Seller name  | The name of the seller |
| Seller Model | The model used by the seller |

###  运行 cheat task
欺骗任务的运行过程如下:
```
#parameters:
python3 <Path> <GameInfo> <Cheat Model> <Recognition Model>

#example:
python3 run_cheat_task.py ../reproductions/Autosave-China-60 gpt4 gpt4
```
我们还提供了一个与人类对话的版本，只需重写文件路径并将模型改为human。下面是一个例子:
 ```
python3 run_cheat_task_speak.py ../reproductions/Autosave-China-60 gpt4 gpt4
```
具体参数见下表:

| Parameters| Introduction| 
|-------|-------|
| Path |  Experiment file path|
| GameInfo |Path to the game save |
| Cheat Model | The model used by the cheater |
| Recognition Model | The model used by the recognizer |
##   使用本地AI服务器
如果你想在在游戏界面中体验我们的benchmark，那么你需要打开我们提供的本地游戏AI服务器。下面是具体步骤:
### Step 1. 下载游戏
Mac客户端下载地址是 https://drive.google.com/file/d/1Ohx6pvcdZbVzte0cAaXPHEAIRpJ2obqK/view?usp=sharing

Windows客户端下载地址是 https://drive.google.com/file/d/1ap99uZnhcpgIkDgJKAaPk277bTBi34Ag/view?usp=sharing

请根据你的操作系统下载对应的游戏客户端。
### Step 2. 模型设置
在游戏中，你需要配置CivAgent的基本参数。在`scripts/tasks/config.yaml`中设置(前面有所介绍)。
### Step 3. 运行游戏
Windows: 点击Unciv.exe文件，然后进入游戏。

Mac: 点击Unciv.jar文件，可以直接进入游戏。我们还额外提供了一个命令行启动方式，可以直接设置`DebugUtils.kt`中的变量，以下是变量的介绍：

| Parameters   | Introduction| Types
|--------------|-------|-------|
| NEED_POST         | Use the AI module via http request, set false when build jar for simulator|Boolean|
| NEED_GameInfo     | Pass gameinfo with each interface request. Enabling this would increase processing time |Boolean|
| SIMULATE_UNTIL_TURN   | Simulate until this turn on the first "Next turn" button press. |Boolean|
| AI_Server_Address  | Set the game's AI server address |String|
| LLM_API_KEY  | Set the API KEY used by the LLM, Can be empty |String|
| LLM_MODEL | Set up the model using LLM, Can be empty|String|
| CONNECT_TIMEOUT  | Set a timeout limit for invoking LLM |Int|
以下是一个例子：
```
#采取默认的配置
java -jar Unciv.jar 
#设置参数
java -jar Unciv.jar NEED_POST=true AI_Server_Address=http://127.0.0.1:2337/
```
在创建游戏的界面，你需要做以下设置：
```
1.将城邦数量设置为0
2.将多人在线游戏关闭
```
### Step 4. 打开服务器
游戏AI服务器是Flask实现的，因此需要启动Flask服务器。然后运行下面的命令:
```
cd deployment/ai
python ai_server.py

默认端口: http://127.0.0.1:2337/
```
如果你已经做到了这一点，那么恭喜你，你已经将游戏中的决策链接到本地服务器了。这时你已经可以开始体验我们的benchmark了。
### Step 5. 决策可视化
在服务器终端界面，你可以看到游戏中的发送来的决策请求。

在`Log`文件夹中查看日志你可以看到游戏中各CivAgent的技能选择、科技选择、生产选择，以及外交决策信息。

如果你想定制自己的外交决策模块，请继续阅读。
### Step 6. 自定义决策模块
在现有的游戏AI服务器中，决策模块的原型是现有的游戏行为树。如果您是想进一步研究和制定外交决策的开发人员或研究人员，我们提供示例供参考。

在游戏文件的`DebugUtils.kt`中，我们提供了名为`NEED_GameInfo`的开关，用于控制是否将完整的游戏存档传递给服务器。如果你想要传递完整游戏存档信息，你需要设置为`True`，否则设置为`False`。若设置为`False`，游戏存档信息会是含有游戏ID的字典。

现有的服务器中我们提供了两种AI服务：
```
use_ai == 'civagent'  # 使用LLM进行决策
use_ai == 'native_unciv'  # 使用原生的游戏行为树进行决策 
注意：在use_ai == 'native_unciv'的情况下，NEED_GameInfo的值需设置为True。
```

在目前的AI服务器中，以下函数是会收到该开关的影响，其余函数默认会收到完整的游戏存档：
```python
canSignResearchAgreementsWith()
wantsToSignDefensivePact()
hasAtLeastMotivationToAttack()
wantsToSignDeclarationOfFrienship()
chooseTechToResarch()
chooseNextConstruction()
hasAtLeastMotivationToAttack()
commonEnemy()
buyLuxury()
```
您可以定义自己的外交决策函数，函数的参数和返回值需要与现有的函数保持一致。具体的函数例子如下:
```python
def wantsToSignDeclarationOfFrienship(gameinfo, civ_name_1, civ_name_2, game_skill_data):
    """
        Assessing whether our civilization can sign a declaration of friendship with the target civilization.
        Parameters:
            gameinfo: String
                If the game launcher parameter NEED_GAMEINFO == True, then gameinfo represents the game save information.
                Otherwise, it is represented as a gameid (Unique identifier of the game).
            civ_name_1: String
                The name of our civilization. Active party.
            civ_name_2: String
                The name of the target civilization. Passive party.
        Returns:
            if use_ai == 'civagent':
                String: A JSON string containing the result of being able to sign a declaration of friendship.
            if use_ai == 'native_unciv':
                String: A JSON string containing the result and reason for being able to sign a declaration of friendship.
        Example:
            if use_ai == 'civagent':
                wantsToSignDeclarationOfFrienship(gameinfo, rome, greece) => {"result": "false"}
            if use_ai == 'native_unciv':
                wantsToSignDeclarationOfFrienship(gameinfo, rome, greece) => {"result": "true", "reason": "Rome has a high level of trust with Greece."}
    """
    if use_ai == 'civagent':
        return get_skills(
            "change_closeness", civ_name_1, civ_name_2, game_skill_data
        )
    elif use_ai == 'native_unciv':
        return simulator.wantsToSignDeclarationOfFrienship(
            gameinfo, civ_name_1, civ_name_2
        ), {}
    else:
        # todo write your custom ai
        raise
```
` wantstosigndeclarationfriendship `这是一个确定双方是否可以签署友谊声明的函数。在游戏中，做出一个决策请求，请求中的信息包含游戏存档信息`gameinfo`、文明1的名称`civ1_name`和文明2的名称`civ2_name`。函数体调用Jar包中的行为树决策，最终返回一个json文件，其中包含决策结果和决策原因。

开发人员可以用自定义的方式重写函数体，只要返回格式保持一致。

##   部署你自己的游戏服务器和聊天服务器，邀请远程玩家接入
(注：需要与上部分ai服务器搭配使用, 对外开放服务需开发者自行准备域名)
###Redis设置
项目使用了Redis内存数据库作为多个应用传递信息的中间数据库。在本地部署时，需要配置Redis数据库。Redis数据库的安装教程可以参考[Redis官网](https://redis.io/)。
下载版本需要5.0及以上。

在`config.py`文件中，我们提供了Redis数据库的配置信息，开发者需要根据自己的Redis数据库配置信息进行修改。
```
#config文件中的需要配置信息如下：
Redis:
  host: 
  port: 
  db: 
  password: 
```

### 游戏服务器设置与启动
游戏服务器用于在线多人对战模式，玩家可以通过该服务器进行多人游戏。这边提供开发者可自行部署本地的游戏服务器。
在`deployment\unciv_server`文件中，我们提供了游戏服务器的源码，本地部署只需运行以下命令：
```
nohup python unciv_server.py -p 2333 -g -l WARNING >> unciv_server.out 2>&1 &
```
在游戏设置界面选择多人游戏，在选项处将服务器地址改为你自己的服务器地址即可。

### Chat server设置与启动
聊天功能是游戏中的一个重要功能，玩家可以通过聊天功能进行实时交流。在`deployment\chatbot\chat_server`文件中，我们提供了聊天服务器的源码。
在`config.py`文件中, 我们提供了聊天服务器的配置信息，开发者需要根据自己的聊天服务器配置信息进行修改。
```
#config文件中的需要配置信息如下,开发者需要将chat_server的url改为自己设置的服务器地址，这会用于后续与聊天软件的连接。
chat_server:
  url: http://127.0.0.1:2337/
```

配置好以上后，本地部署只需运行以下命令：
```
nohup python chat_server.py >> chat_server.log 2>&1 &
```
###Mq listener设置与启动
mq_listener是用于触发事件回复、主动对话以及自由对话的服务模块，它会监听redis中的消息队列，条件满足时向ai服务器发送相应的请求。
需要开发者在`config.py`文件中配置ai服务器的信息，如以下所示:
```
#填入ai_server的url，用于连接ai服务器
ai_server:
  url: http://127.0.0.1:2335/
```
配置完以上，运行以下命令即可：
```
nohup python mq_listener.py >> mq_listener.log 2>&1 &
```

### Discord server设置与启动
Discord是一款非常流行的聊天软件，我们提供了与Discord服务器的连接。在`chatbot\discord\discord_server`文件中，
我们提供了我们Discord服务器的源码，开发者可以自行部署本地的Discord服务器。若开发者想要在自己的Discord上进行调试和开发，需要自行前往Discord官网创建自己的服务器频道，并创建对应的机器人。

服务器id可以从Discord服务器设置中获取，机器人的token和id可以从[Discord开发者网站](https://discord.com/developers/applications)获取。
最后将服务器频道id，机器人的token和id填入discord_server文件中，如以下所示：
``` 
#填入对应的服务器频道id，机器人token和id，用于连接Discord服务器
#Unciv_Bot为管理员机器人，mongolia、china、rome、aztecs、greece、egypt为文明机器人
BotToken = {
    'Unciv_Bot': 
    'mongolia': 
    'china': 
    'rome': 
    'aztecs': 
    'greece':
    'egypt': 
}

discord_robot2id = {
    'Unciv_Bot': 
    'mongolia': 
    'china': 
    'rome': 
    'aztecs': 
    'greece': 
    'egypt': 
}
default_guild_id = 1194463544666755204
``` 
配置完以上，运行以下命令即可：
```
nohup python discord_server.py >> discord_server.log 2>&1 &
```
完成以上步骤后Discord服务器就已经启动了，开发者可以在自己的Discord上进行调试和开发。



