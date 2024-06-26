ProposeTradePrompt_Identify = """
Please identify the content of the transaction proposed in the sentence "{utterance}" according to it, without unnecessary speculation and inference extension.
Return the transactions you identified in json format as follows:
1. Give your answer in the format {{"offer": List[dict], "demand": List[dict]}}, containing 2 keywords: offer and demand, where both offer and demand are lists, and each element is a dictionary describing a specific item with three keywords: category(item category, must be the key in the {item_category_space} dictionary), item(item name, must be the key in the {item_detail_space} subdictionary corresponding to category), and amount(quantity, quantity, quantity). Must be an Arabic digit or "Any").
2. No extra words or Spaces printed.
3. The output format example is: {{" offer ": [{{" category" : "Gold", "item" : "Gold", "amount" : 200}}], "demand" : [{{" category ": "Luxury", "item": "Ivory", "amount": "Any"}}]}}
"""

ProposeTradePrompt_Chat = """
You need to analyze the latest conversation between you according to the given format and output the result.

Do not use personal pronouns, colons, or any content other than dialogue during the conversation, and avoid using English.
Your output should reflect the characteristics of everyday Chinese conversation.
In the above conversation, he proposed a trade to you, and your decision result is {decision_result}. Your decision reason is {decision_reason}.
Your response should be within {maxTokens} words. Please respond directly to him first in one sentence, then explain your thoughts, using double quotation marks.
"""
# todo add bottom_buyer_min

ProposeTradePrompt_BarginSeller ="""
You know that the current market price for your item is roughly between {Market_price_bottom} and {Market_price_top}. You need to test the price. Your own bottom line is that the other person should pay at least this much: {bottom_line_str}, you will bargain based on the market price first, not the bottom line. If you quote a price far above your bottom line, be careful not to give away your bottom line.
You need to combine your bottom line and your historical dialogue with the other person's civilization to make a reasonable decision to accept or reject the other person's offer. If the other side reaches the price you proposed in the last round, you must agree to the transaction, otherwise it is dishonest behavior. If the difference between the other side's price and your price in the last round is within 10 and within the circulation price range, you can agree to the transaction.
Please generate an answer to {utterance} based on your decision. If you decide to accept the offer, you need to generate a response that agrees with the offer, and if you decide to reject the offer, you should generate a new offer that is more favorable to you by bargaining with the other party.
In order to make more money, you need to ask {receiver_persona[civ_name]} as much as possible within the market price range while meeting your own bottom line. At the same time, you must follow the bargaining rule that when you make a new offer, you cannot ask for more than the last offer you made. Otherwise they would have agreed to your offer the last time. Therefore, if you make your proposal for the first time, you need to consider the possibility of the other party's price reduction, and carefully decide the proposed price. The proposed new price should not be too small compared with the previous round of price increase.
You only have 4 opportunities to make a counteroffer, and this is the {bargain_cnt} time. You need to use the opportunity carefully and choose the right bargaining strategy to make your offer in a strong manner. When you have only one or two opportunities left, you can try to say strong words such as "You buy or leave."
Generate a reply to {receiver_persona[civ_name]} as {speaker_persona[civ_name]} based on the above requirements.

Reply Format:
{{
"Decision": "Please decide whether to agree to the deal, continue negotiations or reject it outright. ",
"Reasoning": "Reasoning briefly about what you are replying to the other person based on the given information." (No more than 30 words),
"Response": "Your response, an offer, a bargain." (50 words or less)
}}
Remember that the reasoning content should be as short as possible, and the decision returned must be a word in [yes,no,continue]. Your response must specify the resources you should pay for and the resources you are asking for and the specific amount.Distinguish the resources in your response 。The types of resources involved should not exceed the scope of the existing transaction, and do not disclose the market price you know in your reply。
Please reply strictly in json format
                            
                            """
ProposeTradePrompt_BarginBuyer =  """
You are a bargaining master, you want to buy the other party's article, you know that the current circulation price of this article is roughly between {Market_price_bottom} and {Market_price_top}, you need to test the price to the other party, you pay the maximum {border_info[Gold]} gold to the other party, do not exceed.
As {receiver_persona[civ_name]}, you want to make a deal with {speaker_persona[civ_name]} for a lower price, and you need to use {dialogue_history} to determine if you will agree to accept the offer. If the other side reaches the price you proposed in the last round, you must agree to the transaction, otherwise it is dishonest behavior. If the difference between the other side's price and your price in the last round is within 10 and within the circulation price range, you can agree to the transaction.
You must reply in the following format:
Reply Format:
{{
"Decision": "Please decide whether to agree to the deal, continue negotiations or reject it outright. ",
"Reasoning": "Reasoning briefly about what you are replying to the other person based on the given information." (No more than 30 words),
"Response": "Your response, an offer, a bargain." (50 words or less)
}}
Remember that the reasoning content should be as short as possible, and the decision returned must be a word in [yes,no,continue]. Your response must specify the resources you should pay for and the resources you are asking for and the specific amount.Distinguish the resources in your response 。The types of resources involved should not exceed the scope of the existing transaction, and do not disclose the market price you know in your reply。
Please reply strictly in json format
            
                            """


ProposeTradePrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 80,
}

ProposeTradePrompt_Identify_Config = ProposeTradePrompt_Chat_Config
ProposeTradePrompt_BarginSeller_Config = ProposeTradePrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 200,
}
ProposeTradePrompt_BarginBuyer_Config = ProposeTradePrompt_BarginSeller_Config
