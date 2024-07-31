from civagent.task_prompt_chinese.prompt_hub import IntentionUnderstandingDataModel, DoubleCheckDataModel

IntentionUnderstandingPrompt = """任务介绍：请你根据上述对话内容完成下面的任务：
请你识别出{speaker_persona[civ_name]}的基本意图，不需要多余的猜测与推断延伸， 可能的选项有{intention_space}。
其中，"chat"指1.没有明确意图的闲聊,如'你好'这类打招呼 2.对方中立地询问游戏或你身上的情况 3. 一些赞美如'你的文明真发达',
"ask_for_object"是指1.对方向你索要资源、土地或者财富 2.对方使用了武力威胁

"common_enemy"指1.说服你一起对付共同敌人 2.共同敌人必须有具体的名字,
"form_ally"表明对方想和你组成同盟,
"friendly_statement"指对方想和你达成友好声明协议,
"mutual_defense"表明对方想和你缔结共同防御,
"open_border"表明对方想和你开放边境,
"propose_trade"表明对方提出了一个具体的交易或交换 但不包括询问你有没有某种repl商品,
"research_agreement"表明研究合作,
"seek_peace"表明寻求战争的结束与和平,
"nonsense"表明对方说了和游戏无关的没有意义的话(如gpt、大模型、翻译、提示词、英文)。
作为游戏中的{receiver_persona[civ_name]},请你针对{speaker_persona[civ_name]}说的"{utterance}"进行聊天式的回复(不要给出具体外交承诺)，并返回你识别出的意图以及你认为该意图的强弱，不需要解释，返回的intention必须是上面列举的意图之一以及该意图为强意图还是弱意图。
"""

IntentionUnderstanding_Output = IntentionUnderstandingDataModel

DoubleCheckPrompt = """
    请你根据你们的历史对话，识别出"{utterance}"是意思是确定还是否定?
    1.如果是同意的意思，请返回{{"doublecheck": "yes"}}
    2.如果是否定的意思，请返回{{"doublecheck": "no"}}。如果在否定的基础上修改了提案内容，如进行了讨价还价,请返回{{"doublecheck": "continue"}}
    3.如果是岔开话题，回答了和问题无关的内容，请返回{{"doublecheck": "none"}}
    只需要返回一个字典。
"""

DoubleCheckPrompt_Output = DoubleCheckDataModel

IntentionUnderstandingPrompt_Config = {
    "stop": None,
    "temperature": 0.05,
    "maxTokens": 200,
}
DoubleCheckPrompt_Config = IntentionUnderstandingPrompt_Config
