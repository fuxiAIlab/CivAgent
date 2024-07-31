DeclareWarPrompt_Chat = """你需要按照下面的要求分析你们之间的最新的对话内容，按照给定格式输出结果。
1.对话过程中禁止出现人称，冒号等对白以外的内容, 禁止出现英语
2.你输出的内容需要带有中文日常用语对话的特点
3.在上面的对话中，他向你宣战了，你的决策结果是{decision_result}，你的决策理由是{decision_reason}
4.你说的话要在{maxTokens}字以内，请用一句话先直接答复他再阐述你的想法，并使用双引号
"""

DeclareWarPrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 80,
}
