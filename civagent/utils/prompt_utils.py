from civagent import action_space as agent_action_space
from civagent.task_prompt import system_prompt
from civagent import task_prompt


def str_make(T, d):
    # todo use f-string by eval(f"""f'''{x}'''""")
    return T.format(**d)


def task_prompt_make(prompt_str, context_dict):
    return str_make(prompt_str, context_dict)


def dialogue_history_make(prompt_str, context_dict):
    dialogue_history_str = "historical_dialogue:\n"
    if len(context_dict.get('dialogue_history', [])) >= 1:
        for d in context_dict['dialogue_history']:
            dialogue_history_str += str_make(prompt_str, d)
    return dialogue_history_str


def event_history_make(prompt_str, context_dict):
    event_history_str = "historical evens:\n"
    if len(context_dict.get('event_history', [])) >= 1:
        for d in context_dict['event_history']:
            d["turn_gap"] = int(context_dict['round']) - int(d['turns'])
            d["civ_name"] = context_dict["receiver_persona"]["civ_name"]
            event_history_str += str_make(prompt_str, d)
    return event_history_str


def prompt_make(intention, context_dict):
    prompt_str = "" + system_prompt.GameInfoPrompt
    agent_profile_str, dialoge_str = "", ""
    # todo add into test reqs
    if 'war_civs' in context_dict:
        agent_profile_str += str_make(system_prompt.AgentProfilePrompt, context_dict)
    # todo receiver and Intention annotations were added
    if isinstance(context_dict.get('dialogue_history', ""), list):
        dialoge_str = dialogue_history_make(system_prompt.DialogeHistoryPrompt, context_dict)
        dialoge_str += str_make(system_prompt.DialogePrompt, context_dict)
    else:
        dialoge_str = 'The historical dialogue is:\n' + str(context_dict.get('dialogue_history', ""))
    event_str = event_history_make(system_prompt.EventHistoryPrompt, context_dict)

    # if 'asked_object' not in context_dict:
    #     context_dict['asked_object'] = '资源、土地或者财富'
    #     context_dict = {**context_dict, **task_prompt.AskForObjectPrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.AskForObjectPrompt_Chat, context_dict)
    #     prompt_config = task_prompt.AskForObjectPrompt_Chat_Config
    # elif intention == 'ask_for_object_identify':
    #     context_dict = {**context_dict, **task_prompt.AskForObjectPrompt_Identify_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.AskForObjectPrompt_Identify, context_dict)
    #     prompt_config = task_prompt.AskForObjectPrompt_Identify_Config
    # elif intention == 'change_closeness':
    #     context_dict = {**context_dict, **task_prompt.ChangeClosenessPrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.ChangeClosenessPrompt_Chat, context_dict)
    #     prompt_config = task_prompt.ChangeClosenessPrompt_Chat_Config
    # elif intention == 'chat':
    #     context_dict = {**context_dict, **task_prompt.ChatPrompt_Close_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.ChatPrompt_Close, context_dict)
    #     prompt_config = task_prompt.ChatPrompt_Chat_Config
    # elif intention == 'nonsense':
    #     context_dict = {**context_dict, **task_prompt.NonsensePrompt_Close_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.NonsensePrompt_Close, context_dict)
    #     prompt_config = task_prompt.NonsensePrompt_Close_Config
    # # elif intention == 'declare_war':
    # #     context_dict = {**context_dict, **task_prompt.DeclareWarPrompt_Chat_Config}
    # #     task_prompt_str = task_prompt_make(task_prompt.DeclareWarPrompt_Chat, context_dict)
    # #     prompt_config = task_prompt.DeclareWarPrompt_Chat_Config
    # elif intention == 'common_enemy':
    #     context_dict = {**context_dict, **task_prompt.CommonEnemyPrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.CommonEnemyPrompt_Chat, context_dict)
    #     prompt_config = task_prompt.CommonEnemyPrompt_Chat_Config
    # elif intention == 'form_ally':
    #     context_dict = {**context_dict, **task_prompt.FormAllyPrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.FormAllyPrompt_Chat, context_dict)
    #     prompt_config = task_prompt.FormAllyPrompt_Chat_Config
    # elif intention == 'friendly_statement':
    #     context_dict = {**context_dict, **task_prompt.FriendlyStatementPrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.FriendlyStatementPrompt_Chat, context_dict)
    #     prompt_config = task_prompt.FriendlyStatementPrompt_Chat_Config
    # elif intention == 'intention_understanding':
    #     context_dict = {**context_dict, **task_prompt.IntentionUnderstandingPrompt_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.IntentionUnderstandingPrompt, context_dict)
    #     prompt_config = task_prompt.IntentionUnderstandingPrompt_Config
    # elif intention == 'doublecheck':
    #     context_dict = {**context_dict, **task_prompt.DoubleCheckPrompt_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.DoubleCheckPrompt, context_dict)
    #     prompt_config = task_prompt.DoubleCheckPrompt_Config
    # elif intention == 'mutual_defense':
    #     context_dict = {**context_dict, **task_prompt.MutualDefensePrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.MutualDefensePrompt_Chat, context_dict)
    #     prompt_config = task_prompt.MutualDefensePrompt_Chat_Config
    # elif intention == 'open_border':
    #     context_dict = {**context_dict, **task_prompt.OpenBorderPrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.OpenBorderPrompt_Chat, context_dict)
    #     prompt_config = task_prompt.OpenBorderPrompt_Chat_Config
    if intention == 'propose_trade':
        context_dict = {**context_dict, **task_prompt.ProposeTradePrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.ProposeTradePrompt_Chat, context_dict)
        prompt_config = task_prompt.ProposeTradePrompt_Chat_Config
    elif intention == 'propose_trade_identify':
        context_dict = {**context_dict, **task_prompt.ProposeTradePrompt_Identify_Config}
        task_prompt_str = task_prompt_make(task_prompt.ProposeTradePrompt_Identify, context_dict)
        prompt_config = task_prompt.ProposeTradePrompt_Identify_Config
    elif intention == 'bargain_buyer':
        context_dict = {**context_dict, **task_prompt.ProposeTradePrompt_BarginBuyer_Config}
        task_prompt_str = task_prompt_make(task_prompt.ProposeTradePrompt_BarginBuyer, context_dict)
        prompt_config = task_prompt.ProposeTradePrompt_BarginBuyer_Config
    elif intention == 'bargain_seller':
        context_dict = {**context_dict, **task_prompt.ProposeTradePrompt_BarginSeller_Config}
        task_prompt_str = task_prompt_make(task_prompt.ProposeTradePrompt_BarginSeller, context_dict)
        prompt_config = task_prompt.ProposeTradePrompt_BarginSeller_Config
    # elif intention == 'research_agreement':
    #     context_dict = {**context_dict, **task_prompt.ResearchAgreementPrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.ResearchAgreementPrompt_Chat, context_dict)
    #     prompt_config = task_prompt.ResearchAgreementPrompt_Chat_Config
    # elif intention == 'seek_peace':
    #     context_dict = {**context_dict, **task_prompt.SeekPeacePrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.SeekPeacePrompt_Chat, context_dict)
    #     prompt_config = task_prompt.SeekPeacePrompt_Chat_Config
    # elif intention == 'deceive':
    #     context_dict = {**context_dict, **task_prompt.DeceivePrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.DeceivePrompt_Chat, context_dict)
    #     prompt_config = task_prompt.DeceivePrompt_Chat_Config
    else:
        assert False, f"Unknown intention {intention}"
    if intention in ('doublecheck', 'propose_trade_identify', 'bargain_seller'):
        prompt_str = f"{dialoge_str}\n{task_prompt_str}"
    else:
        prompt_str = f"{prompt_str}\n{agent_profile_str}\n{event_str}\n{dialoge_str}\n{task_prompt_str}"
    return prompt_str, prompt_config


def intention_doublecheck(intention_result, req):
    intention_question = agent_action_space.doublecheck_question
    intention = intention_result['intention']
    if intention == 'propose_trade' and len(intention_result.get('civ2_resource_dict', [])) == 0:
        intention = 'propose_trade_gift'
    if intention == 'ask_for_object' and req.get('is_at_war', False):
        intention = 'ask_for_object_at_war'
    response = intention_question[intention][0]
    # todo Format of transfer Are you asking me for [{'category': 'Gold', 'item': 'Gold', 'amount': 100}]?
    return {
        "response": str_make(response, intention_result)
    }
