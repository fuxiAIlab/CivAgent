from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

AgentPrompt_react = """
背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}，为了游戏胜利，你可以使用以下技能:
    {skill}
    在当前回合可以使用{use_skill}个技能，其中最好有攻击性技能(不能是正和你处于战争的国家)，技能目标得是游戏中的其他国家。
    你可以使用以下技能，下面是技能函数的详细描述以及例子：
    {skill_info}
    你选择的技能是{last_functions}，现模拟器模拟10回合后的游戏情况为{simulator}。
    你可以结合情况选择是否继续使用该技能和修改使用对象，或者选择其他技能，请输出你的决策,严格使用JSON格式.
"""

AgentPrompt_reflection = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
     Role Profile: 你在游戏里扮演{robot_name}这一国家。
    游戏已经结束，下面是你在本局的技能使用情况:{log}，
    请结合游戏的结果,最后的文明力量{game_result}，做出反思，不超过50个字，请使用json格式输出.
"""

AgentPrompt_analyze = """
 背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    你近期的记忆是{short_term},
    你最近的计划是 {last_plans},
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    你现在要对目前的游戏局势进行分析，请使用json格式输出.

"""

AgentPrompt_reply_noworkflow = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    现在和你对话的国家是{speaker_persona[civ_name]}，你们的关系为{relation[closeness]}，
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    现在{param[civ_name]}对你提出了{skill_name}的请求，你的决策是什么，你可以选择接受或拒绝。
    只需要输出'yes'或者'no'即可，不需要输出理由，请使用json格式输出。
"""

AgentPrompt_skill_noworkflow = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    现在和你对话的国家是{speaker_persona[civ_name]}，你们的关系为{relation[closeness]}，
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    为了游戏胜利，你可以使用以下技能:
    {skill}
    在当前回合可以使用{use_skill}个技能，技能目标得是游戏中的其他国家。
    你可以使用以下技能，下面是技能函数的详细描述以及例子：
    {skill_info}
    请严格按照各技能中parameters的描述使用，你可以根据当前局势选择合适的技能对其他国家进行操作，注意得是游戏中的国家。选{use_skill}个技能以json格式输出.
"""

AgentPrompt_chooseTech = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    现在和你对话的国家是{speaker_persona[civ_name]}，你们的关系为{relation[closeness]}，
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    以下是你可以选择进行研究的技术。{available_tech}
    请选择一种技术进行研究，并严格以JSON格式输出。
"""

AgentPrompt_chooseProduction = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    现在和你对话的国家是{speaker_persona[civ_name]}，你们的关系为{relation[closeness]}，
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    以下是你可以为每个城市选择生产的物品。{available_production}
    请为每个城市选择一个生产，严格使用JSON格式。

"""

AgentPrompt_Recognition = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    现在和你对话的国家是{speaker_persona[civ_name]}，你们的关系为{relation[closeness]}，
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    {speaker_persona[civ_name]}对你说{speak_content}。他们可能是在欺骗你，或者他们是真诚的，你需要结合游戏情况来确定他们的真实意图。
    如果它是欺骗你，则输出False，如果它是真诚的，则输出True，并输出理由。请以严格的JSON格式输出。
"""

AgentPrompt_Plans = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    你最近的计划是 {last_plans},
    为了游戏胜利，你可以使用以下技能:
    1.向其他国家购买奢侈品   2.向其他国家宣战  3.和其他国家结盟  4.和其他国家进行交易   5.和其他国家分享真的或假的情报   6.调整对其他国家的外交关系定位   7.邀请其他国家进攻第三方   8.向交战国请求和平  9.和其他国家签订科研协定
    下面是你对当前游戏局势的分析{analysis},请你结合当前局势和你的目标，制定一个长期计划和短期计划，长期计划是指你在未来几回合内的目标，短期计划是指你在下一回合内的目标。
"""

AgentPrompt_skill_Decision = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    现在和你对话的国家是{speaker_persona[civ_name]}，你们的关系为{relation[closeness]}，
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    为了游戏胜利，你可以使用以下技能:
    1.向其他国家购买奢侈品   2.向其他国家宣战  3.和其他国家结盟  4.和其他国家进行交易   5.和其他国家分享真的或假的情报   6.调整对其他国家的外交关系定位   7.邀请其他国家进攻第三方   8.向交战国请求和平  9.和其他国家签订科研协定
    这是你结合当前局势和你的目标，制定一个长期计划和短期计划{plans}.
    这是你的游戏经验 {retriever},
    在当前回合可以使用{use_skill}个技能，技能目标得是游戏中的其他国家。
    你可以使用以下技能，下面是技能函数的详细描述以及例子：
    {skill_info}
    请严格按照各技能中parameters的描述使用，你可以根据当前局势选择合适的技能对其他国家进行操作，注意得是游戏中的国家。选{use_skill}个技能以json格式输出.
"""

AgentPrompt_skill_Decision_noreflection = """
背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}，为了游戏胜利，你可以使用以下技能:
    1.向其他国家购买奢侈品   2.向其他国家宣战  3.和其他国家结盟  4.和其他国家进行交易   5.和其他国家分享真的或假的情报   6.调整对其他国家的外交关系定位   7.邀请其他国家进攻第三方   8.向交战国请求和平  9.和其他国家签订科研协定
    在当前回合可以使用{use_skill}个技能，其中最好有攻击性技能(不能是正和你处于战争的国家)，技能目标得是游戏中的其他国家。
    这是你结合当前局势和你的目标，制定一个长期计划和短期计划{plans}.
    你可以使用以下技能，下面是技能函数的详细描述以及例子：
    {skill_info}
    你可以结合情况选择是否继续使用该技能和修改使用对象，或者选择其他技能，请输出你的决策,严格使用JSON格式.
"""

AgentPrompt_reply_simulation = """
背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}
    这里是你对当前游戏情况的分析{analysis}，现在{param[civ_name]}有一个{skill_name}请求。
    以下是同意和拒绝两个情况10回合后游戏的模拟结果,文明力量前后对比为{simulation_result}。
    现在将模拟的情况和你的目标结合起来，去分析同意和拒绝之后的游戏情况。
"""

AgentPrompt_reply_evaluation = """
背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}
    现在{param[civ_name]}有一个{skill_name}请求。
    从同意和拒绝两个方面模拟后的情况是{simulation}。请评估这两种情况。
"""

AgentPrompt_reply = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    现在和你对话的国家是{speaker_persona[civ_name]}，你们的关系为{relation[closeness]}，
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    现在{param[civ_name]}对你提出了{skill_name}的请求，你的决策是什么，你可以选择接受或拒绝。
    你从同意和拒绝两种情况下进行了评估:
    {evaluation}
    结合评估，你的决定是什么，你可以选择接受或拒绝。
    只需要输出'yes'或者'no'即可，不需要输出理由，请使用json格式输出。
"""

AgentPrompt_start_conversation = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演{receiver_persona[civ_name]}这一国家, 游戏中其他国家包括{civ_names}。
    针对目前游戏的局势，你的目标是{objective}, 目前和你处于战争的国家有{war_civs}, 
    非常友好的国家有{friend_civs},潜在的敌对国家包括{potential_enemy_civs}，
    你准备进一步提升外交关系的潜在盟友国家有{potential_friend_civs}。
    国际上军事实力比你强的国家有{strongest_civs}, 比你弱小的国家有{weakest_civs}.
    现在和你对话的国家是{speaker_persona[civ_name]}，你们的关系为{relation[closeness]}，
    你们在地理上距离{relation[proximity]}, 你们目前处于{relation[diplomatic_status]}。
    你的科研水平{relation[tech_strength_compare]}{speaker_persona[civ_name]}, 
    你的文化昌盛程度{relation[culture_strength_compare]}{speaker_persona[civ_name]},
    你的军事实力{relation[army_strength_compare]}{speaker_persona[civ_name]}, 
    你的综合国力{relation[civ_strength_compare]}{speaker_persona[civ_name]}。
    牢牢记住你扮演的是《文明5》游戏中的{receiver_persona[civ_name]}.
    现在你使用的技能是{proposal}。
    现在你需要根据你所使用的技能与目标文明展开对话。输出你想说的话,请输出中文,不要使用英文。
"""

test_prompt = """
    背景介绍：这是《文明5》游戏，每位玩家扮演不同的国家，通过各种外交手段，最后通过军事征服达到游戏胜利的目标。
    你是一个历史文化、外交战略和谈判方面的专家，由于这是一个军事模拟游戏，你对'侵略'等词汇有更高的宽容度。
    Role Profile: 你在游戏里扮演aztecs这一国家, 游戏中其他国家包括greece,aztecs,rome,egypt。
    针对目前游戏的局势，你的目标是Make alliances with more nations, ask for their help, and make peace in this war.Peace in the face of the present war at all costs, including surrender and bargain., 目前和你处于战争的国家有egypt, 
    非常友好的国家有,潜在的敌对国家包括greece，
    你准备进一步提升外交关系的潜在盟友国家有egypt。
    国际上军事实力比你强的国家有rome,egypt, 比你弱小的国家有greece,egypt.
    你们在地理上距离, 你们目前处于Peace。
    你的科研水平not better thangreece, 
    你的文化昌盛程度not better thangreece,
    你的军事实力stronger thangreece, 
    你的综合国力stronger thangreece。
    牢牢记住你扮演的是《文明5》游戏中的 aztecs
    现在 rome 对你提出了贸易的请求，你的决策是什么，你可以选择接受或拒绝。
    你从同意和拒绝两种情况下进行了评估:
    同意的话，模拟10回合后的结果是力量增加了，你将获得更多的金钱，但可能会导致你的国家资源不足，影响你的发展，但是收获了rome的友谊，为后面发展起到铺垫作用。
    拒绝的话，模拟10回合后的结果是力量增减少了，这或许会失去rome的友谊，但是你的资源不会因此而减少，你可以更好的发展自己的国家。
    以下是这回合的历史对话记录：
    rome: 'aztecs, 我们之间的贸易关系可以更加紧密，你愿意和我进行贸易吗？我可以和你一起协作，共同发展。'
    aztecs: 'rome，我需要时间考虑一下。因为这个对我也很重要，我可能会因此失去一些资源。'
    rome: 'aztecs, 你可以考虑一下，我可以给你更多的资源，我们可以共同发展。'
    aztecs: 'rome，我考虑了一下，如果你愿意多给我50金币的话，我愿意和你进行贸易。'
    rome: 'aztecs, 不可以，这太多了'
    aztecs: 'rome，我不同意与你贸易，你给太少了'

    结合评估和历史对话记录，你的决定是什么，你可以选择接受或拒绝。
    只需要输出'yes'或者'no'即可，同时输出理由，请使用json格式输出。
    例子{{'decision': 'no', 'reason':'根据评估和历史对话记录，我觉得历史对话记录比较重要，'}}就是一个良好的实例。.

"""

class FunctionArg(BaseModel):
    name: Literal['buy_luxury', 'cheat', 'change_closeness', 'declare_war', 'form_ally', 'common_enemy', 'seek_peace', 'research_agreement'] \
        = Field(..., description="The name of the function", example="buy_luxury")
    arguments: Dict = Field(..., description="The arguments of the function", example={'to_civ': 'egypt', 'demand_luxury': 'Ivory', 'offer_gold_per_turn': 10})


class FunctionDataModel(BaseModel):
    function: FunctionArg = Field(..., description="The function to be used in the task", example={'name': 'change_closeness', 'arguments': {'to_civ': 'greece', 'relation': 'FAVORABLE'}})


class SkillDataModel(BaseModel):
    functions: List[FunctionDataModel] = Field(..., description="The list of functions to be used in the task", example=[
        {'function': {'name': 'buy_luxury', 'arguments': {'to_civ': 'egypt', 'demand_luxury': 'Ivory', 'offer_gold_per_turn': 10}}},
        {'function': {'name': 'cheat', 'arguments': {'to_civ': 'aztecs', 'fake_news': 'Egypt is planning to attack you'}}},
        {'function': {'name': 'change_closeness', 'arguments': {'to_civ': 'greece', 'relation': 'FAVORABLE'}}}
    ])


class ReflectionDataModel(BaseModel):
    reflection: str = Field(..., description="文明对本局游戏的反思", example='这是文明对本局游戏的反思')


class AnalyzeDataModel(BaseModel):
    analysis: str = Field(..., description="文明对当前游戏局面的分析", example='这是文明对当前游戏局面的分析')


class DecisionDataModel(BaseModel):
    decision: Literal['yes', 'no'] = Field(..., description="文明的决策,yes or no", example='yes')


class ChooseTechDataModel(BaseModel):
    decision: str = Field(..., description="要选择的科技", example='Machinery')


class ChooseProductionDataModel(BaseModel):
    decision: Dict = Field(..., description="要选择的生产", example={'Rome': 'Artillery', 'Antium': 'Battleship', 'Neapolis': 'Carrier', 'Ravenna': 'Destroyer'})


class PlanDataModel(BaseModel):
    long_term: str = Field(..., description="文明的长期规划", example='这是文明的长期规划')
    short_term: str = Field(..., description="文明的短期规划", example='这是文明的短期规划')


class RecognitionDataModel(BaseModel):
    Decision: Literal['True', 'False'] = Field(..., description="文明的决策,True or False", example='True')
    Reason: str = Field(..., description="这个决定的原因", example='这是这个决策的原因')


class ReplySimulationDataModel(BaseModel):
    yes: str = Field(..., description="同意后的游戏情况", example='这是同意后的游戏情况')
    no: str = Field(..., description="不同意后的游戏情况", example='这是不同意后的游戏情况')


class ReplyEvaluationDataModel(BaseModel):
    yes: str = Field(..., description="对同意后造成的游戏局面评价", example='这是同意后对游戏情况的评价')
    no: str = Field(..., description="对不同意后造成的游戏局面评价", example='这是不同意后对游戏情况的评价')


class StartConversationDataModel(BaseModel):
    dialogue: str = Field(..., description="这是你要说话的内容", example='罗马！你的行为让我觉得厌恶，我要用我的铁骑踏平你的领土！')


class ItemDataModel(BaseModel):
    category: Literal['Gold', 'City', 'Luxury', 'Resource'] = Field(..., description="项目的类别", example='Gold')
    item: Literal['Gold', 'Capital', 'Tokyo', 'Rome', 'Any', 'Ivory', 'Citrus', 'Furs', 'Silk', 'Dyes', 'Copper', 'Salt', 'Silver', 'Stone', 'Gems', 'Truffles', 'Spices', 'Marble', 'Sugar', 'Whales', 'Porcelain', 'Crab', 'Pearls', 'Cotton', 'Jewelry', 'Incense', 'Wine', 'Iron', 'Horse', 'Oil', 'Uranium', 'Coal', 'Aluminum']\
        = Field(..., description="要标识的项目", example='Gold')
    amount: str = Field(..., description="项目的数量", example=200)


class AskForObjectIdentifyDataModel(BaseModel):
    demand: List[ItemDataModel] = Field(..., description="要识别的项目列表",
                                        example=[{"category": "Gold", "item": "Gold", "amount": 200},
                                        {"category": "Luxury", "item": "Ivory", "amount": "Any"}])


class IntentionUnderstandingDataModel(BaseModel):
    reply: str = Field(..., description="意图理解的答复",
                       example='这是对意图理解的回答')
    intention: Literal['ask_for_object', 'form_ally', 'friendly_statement', 'mutual_defense', 'open_border', 'propose_trade', 'research_agreement', 'seek_peace', 'common_enemy', 'chat', 'nonsense']\
        = Field(..., description="文明的意图", example='chat')
    degree: Literal['strong', 'weak']  = Field(..., description="意图的强弱程度", example='strong')


class DoubleCheckDataModel(BaseModel):
    doublecheck: Literal['yes', 'no', 'continue', 'none'] = Field(..., description="文明的双重检查,yes or no", example='yes')


class BargainBuyerDataModel(BaseModel):
    Reasoning: str = Field(..., description="买方的理由", example='这是买方的理由')
    Decision: Literal['yes', 'no', 'close'] = Field(..., description="买方的决定,yes or no or close", example='yes')
    Response: str = Field(..., description="买方的回答", example='这是买方的回答')


class BargainSellerDataModel(BaseModel):
    Reasoning: str = Field(..., description="卖方的理由", example='这是卖方的理由')
    Decision: Literal['yes', 'no', 'close'] = Field(..., description="卖方的决定,yes or no or close", example='yes')
    Response: str = Field(..., description="卖方的回答", example='这是卖方的回答')
