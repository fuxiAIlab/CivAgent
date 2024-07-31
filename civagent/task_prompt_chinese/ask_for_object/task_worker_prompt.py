from civagent.task_prompt_chinese.prompt_hub import AskForObjectIdentifyDataModel

AskForObjectPrompt_Identify = """
请你根据{speaker_persona[civ_name]}说的话，识别出{speaker_persona[civ_name]}提出的交易内容，不需要多余的猜测与推断延伸。
按以下要求返回你识别出的内容，
1. 请以{{"demand":List[dict]}}格式给出答案,  列表中每个dict元素包含3个关键词: category(物品类别, 必须是字典{item_category_space}中的key), item(物品名称, 必须是字典{item_detail_space}中category对应的子字典的key)和amount(数量, 必须是阿拉伯数字或者"Any"表示任意数量)。
2. 不输出额外的提示词和空格。
"""

AskForObjectPrompt_Identify_Output = AskForObjectIdentifyDataModel

AskForObjectPrompt_Chat = """你需要按照下面的要求分析你们之间的最新的对话内容，按照给定格式输出结果。
1.对话过程中禁止出现人称，冒号等对白以外的内容, 禁止出现英语
2.你输出的内容需要带有中文日常用语对话的特点
3.在上面的对话中，你们处于和平，他向你索要了{asked_object}并威胁你，你的决策结果是{decision_result}，你的决策理由是{decision_reason}
4.你说的话要在{maxTokens}字以内，请用一句话先直接答复他再阐述你的想法，并使用双引号
"""

AskForObjectPrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 80,
}
AskForObjectPrompt_Identify_Config = AskForObjectPrompt_Chat_Config
