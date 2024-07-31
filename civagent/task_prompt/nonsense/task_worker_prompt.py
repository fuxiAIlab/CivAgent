NonsensePrompt_Close = """You need to analyze the latest conversation between you and output the results in the given format.
1. In the dialogue process, no person, colon and other contents outside the dialogue are allowed, and no Chinese is allowed
2. Your output should have the characteristics of everyday English conversation
3. In the conversation above, he's engaged in too much small talk with you. His words have nothing to do with the game, and you want to express your desire not to continue the conversation.
4. Keep your words within {maxTokens}, and explain your thoughts in one sentence, using double quotes
"""

NonsensePrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 80,
}

NonsensePrompt_Close_Config = NonsensePrompt_Chat_Config
