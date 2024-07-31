CommonEnemyPrompt_Chat = """You need to analyze the latest conversation between you and output the results in the given format.
1. In the dialogue process, no person, colon and other contents outside the dialogue are allowed, and no Chinese is allowed
2. Your output should have the characteristics of everyday English conversation
3. In the conversation above, he is trying to convince you to work together against your common enemy #enemy_country#. Your decision result is {decision_result} and your reason is {decision_reason}.
4. To keep your words within {maxTokens}, identify #enemy_country# and state your thoughts in one sentence, using double quotes
"""

CommonEnemyPrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 80,
}
