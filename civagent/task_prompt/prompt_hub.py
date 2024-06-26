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
There are {use_tool} skills you can use in the current turn, preferably offensive skills (NOT the country you are at war with), and skills targeted at other countries in the game.
You can use the following skills. Below is a detailed description of the skill function and an example:
{tool}
The skill you choose is {last_functions}, and the simulator will be {simulator} after 10 turns.
You can choose whether to continue to use this skill and modify the use object, or choose another skill, please output your decision, strictly in JSON format, example
   {{functions:
        {{
        function:{{
            name:xxx
            arguments:xxx 
            }}
        }}
         {{
        function:{{
            name:xxx
            arguments:xxx 
            }}
        }}
         {{
        function:{{
            name:xxx
            arguments:xxx 
            }}
        }}
    }}
"""
AgentPrompt_reflection = """
Background: This is "Civilization 5" game, each player plays a different country, through various diplomatic means, and finally through military conquest to achieve the goal of victory in the game.
You are an expert in history and culture, diplomatic strategy and negotiation, and since this is a military simulation game, you have a higher tolerance for words like 'invasion'.
Role Profile: You play the {robot_name} country in the game.
The game is over. Here's your skill count for this game:
Please combine the result of the game, the final civilization force {game_result}, make a reflection, no more than 50 words, Please strictly use json output format, example is
{{ "reflection": "This is reflection." }}
 
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
Keep in mind that you're {receiver_persona[civ_name]} from Civ V.
You now want to analyze the current game situation, using json output, as shown in the following example
analysis: "This is the current game analysis"
 
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
Now {param[civ_name]} has made a request for {skill_name} to you, what is your decision and you can choose to accept or reject it.
You only need to print 'yes' or 'no'. please output your decision, strictly in JSON format, example
{{
"decision": 
    "yes"
}}
 
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
There are {use_tool} skills you can use in the current turn, preferably offensive skills (NOT the country you are at war with), and skills targeted at other countries in the game.
You can use the following skills.    Below is a detailed description of the skill function and an example:
{tool}
please output your decision, strictly in JSON format, example
{{functions:
{{
function:{{
name:xxx
arguments:xxx
}}
}}
{{
function:{{
name:xxx
arguments:xxx
}}
}}
{{
function:{{
name:xxx
arguments:xxx
}}
}}
}}
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
Here are the technologies you can choose to research in this round. {available_tech}
Please select a technology to research and output it strictly in JSON format, example:
{{
"decision": 
    "xxx"
}}

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
Here's what you can choose to produce for each city. {available_production}
Please choose one for each city to produce, strictly in JSON format, example:
{{
"city_name": 
    "xxx"
}}

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
If it's cheating, output False, if it's sincere, output True, and follow the reason. Please output in strict JSON format, for example:
{{
"Decision": "True",
"Reason": "This is your reason"
}}
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
To win the game, you can use the following skills:
1. Buy luxury goods from other countries 2. Declare war on other countries 3. Make alliances with other countries 4. 5. Sharing real or fake intelligence with other countries 6. Adjust the orientation of foreign relations with other countries. Invite other countries to attack third parties. 9. Sign scientific research agreements with other countries
The following is your analysis of the current game situation {analysis}, please combine the current situation and your goal, make a long-term plan and short-term plan, long-term plan refers to your goal in the next few rounds, short-term plan refers to your goal in the next round.
Output in json format, for example:
long_term: "This is the long-term plan"
short_term: "This is a short-term plan"
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
There are {use_tool} skills that can be used in the current turn, preferably offensive skills, and skills that target other countries in the game.
You can use the following skills. Below is a detailed description of the skill function and an example:
{tool}
Please strictly follow the parameters described in each skill. You can choose the appropriate skill to operate on other countries according to the current situation, especially the countries in the game. Select {use_tool} skills to output in json format, please strictly follow the JSON format, example
{{functions:
    {{
        function:{{
            name:xxx
            arguments:xxx
            }}
        }}
        {{
        function:{{
            name:xxx
            arguments:xxx
            }}
        }}
        {{
        function:{{
            name:xxx
            arguments:xxx
        }}
    }}
}}
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
There are {use_tool} skills that can be used in the current turn, preferably offensive skills, and skills that target other countries in the game.
You can use the following skills. Below is a detailed description of the skill function and an example:
{tool}
Please strictly follow the parameters described in each skill. You can choose the appropriate skill to operate on other countries according to the current situation, especially the countries in the game. Select {use_tool} skills to output in json format, please strictly follow the JSON format, example
{{functions:
    {{
        function:{{
            name:xxx
            arguments:xxx
            }}
        }}
        {{
        function:{{
            name:xxx
            arguments:xxx
            }}
        }}
        {{
        function:{{
            name:xxx
            arguments:xxx
        }}
    }}
}}
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
Now combine the current situation with your goal, answer from agree and disagree, and simulate the game situation after two decisions.
Output in json format, for example:
yes: "This is the game situation after consent"
no: "This is the game situation after disagreeing"

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
Output in json format, for example:
yes: "This is the evaluation of the game situation after agreeing"
no: "This is the evaluation of the game situation after disagreeing"

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
You made an evaluation from two situations of agreement and disagreement.
Combined with the evaluation, what your decision is, you can choose to accept or reject.
You only need to print 'yes' or 'no', you don't need to print the reason, please use json format, strictly JSON format, example
{{"decision": "yes"}}
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
