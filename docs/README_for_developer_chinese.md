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
如果你想在多人在线游戏中使用本地大模型代理，那么你需要打开我们提供的本地游戏AI服务器。下面是具体步骤:

### Step 1. 打开服务器
游戏AI服务器是Flask实现的，因此需要启动Flask服务器。然后运行下面的命令:

    python flask_server.py

### Step 2. 游戏文件修改
请修改游戏文件DebugUtils.kt中的配置。如下:
```
var NEED_POST: Boolean = true
```
如果你已经做到了这一点，那么恭喜你，你已经将游戏中的决策链接到本地服务器了。如果你想定制自己的外交政策决定，请继续阅读。
### Step 3. 自定义决策模块
在现有的游戏AI服务器中，决策模块的原型是现有的游戏行为树。如果您是想进一步研究和制定外交政策决策的开发人员或研究人员，我们提供示例供参考。

例子如下:
```python
def get_wantsToSignDeclarationOfFrienship(gameinfo, civ1_name, civ2_name):
    '''
        Retrieves whether a civilization wants to sign a declaration of friendship with another civilization.
        Args:
        gameinfo: String representing game information
        civ1_name: Name of the first civilization
        civ2_name: Name of the second civilization
        Returns:
        json_data: A JSON string containing the result and reason for the declaration of friendship
    '''
    game = uncivFiles.gameInfoFromString_easy(gameinfo)
    uncivGame.setGameInfo(game)
    uncivGame.Current = uncivGame
    civ1 = game.getCivilization(civ1_name)
    civ2 = game.getCivilization(civ2_name)
    reason = DiplomacyAutomation.INSTANCE.wantsToSignDeclarationOfFrienship_easy(civ1, civ2)
    python_reason = [str(item) for item in reason.getSecond()]
    pair_dict = {"result": bool(reason.getFirst()), "reason": python_reason}
    json_data = json.dumps(pair_dict)
    return json_data
```
` get_wantstosigndeclarationfriendship `这是一个确定双方是否可以签署友谊声明的函数。在游戏中，做出一个决策请求，请求中的信息包含游戏存档信息`gameinfo`、文明1的名称`civ1_name`和文明2的名称`civ2_name`。函数体调用Jar包中的行为树决策，最终返回一个json文件，其中包含决策结果和决策原因。

开发人员可以用自定义的方式重写函数体，只要返回格式保持一致。