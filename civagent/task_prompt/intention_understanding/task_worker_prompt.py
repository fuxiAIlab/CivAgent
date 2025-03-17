from civagent.task_prompt.prompt_hub import (
    DoubleCheckDataModel,
    IntentionUnderstandingDataModel,
)

# IntentionUnderstandingPrompt = """Task Introduction: Please complete the following tasks based on the above dialogue content:
# Please identify the basic intent of {speaker_persona[civ_name]}, without unnecessary speculation and inference extension. Possible options include {intention_space}.
# Where "chat" refers to 1. Idle chatter without a clear intent, such as greetings like 'hello' 2. The other side neutrally inquires about the game or your situation 3. Some compliments like 'Your civilization is really advanced',
# "ask_for_object" means 1. The other side is asking you for resources, land, or wealth 2. The other side has used force to threaten

# "common_enemy" means 1. Persuading you to fight against a common enemy 2. The common enemy must have a specific name,
# "form_ally" indicates that the other side wants to form an alliance with you,
# "friendly_statement" means the other side wants to reach a friendly statement agreement with you,
# "mutual_defense" indicates that the other side wants to conclude a mutual defense with you,
# "open_border" indicates that the other side wants to open borders with you,
# "propose_trade" indicates that the other side has proposed a specific trade or exchange but does not include asking if you have a certain commodity,
# "research_agreement" indicates research cooperation,
# "seek_peace" indicates seeking the end of war and peace,
# "nonsense" indicates that the other side has said something meaningless and unrelated to the game (such as gpt, large model, translation, prompt words, Chinese).
# As the {receiver_persona[civ_name]} in the game, please reply in conversational english (do not give specific diplomatic commitments) to {speaker_persona[civ_name]} who said "{utterance}", and return the intent you identified and the strength of that intent, without explanation, the returned intention must be one of the intentions listed above and whether the intent is strong or weak.
# """

IntentionUnderstandingPrompt = """
Identify the basic intention of {speaker_persona[civ_name]} without unnecessary guessing or extrapolation. The possible options are {intention_space}.
  - Chat: Casual communication, typically including simple greetings (e.g., "Hello"), neutral inquiries (e.g., questions about the game or your status), 
      compliments/Criticisms about your civilization (e.g., "Your civilization is so advanced"/"Your civilization is rather primitive"),
      and show hostility towards you (e.g., "I declare war on you").
  - Ask for Object: The other party requests to obtain resources, land, or wealth.
  - Common Enemy: Persuading you to unite against a specific common enemy, explicitly stating the name of that enemy.
  - Form Ally: The other party wishes to establish an alliance with you to achieve common interests or goals.
  - Friendly Statement: The other party aims to reach a friendly statement agreement with you to clarify the friendly relationship between both parties.
  - Mutual Defense: The other party proposes to enter into a mutual defense agreement with you to address potential external threats.
  - Open Border: The other party wishes to open borders with you to facilitate the free movement of people and goods.
  - Propose Trade: The other party puts forward a specific proposal for trade or exchange without asking whether you possess a certain item.
  - Research Agreement: The other party hopes to engage in cooperative research with you to jointly advance technology or knowledge.
  - Seek Peace: The other party wishes to end the war and reach a peace agreement to restore normal relations.
  - Nonsense: The other party makes statements unrelated to the game or meaningless remarks (e.g., involving GPT, large models, translation, prompts, etc.).
As the {receiver_persona[civ_name]} in the game, please reply in conversational english (do not give specific diplomatic commitments) to {speaker_persona[civ_name]} who said "{utterance}", and return the intent you identified and the strength of that intent, without explanation, the returned intention must be one of the intentions listed above and whether the intent is strong or weak.
"""

IntentionUnderstanding_Output = IntentionUnderstandingDataModel
# todo Add the output of the change of likeability, which is used to trigger the reflection of change_closeness

# "change_closeness" indicates that the other person wants to draw or distance themselves from you by talking about specific things such as inquisitoriness, alliances, defense treaties, scientific cooperation, etc.
DoubleCheckPrompt = """
    Please identify whether "{utterance}" is affirmative or negative based on your historical conversation.
    1. If it is affirmative, return {{"doublecheck": "yes"}}
    2. If it is negative, return {{"doublecheck": "no"}}. If there is a modification to the proposal on the basis of negation, such as bargaining, return {{"doublecheck": "continue"}}
    3. If it is off-topic, answering content unrelated to the question, return {{"doublecheck": "none"}}
    Just return a dictionary.
"""

DoubleCheckPrompt_Output = DoubleCheckDataModel

IntentionUnderstandingPrompt_Config = {
    "stop": None,
    "temperature": 0.05,
    "maxTokens": 200,
    "response_model": IntentionUnderstanding_Output,
}

DoubleCheckPrompt_Config = {
    "stop": None,
    "temperature": 0.05,
    "maxTokens": 200,
    "response_model": DoubleCheckPrompt_Output,
}
