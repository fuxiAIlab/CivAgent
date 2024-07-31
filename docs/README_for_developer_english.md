# Digital Player: Evaluating Large Language Models based Human-like Agent in Games

<p align="center" width="100%">

![unciv](assets/img.png)

## Entrance

### If you're a player, start  [here](#start-the-game)

### If you're a developer or researchers,start [here](#setting-up-the-environment)

## Start the Game

### Step 1. Set server address

Open the game, modify the synchronization frequency and server address in the setting interface; The new server address is: http://sl.office.fuxi.netease.com:44952

### Step 2. Set the game

On the Start new game screen, check 'Online Multiplayer' in the lower left corner; It is recommended to start from 'Medieval Times', please click' Set as Current player ', click the question mark on the right to select a civilization, the optional civilization includes 【 Chinese 】【 Mongol 】【 Egyptian 】【 Aztec 】【 Roman 】【 Greek 】

### Step 3. Copy the gameid

After creating the game, the gameid is automatically copied to your paste board; Or you can see the game you created in the 'Multiplayer' screen

### Step 4. Chat in discord

[CivAgent Discord](https://discord.com/channels/@me/1196286976639369297)



## Setting Up the Environment
### Install Java JDK
We recommend [temurin-21-jdk](https://adoptium.net/temurin/releases/)
If you are using the Linux Ubuntu system, you can use the following command to install:
```
apt install ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /etc/apt/keyrings/adoptium.gpg
chmod a+r /etc/apt/keyrings/adoptium.gpg
echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list
apt update -y
apt install temurin-21-jdk
```

### Install Ollama
First, Download [Ollama](https://ollama.com/):

Mac : [Please click here to download](https://ollama.com/download/Ollama-darwin.zip)

Windows : [Please click here to download](https://ollama.com/download/OllamaSetup.exe)

Linux:
```
curl -fsSL https://ollama.com/install.sh | sh
```

After installation, open Ollama and download the open-source LLMs required for the experiment.
```
ollama pull mistral
ollama pull llama3
ollama pull gemma
```

### Install python packages
We test the environment on Python 3.9.12.
```
pip install -r requirements.txt
pip install llama_index.embeddings.ollama
```


## Model configuration

This game supports access to a variety of large models, we provide two methods to call the large model. 1. Invoking OpenAi services. 2. Deploy large models locally.

### Use the services we provide

If you need to call OpenAI's service, you only need to fill in your API key in `scripts/tasks/config.yaml`.[here](#step-4-configuration-model-information).
```
# config.yaml
LLM:
  openai_api_key: <Your-api-key>
```

### Deploy LLM using Ollama

[Ollama](https://ollama.com/) is a lightweight service that can be easily installed to all platforms, making it a breeze for developers to get LLM locally. This section describes how to install LLM using Ollama.
###Download Ollama
First, download the latest version of Ollama. You can download Ollama using the link provided below for your system.

Mac : [Please click here to download](https://ollama.com/download/Ollama-darwin.zip)

Windows : [Please click here to download](https://ollama.com/download/OllamaSetup.exe)

Linux:

```
curl -fsSL https://ollama.com/install.sh | sh
```

[Manual install instructions](https://github.com/ollama/ollama/blob/main/docs/linux.md)

###Get up and running with large language models locally

Ollama supports a list of models available on [ollama.com/library](https://ollama.com/library "ollama model library"),
You can go to the link to view the model you want, and then enter the following command in the terminal to load and run the model.

```
ollama run <Your-model-name>
# example:
  ollama run mistral
  ollama run llama2
```

### Configuration model information

With Ollama downloaded and running, you need to configure the model information used by each civilization in your project in order to use the model correctly in your game. Enter your model name in `./benchmark/config.yaml`.

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
### Supported model parameters
Currently, our benchmark supports the following model types:
```
OpenAI series (including compatible models):
  -  gpt-3.5-turbo-1106
  -  gpt-4-1106-preview
  -  deepseek
  
Large local models:
  -  All supported open-source large model types by Ollama
```
Welcome everyone to use DeepSeek to experience our benchmark (for testing purposes only, DeepSeek is a large Chinese model).

##  Running experiments

### Run benchmark

Note that in this experiment, the researcher is free to choose the workflow configuration used by CivAgent. Here are the parameters and a working example:

```
#parameters:
python3 <Path> <Mode> <GameInfo> <Turns> <key words> <Name> <Model> <Workflow> <Simulation> <Reflection> ......

#example:
python3 run_benchmark.py back ../reproductions/Autosave 50 declare_war aztecs gpt3.5 True True True greece gpt3.5 True True False rome gpt3.5 True False False egypt gpt3.5 False False False
```

The detailed parameters can be seen in the following table:


| Parameters | Introduction                                                                             |
| ------------ | ------------------------------------------------------------------------------------------ |
| Path       | Experiment file path                                                                     |
| Mode       | Patterns of reflection (back or none)                                                    |
| GameInfo   | Path to the game save                                                                    |
| Turns      | Maximum number of decision turns in the game（The decision is made once in five rounds） |
| Key words  | Reflect on the keywords used                                                             |
| Name       | The Name of Civilization                                                                 |
| Model      | The model used by the civilization                                                       |
| Workflow   | Whether workflows are required                                                           |
| Simulation | Whether simulation are required                                                          |
| Reflection | Whether reflection are required                                                          |

### Run bargain task

The bargaining mini-task runs as follows:

```
#parameters:
python3 <Path> <GameInfo> <Buyer name> <Buyer Model> <Seller name> <Seller Model>

#example:
python3 run_bargain_task.py ../reproductions/Autosave-China-60 rome gpt4 china gpt4
```

We also provide a version that talks to humans, just rewrite the file path and rewrite the model as Human. An example is as follows:

```
python3 run_bargain_task_speak.py ../reproductions/Autosave-China-60 rome gpt4 china gpt4
```

The detailed parameters can be seen in the following table:


| Parameters   | Introduction                 |
| -------------- | ------------------------------ |
| Path         | Experiment file path         |
| GameInfo     | Path to the game save        |
| Buyer name   | The name of the buyer        |
| Buyer Model  | The model used by the buyer  |
| Seller name  | The name of the seller       |
| Seller Model | The model used by the seller |

### Run cheat task

The cheating mini-task runs as follows:

```
#parameters:
python3 <Path> <GameInfo> <Cheat Model> <Recognition Model>

#example:
python3 run_cheat_task.py ../reproductions/Autosave-China-60 gpt4 gpt4
```

We also provide a version that talks to humans, just rewrite the file path and rewrite the model as Human. An example is as follows:

```
python3 run_cheat_task_speak.py ../reproductions/Autosave-China-60 gpt4 gpt4
```

The detailed parameters can be seen in the following table:


| Parameters        | Introduction                     |
| ------------------- | ---------------------------------- |
| Path              | Experiment file path             |
| GameInfo          | Path to the game save            |
| Cheat Model       | The model used by the cheater    |
| Recognition Model | The model used by the recognizer |

##  Use a local game ai server
If you want to experience our benchmark within the game interface, you will need to open our provided local game AI server. Below are the specific steps:

### Step 1.  Download the game

Mac: The client download link is https://drive.google.com/file/d/1Ohx6pvcdZbVzte0cAaXPHEAIRpJ2obqK/view?usp=sharing.

Windows: The client download link is https://drive.google.com/file/d/1ap99uZnhcpgIkDgJKAaPk277bTBi34Ag/view?usp=sharing.

Please download the corresponding game client based on your operating system.

### Step 2. Model Configuration
In the game, you need to configure the basic parameters of CivAgent. Set them in `scripts/tasks/config.yaml` (as introduced earlier).

### Step 3. To run the game

Windows: Click on the Unciv.exe file, then enter the game.

Mac: Click on the Unciv.jar file, then enter the game.
We also provide an additional command line startup method, which allows direct configuration of variables in `DebugUtils.kt`. Here is an introduction to the variables:

| Parameters   | Introduction| Types
|--------------|-------|-------|
| NEED_POST         | Use the AI module via http request, set false when build jar for simulator|Boolean|
| NEED_GameInfo     | Pass gameinfo with each interface request. Enabling this would increase processing time |Boolean|
| SIMULATE_UNTIL_TURN   | Simulate until this turn on the first "Next turn" button press. |Boolean|
| AI_Server_Address  | Set the game's AI server address |String|
| LLM_API_KEY  | Set the API KEY used by the LLM, Can be empty |String|
| LLM_MODEL | Set up the model using LLM, Can be empty|String|
| CONNECT_TIMEOUT  | Set a timeout limit for invoking LLM |Int|

Here is an example:

```
# Adopt the default configuration.
java -jar Unciv.jar 
# Set the parameters.
java -jar Unciv.jar NEED_POST=true AI_Server_Address=http://127.0.0.1:2337/
```

In the game creation interface, you need to make the following settings:
```
1. Set the number of city-states to 0.
2. Turn off multiplayer online games.
```
### Step 4. Open the server
The game AI server is implemented using Flask, so you need to start the Flask server. Then run the following command:
```
cd deployment
python ai_server.py

Default port : http://127.0.0.1:2337
```
If you have achieved this, congratulations, you have successfully linked the decision-making in the game to the local server. At this point, you can begin experiencing our benchmark.
### Step 5. Decision Visualization
In the server terminal interface, you can see the decision requests sent from the game.

In the `Log` folder, you can view the logs to see the skill selections, technology choices, production selections, and diplomatic decision information for each CivAgent in the game.

If you want to customize your own diplomatic decision module, please continue reading.
### Step 6. Customize the decision module

In the existing game decision server, the prototype of the decision module is the existing game behavior tree. If you are a developer or researcher who would like to further research and develop foreign policy decisions, we provide examples for reference.


In the game file `DebugUtils.kt`, we have provided a switch called `NEED_GameInfo` to control whether the complete game save file is passed to the server. If you want to pass the complete game save file information, you need to set it to `True`; otherwise, set it to `False`. If set to `False`, the game save information will be a dictionary containing game id.

The existing server provides two types of AI services:
```
use_ai == 'civagent'  # Making decisions using LLM
use_ai == 'native_unciv'  # Making decisions using the native game behavior tree
Note: When use_ai == 'native_unciv', the value of NEED_GameInfo should be set to True.
```
In the current AI server, the following function will be affected by this switch, while the rest will receive the complete game save by default:
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
You can define your own diplomatic decision-making function, ensuring that its parameters and return values remain consistent with the existing functions. An example of the function is as follows:
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
`wantsToSignDeclarationOfFrienship`This is a function to determine whether the two parties can sign a declaration of friendship. In the game, a decision request is made, and the information in the request contains the game archive information`gameinfo`, the name of Civilization 1`civ1_name`, and the name of Civilization 2`civ2_name`. The function body calls the behavior tree decision in the Jar package, and finally returns a json file containing the decision result and the reason for the decision.

The developer can rewrite the function body decision in a custom way, as long as the return format is consistent.

##   Deploy your own game server and chat server and invite remote players to connect
(Note: It needs to be used with the above ai server, and developers need to prepare their own domain name for open services)
###Redis Settings
Local deployment requires Redis database configuration. You need to install the Redis database locally. The installation instructions for Redis database can be found on the [Redis website](https://redis.io/).
5.0 and above is required for download.

In the `config.py` file, we provide the Redis database configuration information, developers need to change according to their own Redis database configuration information.
```
# The config file requires the following configuration information:
Redis:
  host: 
  port: 
  db: 
  password: 
```
###Game server setup and startup
The game server is used for online multiplayer battle mode, and players can play multiplayer games through the server. Here, developers can deploy their own local game server.
In the`deployment\unciv_server` file, we provide the source code for the game server. To deploy locally, run the following command:
```
nohup python unciv_server.py -p 2333 -g -l WARNING >> unciv_server.out 2>&1 &
```
In the game Settings interface to select the multiplayer game, in the options to change the server address to the local Settings of the server address.
###Chat server setup and startup
The chat function is an important feature in the game, through which players can communicate in real time. In the `chatbot\chat_server`file, we provide the source code for our chat server.
In the `config.py` file, we provide the chat server configuration information. Developers need to change it according to their own chat server configuration.
 
```
#The following configuration information is required in the config file.Developers need to change the url of chat_server to the server address they set, which will be used for subsequent connections to the chat software.
chat_server:
  url: http://127.0.0.1:2337/
```

Once you've configured the above, you can simply run the following command locally:
```
nohup python chat_server.py
```
###Mq listener setup and startup
mq_listener is a service module for triggering event reply, active dialogue and free dialogue. It listens to the message queue in redis and sends the corresponding request to the ai server when the condition is met.
The developer needs to configure the ai server in the `config.py` file, as shown below:
```
#Fill in the url of ai_server to connect to the ai server
ai_server:
  url: http://127.0.0.1:2335/
```
To do this, run the following command:
```
nohup python mq_listener.py
```
###Discord server setup and startup
Discord is a very popular chat software, and we provided a connection to the Discord server. In `chatbot\discord\discord_server`,
We have provided the source code for our Discord server so that developers can deploy their own local Discord server. 
Developers who want to debug and develop in their own Discord need to go to the official Discord website and create their own server channel and create the corresponding bot.

Server id can be obtained from the Discord server Settings, the robot's token and id can be obtained from/Discord developer [web site] (https://discord.com/developers/applications).
Finally, fill in the server channel id, bot token, and id in the discord_server file, as shown below:
``` 
# Fill in the corresponding server channel id, bot token and id to connect to the Discord server
#Unciv_Bot is the administrator robot, and mongolia, china, rome, aztecs, greece, and egypt are the civilization robots
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
To do this, run the following command:
```
nohup python discord_server.py
```
Once this is done, the Discord server is up and developers can debug and develop in their Discord.