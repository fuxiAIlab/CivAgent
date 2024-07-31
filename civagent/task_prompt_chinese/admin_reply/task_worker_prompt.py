ADMIN_REPLY = {
    'agree_trade': '现在您可以提出正式交易了。',
    'successful_detection': '成功检测到您已进入对应游戏存档{gameid}。开始游戏!',
    'failed_detection': '您还没进入对应游戏存档{gameid}，请先开启游戏客户端，从多人游戏中进入该存档!',
    'game_not_launched': '检测到您还未进入上一次游戏存档{gameid}；请先开启游戏客户端，从多人游戏中进入该存档! 如果您进入了其他存档，请从游戏客户端获取多人游戏gameid发给我来启动游戏: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    'search_bot': '请搜索管理员机器人启动游戏。',
    'join_game': '加入游戏 {gameid}!',
    "team_name": "CivAgent_Unciv_{gameid}'",
    'querying_civ': '我不在游戏对局中，可交谈文明包括',
    'gm_command_success': 'GM指令成功。',
    'gm_command_error': 'GM指令运行出错! 请输入正确的GM指令或最新的gameid。',
    'LLM_error': '大模型调用阶段出错!',
    'analysis_gm': """正在分析您的GM指令。如果您另外想进入其他存档，
                    请从游戏客户端获取多人游戏gameid发给我来启动游戏: 
                    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                    """.replace('\t', ''),
    'gm_intro': """欢迎游玩 CivAgent版Unciv, 这是一款由大语言模型驱动的类《文明5》游戏
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
                    """.replace('\t', '')
}
