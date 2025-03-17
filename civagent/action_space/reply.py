ADMIN_REPLY = {
    "agree_trade": "Now you can  propose a formal transaction.",
    "successful_detection": "Successfully detected that you have entered the corresponding game save {gameid}. Start the game!",
    "failed_detection": "You have not entered the corresponding game save {gameid}, please open the game client first, enter the save from the multiplayer game!",
    "game_not_launched": "You have not entered the last game save {gameid}; Please open the game client first to access the save from the multiplayer game! If you have access to another save, get the multiplayer gameid from the game client and send it to me to launch the game: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "search_bot": "Search the Admin Bot to launch the game.",
    "join_game": "Join the game {gameid}!",
    "team_name": "CivAgent_Unciv_{gameid}",
    "querying_civ": "I am not in a game match. You can talk to civilizations including",
    "gm_command_success": "The GM command successfully executed.",
    "gm_command_error": "The GM command encountered an error when executed! Please enter the correct GM command or the latest gameid.",
    "LLM_error": "CivAgent encountered an error when executed!",
    "analysis_gm": """Your GM command is being analyzed. If you also want to join other game,
                    Get the multiplayer gameid from the game client and send it to me to start the game:
                    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                    """.replace(
        "\t", ""
    ),
    "gm_intro": """
                    Welcome to CivAgent Special Edition of Unciv, a Civ 5-like game driven by a large language model
                    You can freely initiate diplomatic conversations with AI bots on the discord platform and enjoy a deep gameplay experience during the confrontation of human-like AI.
                    You don't have to worry about your opponent being non-conversable/stupid like traditional AI, you don't have to worry about your opponent suddenly being offline, you don't have to worry about your little brother being tempted out of the game, you don't have to worry about being a supporting player in a strategy game without making money.
                    You can help us test the game by:
                    Step1: Start a new game, check the 'Online Multiplayer' box in the bottom left corner
                    Step2: In accordance with the game tutorial free play, expand the force, build an army
                    Step3: In your unique game pattern, use dialogue to test/conciliate/incorporate/threaten/deceive AI robots to achieve your strategic goals.
                    -------------------------------------------------
                    To speed up the game, we provide the following commands:
                    #add_gold 10000 You add 10000 gold
                    add_gold 10000 civ
                    #add_tech china
                    add_tech civ
                    #fast_build china Chinese civilization units quickly build
                    fast_build civ
                    #declare_war china rome Let China declare war on Rome
                    declare_war civ civ
                    #make_peace china rome #make_peace China Rome
                    make_peace civ civ
                    #open_border china rome Let China and Rome open their borders to each other
                    open_border civ civ
                    #form_ally china rome #form_ally China Rome
                    form_ally civ civ
                    #annex_city china rome rome Let China occupy Rome City of Rome, city name can be empty
                    annex_city civ civ city_name
                    civ includes [china|mongolia|rome|aztecs|greece|egypt]
                    --------------------------------------------------
                    Business simulation sandbox games have a natural 'emergence' mechanism, which is very suitable for the application of large language models.
                    Game start!
                    """.replace(
        "\t", ""
    ),
}


ADMIN_REPLY_CHINESE = {
    "agree_trade": "现在您可以提出正式交易了。",
    "successful_detection": "成功检测到您已进入对应游戏存档{gameid}。开始游戏!",
    "failed_detection": "您还没进入对应游戏存档{gameid}，请先开启游戏客户端，从多人游戏中进入该存档!",
    "game_not_launched": "检测到您还未进入上一次游戏存档{gameid}；请先开启游戏客户端，从多人游戏中进入该存档! 如果您进入了其他存档，请从游戏客户端获取多人游戏gameid发给我来启动游戏: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "search_bot": "请搜索管理员机器人启动游戏。",
    "join_game": "加入游戏 {gameid}!",
    "team_name": "CivAgent_Unciv_{gameid}'",
    "querying_civ": "我不在游戏对局中，可交谈文明包括",
    "gm_command_success": "GM指令成功。",
    "gm_command_error": "GM指令运行出错! 请输入正确的GM指令或最新的gameid。",
    "LLM_error": "大模型调用阶段出错!",
    "analysis_gm": """正在分析您的GM指令。如果您另外想进入其他存档，
                    请从游戏客户端获取多人游戏gameid发给我来启动游戏:
                    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                    """.replace(
        "\t", ""
    ),
    "gm_intro": """欢迎游玩 CivAgent版Unciv, 这是一款由大语言模型驱动的类《文明5》游戏
                    您可以在discord平台自由发起对AI机器人的外交对话，在类真人AI的对抗过程中享受深度游戏体验。
                    您不必担心您的对手像传统AI那样不可交谈/非常愚笨, 您不必担心您的对手突然下线，您不必担心您的小弟受到游戏外的诱惑，您不必担心不充钱只能做个战略游戏中的配角。
                    您可以通过以下几步帮我们测试游戏:
                    Step1:开始新游戏，勾选左下角的'在线多人游戏'
                    Step2:按照游戏内部教程自由游玩，扩展势力，建立军队
                    Step3:在您独特的游戏格局下，通过对话来试探/怀柔/收编/威胁/欺骗AI机器人，实现您的战略目标。
                    -------------------------------------------------
                    为了加快游戏进度，我们提供以下指令:
                    #add_gold 10000 你增加10000金币
                    add_gold 10000 civ
                    #add_tech china china文明科技快速完成
                    add_tech civ
                    #fast_build china china文明单位快速建造
                    fast_build civ
                    #declare_war china rome 让中华向罗马宣战
                    declare_war civ civ
                    #make_peace china rome 让中华与罗马和平
                    make_peace civ civ
                    #open_border china rome 让中华与罗马互相开放边境
                    open_border civ civ
                    #form_ally china rome 让中华与罗马互相同盟
                    form_ally civ civ
                    #annex_city china rome rome 让中华占领罗马的罗马城,城市名可为空
                    annex_city civ civ city_name
                    civ包括[china|mongolia|rome|aztecs|greece|egypt]
                    --------------------------------------------------
                    模拟经营沙盒类游戏不需要堆料就天然具有'涌现'机制，非常适合大语言模型的应用。
                    A game is a series of meaningful choices. -- Sid Meier
                    游戏开始!
                    """.replace(
        "\t", ""
    ),
}


EVENT_TRIGGER_REPLY = {
    "turn_event": "World events in round {turns}: {text}",
    "turn_event_default": "World events in round {turns}: nothing",
    "declare_war_event": "I've declared war on you.",
    "heard_war_event": "I heard you were attacked by {attack_civ_name}. Is there anything you would like to discuss with me diplomatically?",
    "time_out_event": " the reply has exceeded the time limit.",
}


EVENT_TRIGGER_REPLY_CHINESE = {
    "turn_event": "第{turns}回合的世界大事: {text}",
    "turn_event_default": "第{turns}回合的世界大事: 无",
    "declare_war_event": "我向你宣战了。",
    "heard_war_event": "听说你被{attack_civ_name}进攻了，你有什么想和我进行外交讨论的事宜吗？",
    "time_out_event": " 针对该回复已超时！",
}


INTENTION_RESPONSE = {
    "unknown_civ": "What civilization are you from? I haven't seen you before.",
    "doublecheck": "Then I made a mistake. Let 's get back to the game.",
    "nonsense": "Let's do less of these useless conversations and focus more on the development of our country.",
    "seek_peace": "We're not at war...",
    "common_enemy": "We will have to discuss the specific measures.",
    "propose_trade": "Your transaction is too complicated. Let's go to the transaction screen.",
    "bargain_result_yes": "It's very good. We've come to a mutually beneficial deal.",
    "bargain_result_no": "Let's work together next time.",
    "bargain_success": "Excellent, we have reached a mutually beneficial trade agreement.",
    "bargain_fail": "I'm tired from all the bargaining. Let's just leave it for this time, and cooperate next time.",
}


INTENTION_RESPONSE_CHINESE = {
    "unknown_civ": "你是哪个文明？我没有见过你。",
    "doublecheck": "那我搞错了。让我们重新回到游戏中",
    "nonsense": "我们还是少做这些无用的对话，多关注各自国家的发展。",
    "seek_peace": "我们并没有在战争……",
    "common_enemy": "我们必须讨论具体措施。",
    "propose_trade": "你的交易太复杂了。让我们转到交易界面进行。",
    "bargain_result_yes": "非常好。我们达成了一笔互利的交易。",
    "bargain_result_no": "下次让我们一起合作吧。",
    "bargain_success": "太好了，我们达成了互利的贸易协议。",
    "bargain_fail": "讨价还价弄得我累了。我们这次先不管它，下次再合作。",
}
