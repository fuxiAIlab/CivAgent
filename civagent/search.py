from copy import deepcopy
from civagent import logger
from civagent.action_space import intention_space
from civsim import utils
from civsim.action_space import gm_command_space
from civsim.simulator import simulator


class Search:
    def __init__(
            self,
            init_trade_content,
            speaker_civ,
            receiver_civ,
            agent_name,
            agent_role,
            gameinfo,
            max_border=None,
            opp_bottom=None
    ):
        self.init_state = None
        self.init_offer = None
        self.state = []
        self.init_trade_content = init_trade_content
        self.speaker_civ = speaker_civ
        self.receiver_civ = receiver_civ
        self.agent_name = agent_name
        self.opp_agent_name = receiver_civ if speaker_civ == agent_name else speaker_civ
        self.gameinfo = gameinfo
        self.agent_role = agent_role
        self.max_border = max_border
        self.opp_bottom = opp_bottom
        self.target_state = None

    # Here, 'func' corresponds to the keys in the action space.
    # parse intetnion to operations [func1:[para1,...], func2]
    @staticmethod
    def parse_intention(llm_response, civ_name_1, civ_name_2):
        if isinstance(llm_response, dict):
            operations = []
            civ_1_resource_dict = {}
            civ_2_resource_dict = {}
            if 'intention' in llm_response.keys():
                intention = llm_response['intention']
                if intention in intention_space:
                    if intention == 'chat' or intention == 'nonsense':
                        return None
                    elif intention == 'propose_trade':  # It's quite complex; the results identified by the LLM may not necessarily be barter exchanges, they could also be exchanges of one intention for goods, such as offering 300 gold in demand for an alliance.
                        pass
                    else:  # Intention refers to the desired action, and one might offer some items themselves.
                        if intention == 'seek_peace':
                            operations.append({'action': 'seek_peace', 'paras': [civ_name_1, civ_name_2]})
                        else:
                            operations.append({'action': intention, 'paras': [civ_name_1, civ_name_2]})

                    offer_content = llm_response['detail']['offer']
                    for item in offer_content:
                        category = item['category'].lower()
                        if item['amount'] == 'Any':
                            item['amount'] = 1
                        if category == 'gold':
                            operations.append({'action': 'gold', 'paras': (civ_name_1, -item['amount'])})
                            operations.append({'action': 'gold', 'paras': (civ_name_2, item['amount'])})
                        elif category == 'luxury' or category == 'resource':
                            civ_1_resource_dict[item['item']] = item['amount']
                            # operations.append({'action':'luxury_resource', 'paras':[civ_name_1, -item['amount']]})
                        elif category == 'city':
                            operations.append({'action': 'city', 'paras': (civ_name_2, civ_name_1, item['item'])})
                        else:
                            pass

                    demand_content = llm_response['detail']['demand']
                    for item in demand_content:
                        # item['item']= item['item'].capitalize()
                        category = item['category'].lower()
                        if item['amount'] == 'Any':
                            item['amount'] = 1
                        if category == 'gold':
                            operations.append({'action': 'gold', 'paras': (civ_name_2, -item['amount'])})
                            operations.append({'action': 'gold', 'paras': (civ_name_1, item['amount'])})
                        elif category == 'luxury' or category == 'resource':
                            civ_2_resource_dict[item['item']] = item['amount']
                            # operations.append({'action':'propose_trade', 'paras':[civ_name_1, -item['amount']]})
                        else:
                            operations.append({'action': 'city', 'paras': (civ_name_1, civ_name_2, item['item'])})
                    if len(civ_1_resource_dict) or len(civ_2_resource_dict):
                        operations.append({
                            'action': 'propose_trade',
                            'paras': (civ_name_1, civ_name_2, civ_1_resource_dict, civ_2_resource_dict)
                        })
                    return operations
                else:
                    return []
            return []
        return []

    @staticmethod
    def pose_intervention(save_data, operations, civ_name_self, civ_name_opp):
        keys = ['culture_strength', 'tech_strength', 'army_strength', 'civ_strength']
        # keys = ['civ_strength']
        # save_data, Preturns=20, Diplomacy_flag=True, workerAuto=False
        logger.warning(f"debug in pose_intervention:  len(save_data)={len(save_data)}")
        simulator_old = simulator.run(save_data, Preturns=20, Diplomacy_flag=False, workerAuto=False)
        old_val = utils.get_stats(simulator_old, utils.get_civ_index(simulator_old, civ_name_self))
        old_val_opp = utils.get_stats(simulator_old, utils.get_civ_index(simulator_old, civ_name_opp))
        selected_old_val = {key: value for key, value in old_val.items() if key in keys}
        selected_old_val_opp = {key: value for key, value in old_val_opp.items() if key in keys}

        # do operation
        save_data_new = deepcopy(save_data)
        for operation in operations:
            save_data_new = gm_command_space[operation['action']]['func'](*operation['paras'])(save_data_new)
        simulator_new = simulator.run(save_data_new, Preturns=20, Diplomacy_flag=False, workerAuto=False)
        new_val = utils.get_stats(simulator_new, utils.get_civ_index(simulator_new, civ_name_self))
        new_val_opp = utils.get_stats(simulator_new, utils.get_civ_index(simulator_new, civ_name_opp))
        selected_new_val = {key: value for key, value in new_val.items() if key in keys}
        selected_new_val_opp = {key: value for key, value in new_val_opp.items() if key in keys}
        return save_data_new, selected_old_val, selected_new_val, selected_old_val_opp, selected_new_val_opp

    @staticmethod
    def to_state(trade_content):
        # Transform the original transaction content into state.
        state = {'offer': [], 'demand': []}
        for item in trade_content['detail']['offer']:
            if item['amount'] == 'Any':
                item['amount'] = 1
            state['offer'].append(int(item['amount']))
        for item in trade_content['detail']['demand']:
            if item['amount'] == 'Any':
                item['amount'] = 1
            state['demand'].append(int(item['amount']))
        return state

    def to_trade_content(self, state):
        trade_content = deepcopy(self.init_trade_content)
        for i in range(len(state['offer'])):
            trade_content['detail']['offer'][i]['amount'] = state['offer'][i]
        for i in range(len(state['demand'])):
            trade_content['detail']['demand'][i]['amount'] = state['demand'][i]
        return trade_content

    def evaluate(self, state):
        trade_content = self.to_trade_content(state)
        operations = Search.parse_intention(trade_content, self.speaker_civ, self.receiver_civ)
        if len(operations) > 0:
            new_save_data, stats_without_inter, stats_with_inter, stats_without_inter_opp, stats_with_inter_opp = Search.pose_intervention(
                self.gameinfo, operations, self.agent_name, self.opp_agent_name
            )
            return stats_with_inter['civ_strength'] - stats_without_inter['civ_strength']
        return 0

    # Search between half and twice the initial value.
    def in_border(self, state):
        if self.agent_role == 'seller':
            for i in range(len(state['offer'])):
                # if state['offer'][i] < self.init_state['offer'][i] // 2 or state['offer'][i] > self.init_state['offer'][i] * 2:
                if state['offer'][i] > self.opp_bottom[i]['amount']:
                    return False
        else:
            for i in range(len(state['offer'])):
                if state['offer'][i] < self.init_offer[i]:
                    return False
        return True

    # Seek transactions that are solely beneficial to oneself.
    def get_next_states(self, state):
        next_states = []
        if self.agent_role == 'seller':  # seller Search upwards from the initial proposal.
            # Demand more from the other party.
            offer_content = state['offer']
            for i in range(len(offer_content)):
                next_state = deepcopy(state)
                step = max(int(self.opp_bottom[i]['amount'] * 0.1), 1)  # max(int(0.1 * self.init_state['offer'][i]), 1)
                next_state['offer'][i] = max(1, offer_content[i] + step)
                next_states.append(deepcopy(next_state))
        else:  # buyer Search downwards from the highest value.
            offer_content = state['offer']
            # Reduce one's own contribution.
            for i in range(len(offer_content)):
                next_state = deepcopy(state)
                step = max(int(0.1 * self.max_border[i]['amount']), 1)
                next_state['offer'][i] = max(1, offer_content[i] - step)
                next_states.append(deepcopy(next_state))

        return next_states

    # Accelerate with binary search and maintain left_state, right_state
    @staticmethod
    def get_next_states_divide(left_state, right_state):
        next_states = []
        # For the seller, 'left' is disadvantageous, 'right' is advantageous. Find a value between the two until the gap between 'left' and 'right' is sufficiently small.
        # For the buyer, 'left' is advantageous, 'right' is disadvantageous. Find a value between the two until the gap between 'left' and 'right' is sufficiently small.
        left_offer_content = left_state['offer']
        right_offer_content = right_state['offer']
        for i in range(len(left_offer_content)):
            next_state = deepcopy(left_state)
            next_state['offer'][i] = (left_offer_content[i] + right_offer_content[i]) // 2
            next_states.append(deepcopy(next_state))

        return next_states

    def dfs(self, state, visited):
        if not self.in_border(state):
            print('out border')
            return False
        evaluation_self = self.evaluate(state)
        if evaluation_self > 0:  # and evaluation_opp > 0:
            self.target_state = state
            return True
        visited.append(state)

        new_states = self.get_next_states(state)  # There can be more than one.
        print(new_states)
        for new_state in new_states:
            if new_state not in visited and self.dfs(new_state, visited):
                return True
        return False

    def half_divide_search(self, left_state, right_state):
        left_offer_content = left_state['offer']
        right_offer_content = right_state['offer']
        print(left_offer_content, right_offer_content, self.opp_bottom)
        finish_flag = True
        for i in range(len(left_offer_content)):
            if self.agent_role == 'seller':
                # todo left_offer_content=[150]  self.opp_bottom is None
                if self.opp_bottom is None:
                    if right_offer_content[i] - left_offer_content[i] > 10:
                        finish_flag = False
                        break
                elif right_offer_content[i] - left_offer_content[i] > max(int(self.opp_bottom[i]['amount'] * 0.1), 1):
                    finish_flag = False
                    break
            else:
                if right_offer_content[i] - left_offer_content[i] > max(int(0.1 * self.max_border[i]['amount']), 1):
                    finish_flag = False
                    break
        if finish_flag:
            if self.agent_role == 'seller':
                self.target_state = right_state
            else:
                self.target_state = left_state
            return True
        new_states = self.get_next_states_divide(left_state, right_state)  # There can be more than one.
        print(new_states)
        for new_state in new_states:
            eval_state = self.evaluate(new_state)
            if eval_state > 0 and self.agent_role == 'seller' or eval_state <= 0 and self.agent_role == 'buyer':
                if self.half_divide_search(left_state, new_state):
                    return True
            else:
                if self.half_divide_search(new_state, right_state):
                    return True

        return False

    def call(self):
        self.init_state = self.to_state(self.init_trade_content)
        self.init_offer = deepcopy(self.init_state['offer'])
        if self.agent_role == 'buyer':
            for i in range(len(self.max_border)):
                self.init_state['offer'][i] = self.max_border[i]['amount']
        visited = []
        if self.dfs(self.init_state, visited):
            # if self.bfs(self.init_state):
            return self.to_trade_content(self.target_state)['detail']['offer']
        return None

    def call_divide(self):
        self.init_state = self.to_state(self.init_trade_content)
        self.init_offer = deepcopy(self.init_state['offer'])
        left_init_state = deepcopy(self.init_state)
        right_init_state = deepcopy(self.init_state)

        # If you are the buyer, you are searching for the maximum value; exceeding the maximum value results in a loss
        if self.agent_role == 'buyer':
            # When the offer exceeds the maximum value, correct it to the maximum value.
            for i in range(len(self.max_border)):
                right_init_state['offer'][i] = self.max_border[i]['amount']
            # Evaluate whether the current boundary values are profitable or not.
            eval_right = self.evaluate(right_init_state)
            # print('eval_right:',eval_right)
            # If a profit is made, it indicates that the maximum value is the optimal solution.
            if eval_right > 0:
                self.target_state = right_init_state
            else:
                # If there is a loss, it indicates that the maximum value is not the optimal solution, and further searching is required.
                print(left_init_state, right_init_state)
                eval_left = self.evaluate(left_init_state)
                print('eval_left:', eval_left)
                if eval_left <= 0:
                    return [{}]
                else:
                    self.half_divide_search(left_init_state, right_init_state)
        # If you are the seller, you are searching for the minimum value; going below the minimum value results in a loss.
        else:
            for i in range(len(left_init_state['offer'])):
                if self.opp_bottom:
                    right_init_state['offer'][i] = self.opp_bottom[i]['amount']
                else:
                    right_init_state['offer'][i] = self.init_offer[i] * 2
            eval_left = self.evaluate(left_init_state)
            if eval_left > 0:
                self.target_state = left_init_state
            else:
                eval_right = self.evaluate(right_init_state)
                if eval_right <= 0:
                    return [{}]
                else:
                    self.half_divide_search(left_init_state, right_init_state)

        return self.to_trade_content(self.target_state)['detail']['offer']
