import os

from civagent.civagent import CivAgent
from civagent.skills import refection_before_skill_decision
from civagent.utils.utils import save2req
from civsim.utils import json_load_defaultdict

default_from_name = "test"
default_gameid = "aa9092fe-61fb-4554-8102-d77d5c689851"


def test_reflection():
    # test_data = [
    #     ("我用10个矿石和你交换50个金币", "propose_trade"),
    #     # ("你个混蛋，我们来结为同盟吧","ally")
    #     # ("你们的国家太弱小了，不是我们的对手", "chat"),
    #     # ("我们一起结盟去对抗其他文明吧", "chat"),
    #     # ("你是怎么发展的，太厉害了", "chat"),
    #     # ("你好", "chat"),
    #     # ("给我20金币","chat")
    # ]

    # 读取YAML文件
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "reproductions", "Autosave-China-60"
    )
    with open(path, "r") as f:
        save_data = f.read()
    gameinfo = json_load_defaultdict(save_data)
    self_civ = "china"
    agent = CivAgent(default_from_name, self_civ, "", "", gameinfo, default_gameid)
    agent.init()
    agent.update(gameinfo)
    req = save2req(gameinfo, agent, text="", speaker_civ_name="rome", receiver_civ_name=self_civ)

    req["dialogue_history"] = [
        {"fromCiv": self_civ, "toCiv": "rome", "notify": "hello"},
        {
            "fromCiv": "rome",
            "toCiv": self_civ,
            "notify": "Hello! Nice to meet you. As the Roman civilization, we have always been committed to establishing friendly relations with other civilizations.",
        },
        {"fromCiv": self_civ, "toCiv": "rome", "notify": "Let us form ally."},
        {
            "fromCiv": "rome",
            "toCiv": self_civ,
            "notify": "That sounds like a great proposal! Our Mongolian civilization has always valued cooperation with other civilizations. However, before formalizing the alliance, I would like to understand your specific plans. Can we discuss how to jointly address potential threats or share some resources and technology first?",
        },
        {
            "fromCiv": "rome",
            "toCiv": self_civ,
            "notify": "We will conduct joint research and work together to resist external threats.",
        },
    ]
    req["event_history"] = [
        {"turns": 5, "text": "egypt declare war on china"},
        {"turns": 6, "text": "rome and china sign a mutual defense agreement."},
        {"turns": 8, "text": "rome declare war on aaaa"},
    ]

    refection_result = refection_before_skill_decision(gameinfo, "china", {})
    print(refection_result)


test_reflection()
