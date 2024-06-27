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

In the game creation interface, you need to make the following settings:
```
1. Set the number of city-states to 0.
2. Turn off multiplayer online games.
```
### Step 4. Open the server
The game AI server is implemented using Flask, so you need to start the Flask server. Then run the following command:
```
cd deployment
python flask_server.py
```
If you have achieved this, congratulations, you have successfully linked the decision-making in the game to the local server. At this point, you can begin experiencing our benchmark.
### Step 5. Decision Visualization
In the server terminal interface, you can see the decision requests sent from the game.

In the `Log` folder, you can view the logs to see the skill selections, technology choices, production selections, and diplomatic decision information for each CivAgent in the game.

If you want to customize your own diplomatic decision module, please continue reading.
### Step 6. Customize the decision module

In the existing game decision server, the prototype of the decision module is the existing game behavior tree. If you are a developer or researcher who would like to further research and develop foreign policy decisions, we provide examples for reference.

An example:

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
`get_wantsToSignDeclarationOfFrienship`This is a function to determine whether the two parties can sign a declaration of friendship. In the game, a decision request is made, and the information in the request contains the game archive information`gameinfo`, the name of Civilization 1`civ1_name`, and the name of Civilization 2`civ2_name`. The function body calls the behavior tree decision in the Jar package, and finally returns a json file containing the decision result and the reason for the decision.

The developer can rewrite the function body decision in a custom way, as long as the return format is consistent.

## Authors and Citation

**Authors:** Jiawei Wang,Kai Wang

Please cite our paper if you use the code or data in this repository.

```
@inproceedings{2023XXXX,  
author = {Jiawei Wang, Kai Wang},  
title = {Digital Player: Evaluating Large Language Models based Human-like Agent in Games},  
year = {2024},  
publisher = {},  
address = {},  
booktitle = {},  
keywords = {},  
location = {},  
series = {}
}
```
