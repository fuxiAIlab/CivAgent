ChangeClosenessPrompt_Chat = """You need to analyze the latest conversation between you and output the results in the given format.
1. In the dialogue process, no person, colon and other contents outside the dialogue are allowed, and no Chinese is allowed
2. Your output should have the characteristics of everyday English conversation
3. In the conversation above, he said something to you that affected your relationship. Your latest role for him is {decision_result} and your reason for his decision is {decision_reason}.
4. Keep your words within {maxTokens}, and explain your thoughts in one sentence, using double quotes
"""

ChangeClosenessPrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 80,
}