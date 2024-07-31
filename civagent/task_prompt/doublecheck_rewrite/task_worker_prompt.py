DoubleCheckRewritePrompt = """
You need to analyze the latest conversation between you and output the results in the given format.
1. In the dialogue process, no person, colon and other contents outside the dialogue are allowed, and no Chinese is allowed
2. Your output should have the characteristics of everyday English conversation
3. In the conversation above, you think the other person's possible intention is {intention} and you need to express :{response}.
4. Your statement needs to be within {maxTokens} words. Please vividly express your message, considering our relationship and past conversations, and use double quotation marks.
"""

DoubleCheckRewritePrompt_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 30,
}