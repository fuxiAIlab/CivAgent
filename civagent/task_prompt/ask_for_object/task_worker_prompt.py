from civagent.task_prompt.prompt_hub import AskForObjectIdentifyDataModel

AskForObjectPrompt_Identify = """
You don't need any extra guesswork to figure out what {speaker_persona[civ_name]} says based on what {speaker_persona[civ_name]} says.
Do the following to return what you identified,
Give your answer in the format {{"demand":List[dict]}}, where each dict element contains three keywords: category(item category, must be the key in the {item_category_space} dictionary), item(item name, must be the key in the {item_detail_space} subdictionary corresponding to category), and amount(quantity, quantity, quantity). Must be an Arabic digit or "Any" for any quantity).
2. No extra prompts or Spaces.
"""

AskForObjectPrompt_Identify_Output = AskForObjectIdentifyDataModel

AskForObjectPrompt_Chat = """
You need to analyze the latest conversation between you and output the results in the given format.
1. In the dialogue process, no person, colon and other contents outside the dialogue are allowed, and no Chinese is allowed
2. Your output should have the characteristics of everyday English conversation
3. In the above conversation, you are at peace, he asks you for {asked_object} and threatens you, your decision result is {decision_result} and your decision reason is {decision_reason}
4. Keep your words within {maxTokens}, and explain your thoughts in one sentence, using double quotes
 
"""

AskForObjectPrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 80,
}

AskForObjectPrompt_Identify_Config = AskForObjectPrompt_Chat_Config
