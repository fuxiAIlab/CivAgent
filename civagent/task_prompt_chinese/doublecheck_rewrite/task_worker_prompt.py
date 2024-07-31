DoubleCheckRewritePrompt = """
你需要按照下面的要求分析你们之间的最新的对话内容，按照给定格式输出结果。
1.对话过程中禁止出现人称，冒号等对白以外的内容, 禁止出现英语
2.你输出的内容需要带有中文日常用语对话的特点
3.在上面的对话中，你认为对方可能的意图是{intention}，你需要表达的意思是:{response}。
4.你说的话要在{maxTokens}字以内，请根据你需要表达的意思，结合你们的关系和历史对话，用生动的话语输出，并使用双引号
"""

DoubleCheckRewritePrompt_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 30,
}