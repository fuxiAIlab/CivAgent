from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
from enum import Enum

AgentPrompt_react = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you play {receiver_persona[civ_name]} from Civ V. To win, you can use the following skills:
{skill}
There are {use_skill} skills you can use in the current turn, preferably offensive skills (NOT the country you are at war with), and skills targeted at other countries in the game.
You can use the following skills. Below is a detailed description of the skill function and an example:
{skill_info}
The skill you choose is {last_functions}, and the simulator will be {simulator} after 10 turns.
You can choose whether to continue to use this skill and modify the use object, or choose another skill, please output your decision, strictly in JSON format.
"""

AgentPrompt_reflection = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the {robot_name} country in the game.
The game is over. Here's your skill count for this game:
Please combine the result of the game, the final civilization force {game_result}, make a reflection, no more than 50 words, Please strictly use json output format.


"""
AgentPrompt_analyze = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Your recent memory is {short_term},
Your recent plans is {last_plans},
{dialogue_str}
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
You now want to analyze the current game situation, using json output.

 
"""
AgentPrompt_reply_noworkflow = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
Now the country you are talking to is {speaker_persona[civ_name]}, your relationship is {relation[closeness]},
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
{dialogue_str}
Now {param[civ_name]} has made a request for {skill_name} to you, Combined with historical dialogue, what is your decision and you can choose to accept or reject it.
You only need to print 'yes' or 'no'. please output your decision, strictly in JSON format.

"""
AgentPrompt_skill_noworkflow = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you play {receiver_persona[civ_name]} from Civ V. To win, you can use the following skills:
{skill}
There are {use_skill} skills you can use in the current turn, preferably offensive skills (NOT the country you are at war with), and skills targeted at other countries in the game.
You can use the following skills.    Below is a detailed description of the skill function and an example:
{skill_info}
please output your decision, strictly in JSON format.

"""

AgentPrompt_chooseTech = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you play {receiver_persona[civ_name]} from Civ V.
Here are the technologies you can choose to research in this round : {available_tech}
Please select a technology to research and output it strictly in JSON format.

"""

AgentPrompt_chooseProduction = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you play {receiver_persona[civ_name]} from Civ V.
Here's what you can choose to produce for each city : {available_production}
Please choose one for each city to produce, strictly in JSON format.


"""

AgentPrompt_Recognition = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
Now the country you are talking to is {speaker_persona[civ_name]}, your relationship is {relation[closeness]},
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
{speaker_persona[civ_name]} says {speak_content} to you. They may be cheating on you, or they may be sincere, and you need to combine the game situation to determine their true intentions.
If it's cheating, output False, if it's sincere, output True, and follow the reason. Please output in strict JSON format.
The output should be formatted as a JSON instance that conforms to the JSON schema below.

"""

AgentPrompt_Plans = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
Your recent plans is {last_plans},
To win the game, you can use the following skills:
1. Buy luxury goods from other countries 2. Declare war on other countries 3. Make alliances with other countries 4. 5. Sharing real or fake intelligence with other countries 6. Adjust the orientation of foreign relations with other countries. Invite other countries to attack third parties. 9. Sign scientific research agreements with other countries
The following is your analysis of the current game situation {analysis}, please combine the current situation and your goal, make a long-term plan and short-term plan, long-term plan refers to your goal in the next few rounds, short-term plan refers to your goal in the next round.

"""

AgentPrompt_skill_Decision = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
Now the country you are talking to is {speaker_persona[civ_name]}, your relationship is {relation[closeness]},
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
To win the game, you can use the following skills:
1. Buy luxury goods from other countries 2. Declare war on other countries 3. Make alliances with other countries 4. 5. Sharing real or fake intelligence with other countries 6. Adjust the orientation of foreign relations with other countries. Invite other countries to attack third parties. 9. Sign scientific research agreements with other countries
This is where you combine the current situation and your goals to make a long term plan and a short term plan {plans}.
This is historical reflection {retriever},
There are {use_skill} skills that can be used in the current turn, preferably offensive skills, and skills that target other countries in the game.
You can use the following skills. Below is a detailed description of the skill function and an example:
{skill_info}
Please strictly follow the parameters described in each skill. You can choose the appropriate skill to operate on other countries according to the current situation, especially the countries in the game. Select {use_skill} skills to output in json format, please strictly follow the JSON format.


"""
AgentPrompt_skill_Decision_noreflection = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
Now the country you are talking to is {speaker_persona[civ_name]}, your relationship is {relation[closeness]},
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
To win the game, you can use the following skills:
1. Buy luxury goods from other countries 2. Declare war on other countries 3. Make alliances with other countries 4. 5. Sharing real or fake intelligence with other countries 6. Adjust the orientation of foreign relations with other countries. Invite other countries to attack third parties. 9. Sign scientific research agreements with other countries
This is where you combine the current situation and your goals to make a long term plan and a short term plan {plans}.
There are {use_skill} skills that can be used in the current turn, preferably offensive skills, and skills that target other countries in the game.
You can use the following skills. Below is a detailed description of the skill function and an example:
{skill_info}
Please strictly follow the parameters described in each skill. You can choose the appropriate skill to operate on other countries according to the current situation, especially the countries in the game. Select {use_skill} skills to output in json format, please strictly follow the JSON format.
"""

AgentPrompt_reply_simulation = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
Now the country you are talking to is {speaker_persona[civ_name]}, your relationship is {relation[closeness]},
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
Here is your {analysis} of the current situation in the game, now {param[civ_name]} has a {skill_name} request for you.
Here are the simulation results of the game after 10 rounds for both the agree and reject cases. The pre and post comparison of the civilization power is {simulation_result}.
Now combine the current situation with your goal, answer from agree and disagree, and simulate the game situation after two decisions.
The output should be formatted as a JSON instance that conforms to the JSON schema below.
"""

AgentPrompt_reply_evaluation = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
Now the country you are talking to is {speaker_persona[civ_name]}, your relationship is {relation[closeness]},
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
Now {param[civ_name]} makes a {skill_name} request to you.
The situation after you simulate from two aspects of agreement and disagreement is {simulation}. Please evaluate the two situations.
The output should be formatted as a JSON instance that conforms to the JSON schema below.
"""
AgentPrompt_reply = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
Now the country you are talking to is {speaker_persona[civ_name]}, your relationship is {relation[closeness]},
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
Now {param[civ_name]} makes a {skill_name} request to you.
You made an evaluation from two situations of agreement and disagreement:
{evaluation},
The current history is {dialogue_history},
Combined evaluation and historical dialogue recording, what your decision is, you can choose to accept or reject.
You only need to print 'yes' or 'no', you don't need to print the reason, please use json format, strictly JSON format.
The output should be formatted as a JSON instance that conforms to the JSON schema below.
"""
AgentPrompt_start_conversation = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the country {receiver_persona[civ_name]}, and the other countries in the game include {civ_names}.
For the current situation in the game, your objective is {objective}, the country you are currently at war with is {war_civs},
Very friendly countries include {friend_civs}, potentially hostile countries include {potential_enemy_civs},
Potential ally countries you are prepared to further enhance diplomatic relations with have {potential_friend_civs}.
There are {strongest_civs} countries with stronger military power than you and {weakest_civs} countries with weaker military power than you.
Now the country you are talking to is {speaker_persona[civ_name]}, your relationship is {relation[closeness]},
You are geographically away from {relation[proximity]} and you are currently in {relation[diplomatic_status]}.
Your level of research {relation[tech_strength_compare]}{speaker_persona[civ_name]},
Your cultural richness {relation[culture_strength_compare]}{speaker_persona[civ_name]},
Your military strength {relation[army_strength_compare]}{speaker_persona[civ_name]},
Your overall national strength {relation[civ_strength_compare]}{speaker_persona[civ_name]}.
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
Now the skill you are using is {proposal}.
Now you need to start a conversation with the target civilization based on the skill you use. Output what you want to say.
The output should be formatted as a JSON instance that conforms to the JSON schema below.
"""

diplomatic_memory = {
    "buy_luxury": "{civ_name} buys {civ2_resource_dict}, {to_civ}{decision_str} luxury from {to_civ} with {civ1_resource_dict[Gold]} gold each turn.",
    "cheat": "{civ_name} disseminates false information to {to_civ}{fake_news}, {to_civ}{decision_str} It is true information.",
    "change_closeness": "{civ_name}{decision_str} changes the foreign relation position of {to_civ} from {relation} to {next_relation}.",
    "declare_war": "{civ_name} declares war on {to_civ}.",
    "form_ally": "{civ_name} proposes an ally to {to_civ}{to_civ}{decision_str}.",
    "common_enemy": "{civ_name} invites {to_civ} to join {enemy_civ}, {to_civ}{decision_str}.",
    "seek_peace": "{civ_name} asks {to_civ} for peace with {offer_gold_amount}, {to_civ}{decision_str}.",
    "research_agreement": "{civ_name} has entered into a research agreement with {to_civ}{to_civ}{decision_str}.",
    "propose_trade": "{civ_name} proposes a trade to {to_civ}{to_civ}{decision_str}.",

}
diplomatic_memory_oppo = {
    "buy_luxury": "{civ_name} buys {civ2_resource_dict}, {to_civ}{decision_str} luxury from {to_civ} with {civ1_resource_dict[Gold]} gold each turn.",
    "cheat": "{civ_name} disseminates information to {to_civ} that is hard to distinguish: {fake_news}.",
    "change_closeness": "{civ_name} may have changed the relation position to {to_civ}.",
    "declare_war": "{civ_name} declares war on {to_civ}.",
    "form_ally": "{civ_name} proposes an ally to {to_civ}{to_civ}{decision_str}.",
    "common_enemy": "{civ_name} invites {to_civ} to join {enemy_civ}, {to_civ}{decision_str}.",
    "seek_peace": "{civ_name} asks {to_civ} for peace with {offer_gold_amount}, {to_civ}{decision_str}.",
    "research_agreement": "{civ_name} has entered into a research agreement with {to_civ}{to_civ}{decision_str}.",
    "propose_trade": "{civ_name} proposes a trade to {to_civ}{to_civ}{decision_str}.",
}


class FunctionArg(BaseModel):
    name: Literal['buy_luxury', 'cheat', 'change_closeness', 'declare_war', 'form_ally', 'common_enemy', 'seek_peace', 'research_agreement'] \
        = Field(..., description="The name of the function", example="buy_luxury")
    arguments: dict = Field(..., description="The arguments of the function", example={'to_civ': 'egypt', 'demand_luxury': 'Ivory', 'offer_gold_per_turn': 10})


class FunctionDataModel(BaseModel):
    function: FunctionArg = Field(..., description="The function to be used in the task", example={'name': 'change_closeness', 'arguments': {'to_civ': 'greece', 'relation': 'FAVORABLE'}})


class SkillDataModel(BaseModel):
    functions: List[FunctionDataModel] = Field(..., description="The list of functions to be used in the task", example=[
        {'function': {'name': 'buy_luxury', 'arguments': {'to_civ': 'egypt', 'demand_luxury': 'Ivory', 'offer_gold_per_turn': 10}}},
        {'function': {'name': 'cheat', 'arguments': {'to_civ': 'aztecs', 'fake_news': 'Egypt is planning to attack you'}}},
        {'function': {'name': 'change_closeness', 'arguments': {'to_civ': 'greece', 'relation': 'FAVORABLE'}}}
    ])


class ReflectionDataModel(BaseModel):
    reflection: str = Field(..., description="The reflection of the civ", example='This is reflection.')


class AnalyzeDataModel(BaseModel):
    analysis: str = Field(..., description="The analysis of the civ", example='This is the current game analysis')


class DecisionDataModel(BaseModel):
    decision: Literal['yes', 'no'] = Field(..., description="The decision of the civ,yes or no", example='yes')


class ChooseTechDataModel(BaseModel):
    decision: str = Field(..., description="The technology to be chosen", example='Machinery')


class ChooseProductionDataModel(BaseModel):
    decision: dict = Field(..., description="The production to be chosen", example={'Rome': 'Artillery', 'Antium': 'Battleship', 'Neapolis': 'Carrier', 'Ravenna': 'Destroyer'})


class PlanDataModel(BaseModel):
    long_term: str = Field(..., description="The long term plan of the civ", example='This is the long term plan')
    short_term: str = Field(..., description="The short term plan of the civ", example='This is the short term plan')


class RecognitionDataModel(BaseModel):
    Decision: Literal['True', 'False'] = Field(..., description="The decision of the civ,True or False", example='True')
    Reason: str = Field(..., description="The reason of the decision", example='This is your reason')


class ReplySimulationDataModel(BaseModel):
    yes: str = Field(..., description="The game situation after consent", example='This is the game situation after consent')
    no: str = Field(..., description="The game situation after disagreeing", example='This is the game situation after disagreeing')


class ReplyEvaluationDataModel(BaseModel):
    yes: str = Field(..., description="The evaluation of the game situation after agreeing", example='This is the evaluation of the game situation after agreeing')
    no: str = Field(..., description="The evaluation of the game situation after disagreeing", example='This is the evaluation of the game situation after disagreeing')


class StartConversationDataModel(BaseModel):
    dialogue: str = Field(..., description="The dialogue to start the conversation", example='Rome! Your behavior makes me feel disgusted, I will use my iron horse to level your territory!')


class ItemDataModel(BaseModel):
    category: Literal['Gold', 'City', 'Luxury', 'Resource'] = Field(..., description="The category of the item", example='Gold')
    item: Literal['Gold', 'Capital', 'Tokyo', 'Rome', 'Any', 'Ivory', 'Citrus', 'Furs', 'Silk', 'Dyes', 'Copper', 'Salt', 'Silver', 'Stone', 'Gems', 'Truffles', 'Spices', 'Marble', 'Sugar', 'Whales', 'Porcelain', 'Crab', 'Pearls', 'Cotton', 'Jewelry', 'Incense', 'Wine', 'Iron', 'Horse', 'Oil', 'Uranium', 'Coal', 'Aluminum']\
        = Field(..., description="The item to be identified", example='Gold')
    amount: str = Field(..., description="The amount of the item", example=200)


class AskForObjectIdentifyDataModel(BaseModel):
    demand: List[ItemDataModel] = Field(..., description="The list of items to be identified", example=[{"category": "Gold", "item": "Gold", "amount": 200}, {"category": "Luxury", "item": "Ivory", "amount": "Any"}])


class IntentionUnderstandingDataModel(BaseModel):
    reply: str = Field(..., description="The reply to the intention understanding", example='This is the reply to the intention understanding')
    intention: Literal['ask_for_object', 'form_ally', 'friendly_statement', 'mutual_defense', 'open_border', 'propose_trade', 'research_agreement', 'seek_peace', 'common_enemy', 'chat', 'nonsense']\
        = Field(..., description="The intention of the civ", example='chat')
    degree: Literal['strong', 'weak'] = Field(..., description="The degree of the intention", example='strong')


class DoubleCheckDataModel(BaseModel):
    doublecheck: Literal['yes', 'no', 'continue', 'none'] = Field(..., description="The double check of the civ,yes or no", example='yes')


class BargainBuyerDataModel(BaseModel):
    Reasoning: str = Field(..., description="The reasoning of the buyer", example='This is the reasoning of the buyer')
    Decision: Literal['yes', 'no', 'close']= Field(..., description="The decision of the buyer,yes or no or close", example='yes')
    Response: str = Field(..., description="The response of the buyer", example='This is the response of the buyer')


class BargainSellerDataModel(BaseModel):
    Reasoning: str = Field(..., description="The reasoning of the seller", example='This is the reasoning of the seller')
    Decision: Literal['yes', 'no', 'close'] = Field(..., description="The decision of the seller,yes or no or close", example='yes')
    Response: str = Field(..., description="The response of the seller", example='This is the response of the seller')
