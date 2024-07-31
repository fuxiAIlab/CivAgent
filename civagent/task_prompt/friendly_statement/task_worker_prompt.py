FriendlyStatementPrompt_Chat = """You need to analyze the latest conversation between you and output the results in the given format.
1. In the dialogue process, no person, colon and other contents outside the dialogue are allowed, and no Chinese is allowed
2. Your output should have the characteristics of everyday English conversation
3. In the conversation above, he offers you to co-sign an amicable statement, {decision_result} for your decision and {decision_reason} for your decision.
4. Keep your words within {maxTokens}, and explain your thoughts in one sentence, using double quotes
"""

FriendlyStatementPrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 80,
}
