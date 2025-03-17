# DoubleCheckRewritePrompt = """
# You need to analyze the latest conversation between you and output the results in the given format.
# 1. In the dialogue process, no person, colon and other contents outside the dialogue are allowed, and no Chinese is allowed
# 2. Your output should have the characteristics of everyday English conversation
# 3. In the conversation above, you think the other person's possible intention is {intention} and you need to express :{response}.
# 4. Your statement needs to be within {maxTokens} words. Please vividly express your message, considering our relationship and past conversations, and use double quotation marks.
# """

DoubleCheckRewritePrompt = """
You need to analyze the latest conversation between you and output the results in the given format.
1. In the dialogue process, no person, colon and other contents outside the dialogue are allowed, and no Chinese is allowed
2. Your output should have the characteristics of everyday English conversation, and your statement needs to be within {maxTokens} words.
3. In the conversation above, you think the other player's possible intention is {intention}
4. Ask the other party if they want to proceed with {response} with you, remembering to adjust your tone and attitude based on your relationship and past conversations.
5. Your purpose is to confirm yes or no with the other party, not to make a decision.
6. You only need to output your reply to confirm yes or no (not good or bad), no other content is required.
"""
# whether they want to proceed with the {offer_str} - {demand_str} trade, using a tone that reflects your personality.

DoubleCheckRewritePrompt_Config = {
    "stop": None,
    "temperature": 0.5,
    "maxTokens": 50,
}
