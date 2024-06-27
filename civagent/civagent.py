from copy import deepcopy
import random
import collections
import json
from civagent import default_gameid, default_from_name
import civagent.utils.memory_utils
import civagent.utils.utils
from civagent.utils import workflow_utils
from civagent.search import Search
from civsim import utils, action_space
from civagent import action_space as agent_action_space
from civagent import logger
from civagent.utils import prompt_utils
from civsim.utils import json_load_defaultdict, get_civ_index, fix_civ_name
from civagent.utils import workflow_utils
from civagent.utils.utils import save2req
from civagent.task_prompt.prompt_hub import AgentPrompt_react, AgentPrompt_chooseTech, AgentPrompt_chooseProduction, \
    AgentPrompt_analyze, AgentPrompt_reply_noworkflow, AgentPrompt_skill_noworkflow



class CivAgent:
    def __init__(
            self,
            user_id,
            civ_name,
            nicknames,
            character,
            game_info,
            game_id='',
            default_llm="gpt-3.5-turbo-1106"
    ):
        self.default_llm = default_llm
        self.user_id = user_id
        self.civ_name = civ_name
        self.civ_ind = utils.get_civ_index(game_info, civ_name)
        self.nicknames = nicknames
        self.character = character
        self.strengths_info = utils.get_stats(game_info, self.civ_ind)
        # self.culture_strength = strengths_info.get("culture_strength",0)
        # self.tech_strength = strengths_info.get("tech_strength",0)
        # self.army_strength = strengths_info.get("army_strength",0)
        # self.navy_strength = strengths_info.get("navy_strength",0)
        self.memory = civagent.utils.memory_utils.Memory(user_id, game_id)
        self.civ_names = utils.get_all_civs(game_info)
        self.oppo_agent = {}
        self.relations = {}
        self.game_info = game_info
        self.objective = []
        self.ally_civs = set()
        self.enemy_civs = set()
        self.war_civs = set()
        self.friend_civs = set()
        self.potential_enemy_civs = set()
        self.potential_friend_civs = set()
        self.short_term = []

    def init(self):
        for civ_name in self.civ_names:
            if civ_name != self.civ_name:
                # todo Persist to the archive, update more keys
                diplomatic_status = utils.get_diplomatic_status(self.game_info, self.civ_ind, civ_name)
                # relation = utils.get_relation(self.game_info, self.civ_ind, civ_name)
                proximity = utils.get_proximity(self.game_info, self.civ_ind, civ_name)
                self.relations[f"{self.civ_name}#{civ_name}"] = {
                    # todo
                    "closeness": "Unfamiliar",
                    "expected_closeness": "Unfamiliar",
                    "diplomatic_status": diplomatic_status,
                    "proximity": proximity,
                    # todo
                    "army_proximity": proximity,
                    "history_event": [],
                    "promise": [],
                    "owe_favor": []
                }
        self.init_inferred_agent()

    def update(self, game_info):
        self.war_civs = set()
        self.game_info = game_info
        self.civ_ind = utils.get_civ_index(game_info, self.civ_name)
        self.strengths_info = utils.get_stats(game_info, self.civ_ind)
        for civ_name in self.civ_names:
            if civ_name != self.civ_name:
                diplomatic_status = utils.get_diplomatic_status(self.game_info, self.civ_ind, civ_name)
                relation = utils.get_relation(self.game_info, self.civ_ind, civ_name)
                # todo
                expected_relation = utils.get_relation(self.game_info, self.civ_ind, civ_name)
                proximity = utils.get_proximity(self.game_info, self.civ_ind, civ_name)
                self.relations[f"{self.civ_name}#{civ_name}"]["closeness"] = relation
                self.relations[f"{self.civ_name}#{civ_name}"]["expected_closeness"] = expected_relation
                self.relations[f"{self.civ_name}#{civ_name}"]["diplomatic_status"] = diplomatic_status
                self.relations[f"{self.civ_name}#{civ_name}"]["proximity"] = proximity
                self.relations[f"{self.civ_name}#{civ_name}"]["army_proximity"] = proximity
                if diplomatic_status.lower() == 'war':
                    self.war_civs.add(civ_name)
                # todo Make a decision every 10 turns.
                if relation in (action_space.RelationSpace.ALLY.value, action_space.RelationSpace.FRIEND.value):
                    self.friend_civs.add(civ_name)
                if relation in (action_space.RelationSpace.ENEMY.value, action_space.RelationSpace.UNFORGIVABLE.value):
                    self.enemy_civs.add(civ_name)
                if expected_relation in (action_space.RelationSpace.ALLY.value, action_space.RelationSpace.FRIEND.value):
                    self.potential_friend_civs.add(civ_name)
                if expected_relation in (action_space.RelationSpace.ENEMY.value, action_space.RelationSpace.UNFORGIVABLE.value):
                    self.potential_enemy_civs.add(civ_name)
                # todo
                # self.relations[f"{self.civ_name}#{civ_name}"]["closeness"] = "Unfamiliar"
        self.plan_diplomacy_relation()
        self.reflection_objective()

    def plan_diplomacy_relation(self):
        self.potential_enemy_civs = []
        self.potential_friend_civs = []
        # todo Consider the factors from the past.
        self.ally_distant_attack_nearby()
        # todo
        # self.enemy_civs.difference_update(self.potential_friend_civs)
        # self.friend_civs.difference_update(self.potential_enemy_civs)

    def ally_distant_attack_nearby(self):
        proximity_values = {
            "NEIGHBORS": 1,
            "CLOSE": 2,
            "FAR": 3,
            "DISTANT": 4,
            "": 4
        }
        civ_proximity = {}
        for civ_name in self.civ_names:
            if civ_name != self.civ_name:
                civ_proximity[civ_name] = self.relations[f"{self.civ_name}#{civ_name}"]["proximity"]
        sorted_civs = sorted(civ_proximity, key=lambda x: proximity_values[civ_proximity[x].upper()])
        num = min(len(sorted_civs) // 3, 2)
        # todo Consider more factors
        self.potential_friend_civs = sorted_civs[-num:]
        self.potential_enemy_civs = sorted_civs[:num]
        # todo Write to the archive.
        for civ_name in self.potential_friend_civs:
            self.relations[f"{self.civ_name}#{civ_name}"]["expected_closeness"] = "Ally"
        for civ_name in self.potential_enemy_civs:
            self.relations[f"{self.civ_name}#{civ_name}"]["expected_closeness"] = "Enemy"

    def reflection_objective(self):
        # todo LLM reflection
        if len(self.war_civs) < 1:
            self.objective = [random.choice(list(agent_action_space.objective_space_peace))]
        elif len(self.war_civs) == 1:
            self.objective = [random.choice(list(agent_action_space.objective_space_war))]
        else:
            self.objective = [random.choice(list(agent_action_space.objective_space_war_double))]

    def init_inferred_agent(self):
        for civ_name in self.civ_names:
            if civ_name != self.civ_name:
                # todo incomplete information
                self.oppo_agent[civ_name] = CivAgent(
                    self.user_id,
                    civ_name,
                    civ_name,
                    # todo
                    self.character,
                    self.game_info
                )

    @staticmethod
    def bargain(req, game_info, model):
        if 'bottom_line' not in req:
            border_info = CivAgent.get_resource_border(req, game_info)
            req = {**req, **border_info}
            try:
                bottom_line = CivAgent.get_trade_bottom_line(req, game_info, req['bargain_role'])
            except Exception as e:
                logger.exception(f'error in bargain:get_trade_bottom_line {e}')
                bottom_line = {'bottom_line': [{'category': 'Gold', 'item': 'Gold', 'amount': 120}]}
            logger.debug(f"debug in bargain bottom_line:{bottom_line}")
            # todo Delete
            # bottom_line = {'bottom_line': [{'category': 'Gold', 'item': 'Gold', 'amount': 120}]}
            req = {**req, **bottom_line, "bottom_line_str": str(bottom_line['bottom_line'][0].get('amount', 0))}
        else:
            bottom_line = req['bottom_line']
            req = {**req, **bottom_line, "bottom_line_str": str(bottom_line['bottom_line'][0].get('amount', 0))}
        if req['bargain_role'] == 'buyer':
            prompt_str, prompt_config = prompt_utils.prompt_make(
                "bargain_buyer", req
            )
        else:
            prompt_str, prompt_config = prompt_utils.prompt_make(
                "bargain_seller", req
            )
        response, _, actual_prompt = workflow_utils.run_workflows(
            {"prompt": prompt_str, **prompt_config}, model, decision=True
        )
        return {
            "response": response['Response'],
            "bottom_line": bottom_line,
            "decision_result": "bargain",
            "decision_reason": response.get('Reasoning', ""),
            "bargain_result": response['Decision']
        }, actual_prompt

    # propose_new = '''
    #     You are currently a player in the game "Civilization 5," representing a civilization. You are currently representing the civilization {civ_name}. Presently, you need to propose a trade to purchase resources from another civilization, {opp_civ_name}. Your last proposal to {opp_civ_name} for a trade was {last_proposal}. After some negotiation, you were unable to reach an agreement. Your negotiation history is as follows: {chat_history}. It is evident that your trade offer was not advantageous to the other party. Since the other party is unable to meet your purchasing needs, you may consider proposing a new trade by reducing the quantity of resources you wish to purchase. You should not exceed this maximum cost in your proposal: {bottom_buyer}.
    #
    #     Please generate a response to {opp_civ_name} based on the above requirements as {civ_name}.
    #     You must reply in the following format:
    #     Response Format:
    #     Reasoning: Provide a brief rationale for your new proposal to the other party based on the given information.
    #     Response: Your new proposal to {opp_civ_name}.
    # '''
    # def generate_new_proposal(self, req, model):
    #     propose_req = {"civ_name": self.civ_name, "opp_civ_name": req['speaker_persona']['civ_name'],
    #                    "last_proposal": req['utterance'], 'chat_history': req['dialogue_history'],
    #                    'bottom_buyer': self.bottom_line}
    #     propose_prompt_str = propose_new.format(**propose_req)
    #
    #     response, _, actual_prompt = workflow_utils.run_workflows(
    #         {"prompt": propose_prompt_str, **decision_prompt_config}, model, force_json=False
    #     )
    #     content = re.search(r'Response:(.*)', response).group(1).lstrip(' ').rstrip('.')
    #     new_proposal = content
    #     return new_proposal

    @staticmethod
    def get_resource_border(req, game_info):
        civ_name = req["civ_name"]
        civ_resource = utils.get_all_resources(game_info)
        my_resource = civ_resource[civ_name]
        civ_ind = utils.get_civ_index(game_info, civ_name)
        gold_num = game_info['civilizations'][civ_ind]['gold']
        my_resource['Gold'] = gold_num
        return {'border_info': my_resource}

    @staticmethod
    def get_trade_bottom_line(req, game_info, bargain_role='buyer'):
        civ_name = req["civ_name"]
        response = {'intention': 'propose_trade', 'detail': req['identify_result']}
        max_border = deepcopy(response['detail']['offer'])
        opp_border = deepcopy(response['detail']['offer'])
        for i in range(len(response['detail']['offer'])):
            item_category = response['detail']['offer'][i]['category']
            max_border[i]['amount'] = req['border_info'][item_category]
            opp_border[i]['amount'] = req['border_info'][item_category]
        search_instance = Search(
            response,
            req['receiver_persona']['civ_name'],
            req['speaker_persona']['civ_name'],
            civ_name,
            bargain_role,
            game_info,
            max_border,
            opp_border
        )
        bottom_line = search_instance.call_divide()
        return {'bottom_line': bottom_line}

    @staticmethod
    def extract_trades(intention, req, model):
        req["item_category_space"] = action_space.item_category_space
        req["item_detail_space"] = action_space.item_detail_space
        req["intention_space"] = agent_action_space.intention_space
        prompt_str, prompt_config = prompt_utils.prompt_make(
            intention + '_identify', req
        )
        identify_result, _, actual_prompt = workflow_utils.run_workflows(
            {"prompt": prompt_str, **prompt_config}, model, force_json=True
        )
        civ1_resource_dict, civ2_resource_dict = {}, {}
        logger.debug(f"debug in extract_trades: {identify_result}")
        # todo processing Any amount\item
        for item in identify_result.get("offer", {}):
            civ1_resource_dict[item['item']] = item['amount'] if "Any" != item['amount'] else 1
        req['civ1_resource_dict'] = civ1_resource_dict
        for item in identify_result.get("demand", {}):
            civ2_resource_dict[item['item']] = item['amount'] if "Any" != item['amount'] else 1
        req['civ2_resource_dict'] = civ2_resource_dict
        return civ1_resource_dict, civ2_resource_dict, identify_result, actual_prompt

    @staticmethod
    def get_last_dialogue(req):
        # todo
        #  The player may have entered two sentences;
        #  the player's debug information is noted in the receiver's reply;
        #  pair them using the UUID.
        last_dialogue_receiver = [
            x for x in req.get('dialogue_history', [{}])
            if x.get('speaker_civ', '').lower() == req['receiver_persona']['civ_name'].lower()
        ]
        last_dialogue_receiver = last_dialogue_receiver[-1] if len(last_dialogue_receiver) > 0 else {}
        # last_intention_degree = last_dialogue_receiver.get('debug_info', {}).get('intention_degree', '')
        # last_intention = last_dialogue_receiver.get('debug_info', {}).get('intention', '')
        # last_intention_doublecheck = last_dialogue_receiver.get('debug_info', {}).get('doublecheck', '')
        # last_intention_bargainresult = last_dialogue_receiver.get('debug_info', {}).get('bargain_result', '')
        return last_dialogue_receiver.get('debug_info', {})

    """
    text->
    if There is the last bargain tag identification content + identification is successful -》 走response
    if There is no doublecheck tag intent recognition-》if you intend to reply directly; if strong intent plus doublecheck tag if identifies content for trade； -》Don't call the response function
    if There is the last doublecheck tag check identification-》if trade goes bargain in response； else decision
    """

    @staticmethod
    def intention_understanding(req, model, only_chat=False):
        req["item_category_space"] = action_space.item_category_space
        req["item_detail_space"] = action_space.item_detail_space
        req["intention_space"] = agent_action_space.intention_space
        # is doublecheck reply?
        last_dialogue = CivAgent.get_last_dialogue(req)
        # intention = ''
        if not only_chat and last_dialogue.get('bargain_result', '') == 'continue':
            intention = 'bargain'
        elif not only_chat and last_dialogue.get('doublecheck', '') == 'wait':
            intention = 'doublecheck'
        else:
            intention = 'intention_understanding'

        # doublecheck
        if intention == 'bargain':
            prompt_str, prompt_config = prompt_utils.prompt_make(
                "doublecheck", req
            )
            raw_intention, response, actual_prompt = workflow_utils.run_workflows(
                {"prompt": prompt_str, **prompt_config}, model
            )
            # The judgment of whether the other party agrees or not
            if raw_intention['doublecheck'] == 'yes':
                # text = 'It's very good. We've come to a mutually beneficial deal.'
                req['identify_result'] = last_dialogue["identify_result"]
                req['civ1_resource_dict'] = last_dialogue["civ1_resource_dict"]
                req['civ2_resource_dict'] = last_dialogue["civ2_resource_dict"]
                actual_prompt = ""
                # last_dialogue Contains the previous round of transactions
                intention_result = {**last_dialogue, "intention": "trade_bargain", "bargain_result": "yes"}
            elif raw_intention['doublecheck'] in ('no', 'none'):
                # The other side closed the deal
                req['identify_result'] = last_dialogue["identify_result"]
                req['civ1_resource_dict'] = last_dialogue["civ1_resource_dict"]
                req['civ2_resource_dict'] = last_dialogue["civ2_resource_dict"]
                bargain_cnt = last_dialogue.get("bargain_cnt", 0)
                actual_prompt = ""
                intention_result = {**last_dialogue, "intention": "trade_bargain", "bargain_result": "no",
                                    "bargain_cnt": bargain_cnt + 1}
            else:
                # The other side put forward a new proposal
                try:
                    civ1_resource_dict, civ2_resource_dict, identify_result, actual_prompt = CivAgent.extract_trades(
                        'propose_trade', req, model
                    )
                except Exception as e:
                    logger.exception(f'error in bargain:extract_trades {e}:')
                    return {
                        **last_dialogue,
                        "intention": "trade_bargain",
                        "response": 'Your transaction is too complicated. Let\'s go to the transaction screen.',
                        "bargain_result": "no"
                    }, actual_prompt
                req['identify_result'] = identify_result
                req['civ1_resource_dict'] = civ1_resource_dict
                req['civ2_resource_dict'] = civ2_resource_dict
                bargain_cnt = last_dialogue.get("bargain_cnt", 0)
                intention_result = {
                    **last_dialogue,
                    "intention": "trade_bargain",
                    "bargain_result": "continue",
                    "bargain_cnt": bargain_cnt + 1, **identify_result,
                    "civ1_resource_dict": civ1_resource_dict,
                    "civ2_resource_dict": civ2_resource_dict
                }
            return intention_result, actual_prompt

        elif intention == 'doublecheck':
            prompt_str, prompt_config = prompt_utils.prompt_make(
                "doublecheck", req
            )
            raw_intention, response, actual_prompt = workflow_utils.run_workflows(
                {"prompt": prompt_str, **prompt_config}, model
            )
            logger.debug(f"doublecheck result of {req['utterance']} is {raw_intention}")
            if raw_intention.get('doublecheck', '') == 'yes':
                # intention_result = utils.intention_correct(raw_intention)
                raw_intention = {**last_dialogue, **raw_intention}
                return raw_intention, actual_prompt
            # todo raw_intention.get('doublecheck', '') == 'continue'
            else:
                raw_intention['response'] = 'Then I made a mistake. Let \'s get back to the game.'
                raw_intention = {**last_dialogue, **raw_intention}
                return raw_intention, actual_prompt
        # if type == 'intention_understanding':
        else:
            # intention_understanding
            prompt_str, prompt_config = prompt_utils.prompt_make(
                "intention_understanding", req
            )
            raw_intention, response, actual_prompt = workflow_utils.run_workflows(
                {"prompt": prompt_str, **prompt_config}, model
            )
            intention_result = utils.intention_correct(raw_intention)
            intention_degree = intention_result["intention_degree"]
            intention = intention_result['intention']

            if intention == 'nonsense':
                # todo
                intention_result['response'] = ("""Let\'s do less of these useless conversations and """
                                                + """focus more on the development of our country.""")

            if only_chat:
                return intention_result, actual_prompt

            # todo strong in English
            if intention_degree == 'strong' and intention in 'seek_peace' and not req.get('is_at_war', False):
                intention_result['response'] = 'We\'re not at war...'
                intention_result['intention'] = 'chat'
                return intention_result, actual_prompt

            # todo decision of common_enemy
            if intention_degree == 'strong' and intention in ('common_enemy',):
                intention_result['response'] += 'We will have to discuss the specific measures.'
                intention_result['intention'] = 'chat'
                return intention_result, actual_prompt

            if intention_degree == 'strong' and intention in ('ask_for_object', 'propose_trade'):
                try:
                    civ1_resource_dict, civ2_resource_dict, identify_result, _ \
                        = CivAgent.extract_trades(intention, req, model)
                except Exception as e:
                    logger.exception(f'error in bargain:extract_trades{e}:')
                    return {
                        **intention_result,
                        "intention": 'chat',
                        "response": 'Your transaction is too complicated. Let\'s go to the transaction screen.'
                    }, actual_prompt
                if len(civ2_resource_dict) + len(civ1_resource_dict) == 0:
                    # ask_for_object nothing
                    intention_result['intention'] = 'chat'
                    return intention_result, actual_prompt
                else:
                    req['civ1_resource_dict'] = civ1_resource_dict
                    req['civ2_resource_dict'] = civ2_resource_dict
                    intention_result = {
                        **intention_result,
                        "identify_result": identify_result, **identify_result,
                        "civ1_resource_dict": civ1_resource_dict,
                        "civ2_resource_dict": civ2_resource_dict
                    }

            if intention_degree == 'strong' and intention not in ('nonsense', 'chat'):
                # use doublecheck as response
                doublecheck = prompt_utils.intention_doublecheck(intention_result, req)
                intention_result = {**intention_result, **doublecheck, "doublecheck": "wait"}
                # logger.error(f'LLM intention understanding warning: get {response} for {actual_prompt}.')
            return intention_result, actual_prompt

    @staticmethod
    def response(req, intention_result, model, save_data={}, use_random=False):
        if (intention_result.get('doublecheck', '') == 'yes'
                and intention_result.get('intention', '') == 'propose_trade'
                or (intention_result.get('intention', '') == 'trade_bargain')):
            # bargain
            req['bargain_role'] = 'seller'
            result = ''
            decision_gm_fn = None
            # todo Does the other party agree?
            if intention_result.get('bargain_result', "") == 'yes':
                result, actual_prompt = intention_result, ""
                result["response"] = "It's very good. We've come to a mutually beneficial deal."
                key = 'propose_trade'
                param = [req[x] for x in action_space.decision_space[key]['param']]
                # todo gm_fn Support for composition
                decision_gm_fn = action_space.decision_space[key]['func']('yes')(*param)
            elif intention_result.get('bargain_result', "") == 'no':
                result, actual_prompt = intention_result, ""
                result['response'] = 'Let\'s work together next time.'
                decision_gm_fn = None
            else:
                # todo Are we willing to accept it? gameinfo 与 save_data
                # todo use intention_result instead req
                req = {"bargain_cnt": 0, **req, **intention_result}
                try:
                    response, actual_prompt = CivAgent.bargain(req, save_data, model=model)
                except Exception as e:
                    logger.exception(f"error in bargain {e}: ")
                    actual_prompt = ""
                    response = {
                        "response": "This transaction is a bit complicated; "
                                    + "please send it to me in the game trade interface.",
                        "bargain_result": "no"
                    }
                    result = {**intention_result, **response}
                    return result, actual_prompt, decision_gm_fn

                if response.get('bargain_result', "") == 'yes':
                    result, actual_prompt = intention_result, ""
                    result['response'] = 'Excellent, we have reached a mutually beneficial trade agreement.'
                    key = 'propose_trade'
                    # info = {**req, **intention_result}
                    param = [req[x] for x in action_space.decision_space[key]['param']]
                    # todo gm_fn Support for composition
                    decision_gm_fn = action_space.decision_space[key]['func']('yes')(*param)
                elif response.get('bargain_result', "") == 'no':
                    response['response'] = ('I\'m tired from all the bargaining. '
                                            'Let\'s just leave it for this time, and cooperate next time.')
                else:
                    bargain_cnt = intention_result.get("bargain_cnt", 0)
                    result = {**intention_result, **response, "bargain_cnt": bargain_cnt + 1}
            return result, actual_prompt, decision_gm_fn
        elif intention_result.get('doublecheck', '') == 'yes':
            # decision_making
            # 上一个Intention
            intention = intention_result['intention']
            random.seed(req.get('round', 0))
            decision_raw, decision, decision_gm_fn = utils.get_decision_result(intention, req, save_data,
                                                                               use_random=use_random)
            req['decision_result_raw'] = decision_raw
            req['decision_result'] = decision
            # req['decision_reason'] = 'My military strength is much greater than yours.'
            req['decision_reason'] = utils.get_decision_reason(decision_raw, intention, req, save_data,
                                                               use_random=use_random)
            # response
            prompt_str, prompt_config = prompt_utils.prompt_make(intention, req)
            response, _, actual_prompt = workflow_utils.run_workflows({
                "prompt": prompt_str,
                **prompt_config,
            }, model, force_json=False)
            response = utils.extract_quotes_text(response)
            result = {
                **intention_result,
                "response": response,
                "decision_result": req['decision_result'],
                "decision_reason": req['decision_reason']
            }
            return result, actual_prompt, decision_gm_fn
        else:
            # reply directly
            if intention_result.get('intention', '') == 'nonsense':
                return {**intention_result, "decision_result": "close"}, "", None
            else:
                return {**intention_result, "decision_result": "continue"}, "", None

    @staticmethod
    def reply_trade_of_skills(gameinfo, civ1_name, civ2_name, config_data):
        gameinfo = json_load_defaultdict(gameinfo)
        ind_1 = get_civ_index(gameinfo, civ1_name)
        civ2_name = fix_civ_name(civ2_name)
        civ1_name = fix_civ_name(civ1_name)
        turn = gameinfo['turns']
        if isinstance(turn, collections.defaultdict):
            turn = 1
        else:
            turn = int(turn)
        their_offers = {}
        our_offers = {}
        standard_dicts = [
            json.loads(json.dumps(item, default=lambda x: dict(x)))
            for item in gameinfo['civilizations'][ind_1]['tradeRequests']
        ]
        if 'theirOffers' in standard_dicts[0]['trade']:
            their_offers = {'theirOffers': standard_dicts[0]['trade']['theirOffers'][0]}
        if 'ourOffers' in standard_dicts[0]['trade']:
            our_offers = {'ourOffers': standard_dicts[0]['trade']['ourOffers'][0]}

        if our_offers['ourOffers']['type'] == 'WarDeclaration':
            trade = 'Invite us to attack {ourOffers[name]}'
        elif their_offers['theirOffers']['type'] == 'Gold_Per_Turn':
            trade = 'Exchange {theirOffers[amount]} gold for our {ourOffers[name]} each round'
        else:
            trade = 'Use {theirOffers[name]} in exchange for our {ourOffers[name]}'
        robot_name = civ1_name.lower()
        speaker = civ2_name.lower()
        agent = CivAgent(
            default_from_name, robot_name, "", "", gameinfo, default_gameid
        )
        agent.init()
        agent.update(gameinfo)

        req = save2req(
            gameinfo, agent, text='', speaker_civ_name=speaker, receiver_civ_name=robot_name
        )
        req['short_term'] = agent.short_term
        proposal = {
            'param': {'civ_name': speaker},
            'skill_name': trade.format(**their_offers, **our_offers)
        }
        model = config_data[robot_name]['model']
        to_civ_workflow = config_data[robot_name]['workflow']
        if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
            prompt_decision = AgentPrompt_analyze.format(**req, **proposal)
        else:
            prompt_decision = AgentPrompt_reply_noworkflow.format(**req, **proposal)
        decision, _, _ = workflow_utils.run_workflows(
            req={"prompt": prompt_decision, **req, **proposal},
            model=model, force_json=False, decision=True, workflow=to_civ_workflow
        )
        if isinstance(decision, dict):
            decision = decision['decision']
        if decision == 'yes':
            logger.debug(
                f"""On the {turn} turn, {civ1_name} agrees to {civ2_name}'s """
                + f"""{trade.format(**their_offers, **our_offers)} request --success"""
            )
        else:
            logger.debug(
                f"""On the {turn} turn, {civ1_name} denies {civ2_name}'s  """
                + f"""{trade.format(**their_offers, **our_offers)} request --fail"""
            )
        pair_dict = {"result": decision}
        json_data = json.dumps(pair_dict)
        return json_data

    @staticmethod
    def get_inner_state(save_data, civ_ind):
        inner_state = save_data["civilizations"][civ_ind].get("inner_state", {})
        return inner_state

    def set_inner_state(self, save_data):
        civ_ind = self.civ_ind
        data = {
            "objective": self.objective,
            "enemy_civs": list(self.enemy_civs),
            "friend_civs": list(self.friend_civs),
            "potential_enemy_civs": list(self.potential_enemy_civs),
            "potential_friend_civs": list(self.potential_friend_civs)
        }
        save_data["civilizations"][civ_ind]["inner_state"] = data
        return save_data
