from copy import deepcopy
import random
import collections
import ujson as json
from civagent import default_gameid, default_from_name
import civagent.utils.memory_utils
import civagent.utils.utils
from civagent.utils import workflow_utils
from civagent.search import Search
from civagent.utils.prompt_utils import prompt_make, response_make
from civsim import utils, action_space
from civagent import action_space as agent_action_space
from civagent import logger
from civagent.utils import prompt_utils
from civsim.utils import json_load_defaultdict, get_civ_index, fix_civ_name
from civagent.utils import workflow_utils
from civagent.utils.utils import save2req
from civagent.utils.prompt_utils import admin_reply_make
from civagent.action_space import intention_space
from civagent.config import config_data


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
        self.last_plans = []

    def init(self):
        for civ_name in self.civ_names:
            if civ_name != self.civ_name:
                # todo Persist to the save file, update more keys
                diplomatic_status = utils.get_diplomatic_status(self.game_info, self.civ_ind, civ_name)
                # relation = utils.get_relation(self.game_info, self.civ_ind, civ_name)
                proximity = utils.get_proximity(self.game_info, self.civ_ind, civ_name)
                self.relations[f"{self.civ_name}#{civ_name}"] = {
                    # todo
                    "closeness": "Unfamiliar",
                    "expected_closeness": "Unfamiliar",
                    "diplomatic_status": diplomatic_status,
                    "proximity": proximity,
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
                if relation in (
                        action_space.RelationSpace.ALLY.value,
                        action_space.RelationSpace.FRIEND.value
                ):
                    self.friend_civs.add(civ_name)
                if relation in (
                        action_space.RelationSpace.ENEMY.value,
                        action_space.RelationSpace.UNFORGIVABLE.value
                ):
                    self.enemy_civs.add(civ_name)
                if expected_relation in (
                        action_space.RelationSpace.ALLY.value,
                        action_space.RelationSpace.FRIEND.value
                ):
                    self.potential_friend_civs.add(civ_name)
                if expected_relation in (
                        action_space.RelationSpace.ENEMY.value,
                        action_space.RelationSpace.UNFORGIVABLE.value
                ):
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
        # todo Write to the save file.
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
    def bargain(req, game_info):
        if 'bottom_line' not in req:
            border_info = CivAgent.get_resource_border(req, game_info)
            req = {**req, **border_info}
            try:
                bottom_line = CivAgent.get_trade_bottom_line(req, game_info, req['bargain_role'])
            except Exception as e:
                logger.exception(f'error in bargain:get_trade_bottom_line.', exc_info=True)
                bottom_line = {'bottom_line': [{'category': 'Gold', 'item': 'Gold', 'amount': 120}]}
            logger.debug(f"debug in bargain bottom_line:{bottom_line}")
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
            {"prompt": prompt_str, 'llm_config': prompt_config}, decision=True
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
    def extract_trades(intention, req):
        req["item_category_space"] = action_space.item_category_space
        req["item_detail_space"] = action_space.item_detail_space
        req["intention_space"] = agent_action_space.intention_space
        prompt_str, prompt_config = prompt_utils.prompt_make(
            intention + '_identify', req
        )
        identify_result, _, actual_prompt = workflow_utils.run_workflows(
            {"prompt": prompt_str, 'llm_config': prompt_config}, force_json=True
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
        # todo The player may have entered two sentences;
        #  the player's debug information is noted in the receiver's reply;
        #  pair them using the UUID.
        last_dialogue_receiver = [
            x for x in req.get('dialogue_history', [{}])
            if x['fromCiv'] == req['receiver_persona']['civ_name'].lower()
        ]
        last_dialogue_receiver = last_dialogue_receiver[-1] if len(last_dialogue_receiver) > 0 else {}
        if 'debugInfo' in last_dialogue_receiver:
            try:
                last_dialogue_receiver['debugInfo'] = json.loads(last_dialogue_receiver['debugInfo'])
            except Exception:
                last_dialogue_receiver['debugInfo'] = {}
                logger.exception(
                    f"error in json.loads for get_last_dialogue: {last_dialogue_receiver['debugInfo']}",
                    exc_info=True
                )
        else:
            last_dialogue_receiver['debugInfo'] = {}
        # last_intention_degree = last_dialogue_receiver.get('debug_info', {}).get('intention_degree', '')
        # last_intention = last_dialogue_receiver.get('debug_info', {}).get('intention', '')
        # last_intention_doublecheck = last_dialogue_receiver.get('debug_info', {}).get('doublecheck', '')
        # last_intention_bargainresult = last_dialogue_receiver.get('debug_info', {}).get('bargain_result', '')
        return last_dialogue_receiver

    @staticmethod
    def bargin_intention(raw_intention, last_dialogue, req):
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
            intention_result = {
                **last_dialogue, "intention": "trade_bargain",
                "bargain_result": "no", "bargain_cnt": bargain_cnt + 1
            }
        else:
            # The other side put forward a new proposal
            actual_prompt = ""
            try:
                civ1_resource_dict, civ2_resource_dict, identify_result, actual_prompt = CivAgent.extract_trades(
                    'propose_trade', req
                )
            except Exception as e:
                logger.exception(f'error in bargain:extract_trades {e}:', exc_info=True)
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

    @staticmethod
    def intention_correct(intention_task_reply, req, only_chat):
        assert isinstance(intention_task_reply, dict), type(intention_task_reply)
        raw_intention, intention_degree, intention, response = "", "", "", ""
        intention_str = intention_task_reply.get('intention', 'chat')
        for k in intention_space:
            if k in intention_str:
                raw_intention = k
        raw_intention = "nonsense" if len(raw_intention) < 1 else raw_intention
        # pattern = r"degree.{0,4}weak"
        intention_degree = intention_task_reply.get('degree', 'weak')
        if raw_intention in ("open_border", "nonsense"):
            intention = raw_intention
            intention_degree = 'strong'
        elif intention_degree != "strong":
            intention = "chat"
        else:
            intention = raw_intention
        response = intention_task_reply.get('reply', '')
        intention_result = {
            "raw_intention": raw_intention,
            "intention_degree": intention_degree,
            "intention": intention,
            "response": response
        }

        if intention == 'nonsense':
            intention_result['response'] = response_make('nonsense', req)

        if only_chat:
            return intention_result

        if intention_degree == 'strong' and intention in 'seek_peace' and not req.get('is_at_war', False):
            intention_result['response'] = response_make('seek_peace', req)
            intention_result['intention'] = 'chat'
            return intention_result

        # todo decision of common_enemy
        if intention_degree == 'strong' and intention in ('common_enemy',):
            intention_result['response'] += response_make('common_enemy', req)
            intention_result['intention'] = 'chat'
            return intention_result

        if intention_degree == 'strong' and intention in ('ask_for_object', 'propose_trade'):
            try:
                civ1_resource_dict, civ2_resource_dict, identify_result, _ \
                    = CivAgent.extract_trades(intention, req)
            except Exception as e:
                logger.exception(f'error in bargain:extract_trades {e}:', exc_info=True)
                return {
                    **intention_result,
                    "intention": 'chat',
                    "response": response_make('propose_trade', req)
                }
            if len(civ2_resource_dict) + len(civ1_resource_dict) == 0:
                # ask_for_object nothing
                intention_result['intention'] = 'chat'
                return intention_result
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
            model = config_data[req['civ_name'].lower()]['model'] \
                if req.get('llm_model', '') == '' \
                else req['llm_model']
            prompt, prompt_config = prompt_utils.prompt_make(
                'doublecheck_rewrite',
                context_dict={**req, **intention_result}
            )
            response, _, _ = workflow_utils.run_workflows(
                req={'llm_config': prompt_config, "prompt": prompt},
                model=model, force_json=False, decision=True, workflow=False
            )
            intention_result['response'] = response
            # logger.error(f'LLM intention understanding warning: get {response} for {actual_prompt}.')
        return intention_result

    @staticmethod
    def intention_understanding(req, only_chat=False):
        """
        text->
        if There is the last bargain tag identification content + identification is successful -> response
        if There is no doublecheck tag intent recognition->if you intend to reply directly; if strong intent plus doublecheck tag if identifies content for trade； -> Don't call the response function
        if There is the last doublecheck tag check identification -> if trade goes bargain in response； else decision
        """
        req["item_category_space"] = action_space.item_category_space
        req["item_detail_space"] = action_space.item_detail_space
        req["intention_space"] = agent_action_space.intention_space
        last_dialogue = CivAgent.get_last_dialogue(req)['debugInfo']
        if not only_chat and last_dialogue.get('bargain_result', '') == 'continue':
            intention = 'bargain'
        elif not only_chat and last_dialogue.get('doublecheck', '') == 'wait':
            intention = 'doublecheck'
        else:
            intention = 'intention_understanding'
        logger.info(f"intention_understanding: {intention}, last_dialogue: {last_dialogue}")
        # doublecheck
        if intention == 'bargain':
            prompt_str, prompt_config = prompt_utils.prompt_make(
                "doublecheck", req
            )
            raw_intention, response, actual_prompt = workflow_utils.run_workflows(
                {"prompt": prompt_str, 'llm_config': prompt_config}
            )
            # The judgment of whether the other party agrees or not
            intention_result, actual_prompt = CivAgent.bargin_intention(raw_intention, last_dialogue, req)
            return intention_result, actual_prompt

        elif intention == 'doublecheck':
            prompt_str, prompt_config = prompt_utils.prompt_make(
                "doublecheck", req
            )
            raw_intention, response, actual_prompt = workflow_utils.run_workflows(
                {"prompt": prompt_str, 'llm_config': prompt_config}
            )
            logger.debug(f"doublecheck result of {req['utterance']} is {raw_intention}")
            if raw_intention.get('doublecheck', '') == 'yes':
                raw_intention = {**last_dialogue, **raw_intention}
                return raw_intention, actual_prompt
            # todo raw_intention.get('doublecheck', '') == 'continue'
            else:
                raw_intention['response'] = response_make('doublecheck', req)
                raw_intention = {**last_dialogue, **raw_intention}
                return raw_intention, actual_prompt
        # if type == 'intention_understanding':
        else:
            # intention_understanding
            prompt_str, prompt_config = prompt_utils.prompt_make(
                "intention_understanding", req
            )
            raw_intention, response, actual_prompt = workflow_utils.run_workflows(
                {"prompt": prompt_str, 'llm_config': prompt_config}
            )
            intention_result = CivAgent.intention_correct(raw_intention, req, only_chat)

            return intention_result, actual_prompt

    @staticmethod
    def response(req, intention_result, save_data={}, use_random=False):
        if (intention_result.get('doublecheck', '') == 'yes'
                and intention_result.get('intention', '') == 'propose_trade'
                or (intention_result.get('intention', '') == 'trade_bargain')):
            # bargain
            result, actual_prompt, decision_gm_fn = CivAgent.response_bargin(
                req, intention_result, save_data

            )
            return result, actual_prompt, decision_gm_fn

        elif intention_result.get('doublecheck', '') == 'yes':
            # prev Intention
            intention = intention_result['intention']
            random.seed(req.get('round', 0))
            decision_raw, decision, decision_gm_fn = utils.get_decision_result(
                intention, req, save_data, use_random=use_random
            )
            req['decision_result_raw'] = decision_raw
            req['decision_result'] = decision
            # req['decision_reason'] = 'My military strength is much greater than yours.'
            req['decision_reason'] = utils.get_decision_reason(
                decision_raw, intention, req, save_data, use_random=use_random
            )
            # response
            prompt_str, prompt_config = prompt_utils.prompt_make(intention, req)
            response, _, actual_prompt = workflow_utils.run_workflows({
                "prompt": prompt_str,
                'llm_config': prompt_config,
            }, force_json=False)
            response = utils.extract_quotes_text(response)
            if decision_raw == 'yes':
                response = response + admin_reply_make('agree_trade', {}),
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
    def response_bargin(req, intention_result, save_data):
        req['bargain_role'] = 'seller'
        result = ''
        decision_gm_fn = None
        if intention_result.get('bargain_result', "") == 'yes':
            result, actual_prompt = intention_result, ""
            result["response"] = response_make('bargain_result_yes', req)
            key = 'propose_trade'
            param = [req[x] for x in action_space.decision_space[key]['param']]
            # todo gm_fn Support for composition
            decision_gm_fn = action_space.decision_space[key]['func']('yes')(*param)
        elif intention_result.get('bargain_result', "") == 'no':
            result, actual_prompt = intention_result, ""
            result['response'] = response_make('bargain_result_no', req)
            decision_gm_fn = None
        else:
            req = {"bargain_cnt": 0, **req, **intention_result}
            try:
                response, actual_prompt = CivAgent.bargain(req, save_data)
            except Exception as e:
                logger.exception(f"error in bargain {e}: ", exc_info=True)
                actual_prompt = ""
                response = {
                    "response": response_make('propose_trade', req),
                    "bargain_result": "no"
                }
                result = {**intention_result, **response}
                return result, actual_prompt, decision_gm_fn

            if response.get('bargain_result', "") == 'yes':
                result, actual_prompt = intention_result, ""
                result['response'] = response_make('bargain_success', req)
                key = 'propose_trade'
                # info = {**req, **intention_result}
                param = [req[x] for x in action_space.decision_space[key]['param']]
                # todo gm_fn Support for composition
                decision_gm_fn = action_space.decision_space[key]['func']('yes')(*param)
            elif response.get('bargain_result', "") == 'no':
                response['response'] = response_make('bargain_fail', req)
            else:
                bargain_cnt = intention_result.get("bargain_cnt", 0)
                result = {**intention_result, **response, "bargain_cnt": bargain_cnt + 1}
        return result, actual_prompt, decision_gm_fn

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
        # standard_dicts = [
        #     json.loads(json.dumps(item, default=lambda x: dict(x)))
        #     for item in gameinfo['civilizations'][ind_1]['tradeRequests']
        # ]
        standard_dicts = gameinfo['civilizations'][ind_1]['tradeRequests']
        if 'theirOffers' in standard_dicts[0]['trade']:
            their_offers = {'theirOffers': standard_dicts[0]['trade']['theirOffers'][0]}
        if 'ourOffers' in standard_dicts[0]['trade']:
            our_offers = {'ourOffers': standard_dicts[0]['trade']['ourOffers'][0]}

        if our_offers['ourOffers'].get('type', '') == 'WarDeclaration':
            trade = 'Invite us to attack {ourOffers[name]}'
        elif their_offers['theirOffers'].get('type', '') == 'Gold_Per_Turn':
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
        model = config_data[robot_name]['model'] \
            if req.get('llm_model', '') == '' \
            else req['llm_model']
        to_civ_workflow = config_data[robot_name]['workflow']
        if to_civ_workflow == "True" or to_civ_workflow is True or to_civ_workflow == "true":
            prompt_decision, llm_config = prompt_make(
                'agent_analyze', context_dict={**req, **proposal}
            )
        else:
            prompt_decision, llm_config = prompt_make(
                'agent_reply_noworkflow', context_dict={**req, **proposal}
            )
        req['llm_config'] = llm_config
        decision, _, _ = workflow_utils.run_workflows(
            req={'llm_config': llm_config, "prompt": prompt_decision},
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
            "potential_friend_civs": list(self.potential_friend_civs),
            "last_plans": self.last_plans
        }
        save_data["civilizations"][civ_ind]["inner_state"] = data
        return save_data
