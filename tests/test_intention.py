import os

import civsim.simulator.simulator as simulator
from civagent.civagent import CivAgent
from civagent.utils.utils import save2req
from civsim.utils import json_load_defaultdict


simulator.init_jvm()

default_from_name = "test"
default_gameid = "aa9092fe-61fb-4554-8102-d77d5c689851"


def test_intention_understand():
    test_data = [
        ("我想要跟你结盟", "propose_trade"),
        # ("你个混蛋，我们来结为同盟吧","ally")
        # ("你们的国家太弱小了，不是我们的对手", "chat"),
        # ("我们一起结盟去对抗其他文明吧", "chat"),
        # ("你是怎么发展的，太厉害了", "chat"),
        # ("你好", "chat"),
        # ("给我20金币","chat")
    ]

    # 读取YAML文件
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "reproductions", "Autosave-China-60"
    )
    with open(path, "r") as f:
        save_data = f.read()
    gameinfo = json_load_defaultdict(save_data)
    agent = CivAgent(default_from_name, "china", "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)
    req = save2req(gameinfo, agent, text="", speaker_civ_name="rome", receiver_civ_name="china")
    # print(req)
    for i, test_data_tmp in enumerate(test_data):
        utterance, correct_intention = test_data_tmp
        req["utterance"] = utterance
        req["dialogue_history"] = []
        intention_result = CivAgent.intention_understand(req, only_chat=True)
        print(intention_result)

        response_d, decision_gm_fn = CivAgent.response(req, intention_result, path, use_random=False)
    print("#" * 30)


test_intention_understand()
