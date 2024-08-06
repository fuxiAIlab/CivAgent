import copy

from civagent import logger


def str_make(T, d):
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


def response_make(intention, context_dict):
    if 'chinese' in context_dict.get('language', 'chinese').lower():
        import civagent.task_prompt_chinese as task_prompt
    else:
        from civagent import task_prompt
    return task_prompt.Response[intention]


def doublecheck_make(intention, context_dict):
    if 'chinese' in context_dict.get('language', 'chinese').lower():
        import civagent.task_prompt_chinese as task_prompt
    else:
        from civagent import task_prompt
    return task_prompt.Doublecheck_question[intention]


def admin_reply_make(intention, context_dict):
    default_language = 'chinese' if 'discord' not in context_dict.get('platform', '').lower() else 'English'
    if 'chinese' in context_dict.get('language', default_language).lower():
        from civagent.task_prompt_chinese.admin_reply.task_worker_prompt import ADMIN_REPLY
    else:
        from civagent.task_prompt.admin_reply.task_worker_prompt import ADMIN_REPLY
    text = str_make(ADMIN_REPLY[intention], context_dict)
    return text


def envent_trigger_make(intention, context_dict):
    if 'chinese' in context_dict.get('language', 'chinese').lower():
        import civagent.task_prompt_chinese as task_prompt
    else:
        from civagent import task_prompt
    text = str_make(task_prompt.EVENT_TRIGGER_REPLY[intention], context_dict)
    return text


def prompt_make(intention, context_dict):
    if 'chinese' in context_dict.get('language', 'chinese').lower():
        import civagent.task_prompt_chinese as task_prompt
        from civagent.task_prompt_chinese import system_prompt
        import civagent.task_prompt_chinese.prompt_hub as PromptHub
    else:
        from civagent import task_prompt
        from civagent.task_prompt import system_prompt
        import civagent.task_prompt.prompt_hub as PromptHub
    prompt_str = "" + system_prompt.GameInfoPrompt
    agent_profile_str, dialoge_str = "", ""
    # todo add into test reqs
    if 'war_civs' in context_dict:
        agent_profile_str += str_make(system_prompt.AgentProfilePrompt, context_dict)
    # todo add receiver and Intention annotations
    if isinstance(context_dict.get('dialogue_history', ""), list):
        dialoge_str = dialogue_history_make(system_prompt.DialogeHistoryPrompt, context_dict)
        dialoge_str += str_make(system_prompt.DialogePrompt, context_dict)
    else:
        dialoge_str = 'The historical dialogue is:\n' + str(context_dict.get('dialogue_history', ""))
    context_dict['dialogue_str'] = dialoge_str
    event_str = event_history_make(system_prompt.EventHistoryPrompt, context_dict)
    prompt_config = task_prompt.ProposeTradePrompt_Chat_Config
    if intention == 'ask_for_object':
        if 'asked_object' not in context_dict:
            context_dict['asked_object'] = 'resource, city or money'
        context_dict = {**context_dict, **task_prompt.AskForObjectPrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.AskForObjectPrompt_Chat, context_dict)
        prompt_config = task_prompt.AskForObjectPrompt_Chat_Config
    elif intention == 'ask_for_object_identify':
        context_dict = {**context_dict, **task_prompt.AskForObjectPrompt_Identify_Config}
        task_prompt_str = task_prompt_make(task_prompt.AskForObjectPrompt_Identify, context_dict)
        prompt_config = task_prompt.AskForObjectPrompt_Identify_Config
        prompt_config['response_model'] = task_prompt.AskForObjectPrompt_Identify_Output
    elif intention == 'change_closeness':
        context_dict = {**context_dict, **task_prompt.ChangeClosenessPrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.ChangeClosenessPrompt_Chat, context_dict)
        prompt_config = task_prompt.ChangeClosenessPrompt_Chat_Config
    elif intention == 'chat':
        context_dict = {**context_dict, **task_prompt.ChatPrompt_Close_Config}
        task_prompt_str = task_prompt_make(task_prompt.ChatPrompt_Close, context_dict)
        prompt_config = task_prompt.ChatPrompt_Chat_Config
    elif intention == 'nonsense':
        context_dict = {**context_dict, **task_prompt.NonsensePrompt_Close_Config}
        task_prompt_str = task_prompt_make(task_prompt.NonsensePrompt_Close, context_dict)
        prompt_config = task_prompt.NonsensePrompt_Close_Config
    # elif intention == 'declare_war':
    #     context_dict = {**context_dict, **task_prompt.DeclareWarPrompt_Chat_Config}
    #     task_prompt_str = task_prompt_make(task_prompt.DeclareWarPrompt_Chat, context_dict)
    #     prompt_config = task_prompt.DeclareWarPrompt_Chat_Config
    elif intention == 'common_enemy':
        context_dict = {**context_dict, **task_prompt.CommonEnemyPrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.CommonEnemyPrompt_Chat, context_dict)
        prompt_config = task_prompt.CommonEnemyPrompt_Chat_Config
    elif intention == 'form_ally':
        context_dict = {**context_dict, **task_prompt.FormAllyPrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.FormAllyPrompt_Chat, context_dict)
        prompt_config = task_prompt.FormAllyPrompt_Chat_Config
    elif intention == 'friendly_statement':
        context_dict = {**context_dict, **task_prompt.FriendlyStatementPrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.FriendlyStatementPrompt_Chat, context_dict)
        prompt_config = task_prompt.FriendlyStatementPrompt_Chat_Config
    elif intention == 'intention_understanding':
        context_dict = {**context_dict, **task_prompt.IntentionUnderstandingPrompt_Config}
        task_prompt_str = task_prompt_make(task_prompt.IntentionUnderstandingPrompt, context_dict)
        prompt_config = task_prompt.IntentionUnderstandingPrompt_Config
        prompt_config['response_model'] = task_prompt.IntentionUnderstanding_Output
    elif intention == 'doublecheck':
        context_dict = {**context_dict, **task_prompt.DoubleCheckPrompt_Config}
        task_prompt_str = task_prompt_make(task_prompt.DoubleCheckPrompt, context_dict)
        prompt_config = task_prompt.DoubleCheckPrompt_Config
        prompt_config['response_model'] = task_prompt.DoubleCheckPrompt_Output
    elif intention == 'mutual_defense':
        context_dict = {**context_dict, **task_prompt.MutualDefensePrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.MutualDefensePrompt_Chat, context_dict)
        prompt_config = task_prompt.MutualDefensePrompt_Chat_Config
    elif intention == 'open_border':
        context_dict = {**context_dict, **task_prompt.OpenBorderPrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.OpenBorderPrompt_Chat, context_dict)
        prompt_config = task_prompt.OpenBorderPrompt_Chat_Config
    elif intention == 'propose_trade':
        context_dict = {**context_dict, **task_prompt.ProposeTradePrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.ProposeTradePrompt_Chat, context_dict)
        prompt_config = task_prompt.ProposeTradePrompt_Chat_Config
    elif intention == 'propose_trade_identify':
        context_dict = {**context_dict, **task_prompt.ProposeTradePrompt_Identify_Config}
        task_prompt_str = task_prompt_make(task_prompt.ProposeTradePrompt_Identify, context_dict)
        prompt_config = task_prompt.ProposeTradePrompt_Identify_Config
        prompt_config['response_model'] = task_prompt.AskForObjectPrompt_Identify_Output
    elif intention == 'bargain_buyer':
        context_dict = {**context_dict, **task_prompt.ProposeTradePrompt_BarginBuyer_Config}
        task_prompt_str = task_prompt_make(task_prompt.ProposeTradePrompt_BarginBuyer, context_dict)
        prompt_config = task_prompt.ProposeTradePrompt_BarginBuyer_Config
        prompt_config['response_model'] = task_prompt.ProposeTradePrompt_BarginBuyer_Output
    elif intention == 'bargain_seller':
        context_dict = {**context_dict, **task_prompt.ProposeTradePrompt_BarginSeller_Config}
        task_prompt_str = task_prompt_make(task_prompt.ProposeTradePrompt_BarginSeller, context_dict)
        prompt_config = task_prompt.ProposeTradePrompt_BarginSeller_Config
        prompt_config['response_model'] = task_prompt.ProposeTradePrompt_BarginSeller_Output
    elif intention == 'research_agreement':
        context_dict = {**context_dict, **task_prompt.ResearchAgreementPrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.ResearchAgreementPrompt_Chat, context_dict)
        prompt_config = task_prompt.ResearchAgreementPrompt_Chat_Config
    elif intention == 'seek_peace':
        context_dict = {**context_dict, **task_prompt.SeekPeacePrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.SeekPeacePrompt_Chat, context_dict)
        prompt_config = task_prompt.SeekPeacePrompt_Chat_Config
    elif intention == 'deceive':
        context_dict = {**context_dict, **task_prompt.DeceivePrompt_Chat_Config}
        task_prompt_str = task_prompt_make(task_prompt.DeceivePrompt_Chat_first, context_dict)
        prompt_config = task_prompt.DeceivePrompt_Chat_Config
    elif intention == 'doublecheck_rewrite':
        context_dict = {**context_dict, **task_prompt.DoubleCheckRewritePrompt_Config}
        task_prompt_str = task_prompt_make(task_prompt.DoubleCheckRewritePrompt, context_dict)
        prompt_config = task_prompt.DoubleCheckRewritePrompt_Config
    elif intention == 'agent_analyze':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_analyze, context_dict)
        prompt_config = {'response_model': PromptHub.AnalyzeDataModel}
    elif intention == 'agent_skill_noworkflow':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_skill_noworkflow, context_dict)
        prompt_config = {'response_model': PromptHub.SkillDataModel}
    elif intention == 'agent_react':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_react, context_dict)
        prompt_config = {'response_model': PromptHub.SkillDataModel}
    elif intention == 'agent_conversation':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_start_conversation, context_dict)
        prompt_config = {'response_model': PromptHub.StartConversationDataModel}
    elif intention == 'agent_choose_tech':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_chooseTech, context_dict)
        prompt_config = {'response_model': PromptHub.ChooseTechDataModel}
    elif intention == 'agent_choose_production':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_chooseProduction, context_dict)
        prompt_config = {'response_model': PromptHub.ChooseProductionDataModel}
    elif intention == 'agent_reflection':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_reflection, context_dict)
        prompt_config = {'response_model': PromptHub.ReflectionDataModel}
    elif intention == 'agent_reply_noworkflow':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_reply_noworkflow, context_dict)
        prompt_config = {'response_model': PromptHub.DecisionDataModel}
    elif intention == 'agent_recognition':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_Recognition, context_dict)
        prompt_config = {'response_model': PromptHub.RecognitionDataModel}
    elif intention == 'agent_plans':
        task_prompt_str = PromptHub.AgentPrompt_Plans
        prompt_config = {'response_model': PromptHub.PlanDataModel}
    elif intention == 'agent_skill_decision':
        task_prompt_str = PromptHub.AgentPrompt_skill_Decision
        prompt_config = {'response_model': PromptHub.SkillDataModel}
    elif intention == 'agent_skill_decision_noreflection':
        task_prompt_str = PromptHub.AgentPrompt_skill_Decision_noreflection
        prompt_config = {'response_model': PromptHub.SkillDataModel}
    elif intention == 'agent_reply_simulation':
        task_prompt_str = PromptHub.AgentPrompt_reply_simulation
        prompt_config = {'response_model': PromptHub.ReplySimulationDataModel}
    elif intention == 'agent_reply_evaluation':
        task_prompt_str = PromptHub.AgentPrompt_reply_evaluation
        prompt_config = {'response_model': PromptHub.ReplyEvaluationDataModel}
    elif intention == 'agent_reply':
        task_prompt_str = task_prompt_make(PromptHub.AgentPrompt_reply, context_dict)
        prompt_config = {'response_model': PromptHub.DecisionDataModel}
    else:
        assert False, f'Invalid intention: {intention}'

    if intention in ('doublecheck', 'propose_trade_identify', 'bargain_seller'):
        prompt_str = f"{dialoge_str}\n{task_prompt_str}"
    elif intention.startswith("agent"):
        prompt_str = f"{task_prompt_str}"
    elif intention in ('doublecheck_rewrite', ):
        # todo use smaller prompt
        prompt_str = f"{prompt_str}\n{agent_profile_str}\n{event_str}\n{dialoge_str}\n{task_prompt_str}"
    else:
        prompt_str = f"{prompt_str}\n{agent_profile_str}\n{event_str}\n{dialoge_str}\n{task_prompt_str}"
    return prompt_str, prompt_config


def intention_doublecheck(intention_result, req):
    intention = intention_result['intention']
    if 'offer' in intention_result:
        offer_extract = []
        for original_offer in intention_result['offer']:
            offer = copy.deepcopy(original_offer)
            offer['amount'] = offer.get('amount', 1)
            offer_extract.append(f'{offer["amount"]} {offer["item"]}')
        intention_result['offer'] = offer_extract
    if 'demand' in intention_result:
        demand_extract = []
        for original_demand in intention_result['demand']:
            demand = copy.deepcopy(original_demand)
            demand['amount'] = demand.get('amount', 1)
            demand_extract.append(f'{demand["amount"]} {demand["item"]}')
        intention_result['demand'] = demand_extract
    if intention == 'propose_trade' and len(intention_result.get('civ2_resource_dict', [])) == 0:
        intention = 'propose_trade_gift'
    if intention == 'ask_for_object' and req.get('is_at_war', False):
        intention = 'ask_for_object_at_war'
    response = doublecheck_make(intention, req)[0]
    # todo Format of transfer Are you asking me for [{'category': 'Gold', 'item': 'Gold', 'amount': 100}]?
    return {
        "response": str_make(response, intention_result)
    }
