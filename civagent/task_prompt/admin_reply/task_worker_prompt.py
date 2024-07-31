ADMIN_REPLY = {
    'agree_trade': 'Now you can  propose a formal transaction.',
    'successful_detection': 'Successfully detected that you have entered the corresponding game save {gameid}. Start the game!',
    'failed_detection': 'You have not entered the corresponding game save {gameid}, please open the game client first, enter the save from the multiplayer game!',
    'game_not_launched': 'You have not entered the last game save {gameid}; Please open the game client first to access the save from the multiplayer game! If you have access to another save, get the multiplayer gameid from the game client and send it to me to launch the game: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    'search_bot': 'Search the Admin Bot to launch the game.',
    'join_game': 'Join the game {gameid}!',
    'team_name': 'CivAgent_Unciv_{gameid}',
    'querying_civ': 'I am not in a game match. You can talk to civilizations including',
    'gm_command_success': 'The GM command successfully executed.',
    'gm_command_error': 'The GM command encountered an error when executed! Please enter the correct GM command or the latest gameid.',
    'LLM_error': 'CivAgent encountered an error when executed!',
    'analysis_gm': """Your GM command is being analyzed. If you also want to join other game,
                    Get the multiplayer gameid from the game client and send it to me to start the game: 
                    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                    """.replace('\t', ''),
    'gm_intro': """
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
                    """.replace('\t', '')
}
