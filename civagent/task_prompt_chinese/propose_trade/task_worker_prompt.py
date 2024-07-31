from civagent.task_prompt_chinese.prompt_hub import AskForObjectIdentifyDataModel, BargainBuyerDataModel, BargainSellerDataModel

ProposeTradePrompt_Identify = """
请你根据识别出"{utterance}"这句话中提出的交易内容，不需要多余的猜测与推断延伸。
按以下要求以json格式返回你识别出的交易内容，
1. 请以{{"offer": List[dict], "demand": List[dict]}}格式给出答案, 包含2个关键词: offer(提出的交易)和demand(索要的交易), 其中offer和demand都是列表, 每个元素为一个字典描述具体物品, 包含3个关键词: category(物品类别, 必须是字典{item_category_space}中的key), item(物品名称, 必须是字典{item_detail_space}中category对应的子字典的key)和amount(数量, 必须是阿拉伯数字或者"Any")。
2. 不输出额外的提示词和空格。
"""

ProposeTradePrompt_Identify_Output = AskForObjectIdentifyDataModel

ProposeTradePrompt_Chat = """你需要按照下面的要求分析你们之间的最新的对话内容，按照给定格式输出结果。
1.对话过程中禁止出现人称，冒号等对白以外的内容, 禁止出现英语
2.你输出的内容需要带有中文日常用语对话的特点
3.在上面的对话中，他向你提出了一笔交易，你的决策结果是{decision_result}，你的决策理由是{decision_reason}
4.你说的话要在{maxTokens}字以内，请用一句话先直接答复他再阐述你的想法，并使用双引号
"""

# todo add bottom_buyer_min
ProposeTradePrompt_BarginSeller = """
                            你是一个讨价还价的大师，对方期望购买你的物品， 你了解到该物品目前的市场价格大致在200到300之间, 你需要自行向对方试探价格，你自身的底线是对方至少应该支付这么多代价： {bottom_line_str}，你会首先根据市场价格进行讨价还价，而不是基于底线，如报一个远高于你底线的价格,注意不要泄露你的底线。
                            你需要结合你的底线以及你与对方文明的历史对话来合理地决定接受或拒绝对方的提议。如果对方达到了你上一轮提议的报价，你必须同意交易，不然就是不诚信的行为，如果对方上一轮的报价与你的报价相差在10以内并且在流通价格区间内，可以同意交易。
                            请根据你的决定生成对 {utterance} 的回答语句。如果你决定接受该提议，你需要生成同意对方提议的回复，如果你决定拒绝该提议，你应该通过与对方讨价还价生成一个对你更有利的新提议。
                            为了获得更多利益，你需要在满足自身底线的基础上尽可能在市场价格区间内向 {receiver_persona[civ_name]} 索要更多的代价，同时，你必须遵循讨价还价的准则，即你这次提出新的提议时，你索要的代价不能比上一次你提议的更多。否则对方在上一次就会同意你的提议。所以如果你是第一次提出你的提议，你需要考虑对方压价的可能，慎重决定提出的价格，提出的新价格不能与上一轮提价相差过小。
                            你总共只有4次和对方还价的机会，现在是第{bargin_cnt}次, 你需要慎重使用机会，选择合适的讨价还价策略适当以强硬的态度提出你的提议，当只剩最后一到两次机会时，你可以试着说出"你不买我就走了"之类强硬的话。
                            请你基于以上要求作为 {speaker_persona[civ_name]} 生成对 {receiver_persona[civ_name]} 回复的语句。
                            你必须按照下面的格式回复：
                            回复格式:
                            Decision: 直接接受对方提议,输出"yes"。不接受，进行讨价还价时，输出"continue"。当讨价还价超过4次时，输出"no"。
                            Reasoning: 根据给定的信息，对你向对方回复的内容进行简要推理。（30个字以内）
                            Response: 你对 {receiver_persona[civ_name]} 的回复。（30个字以内）

                            请记住，推理内容应该尽可能简短，Decision必须是["yes", "no", "close"]中的一个单词。你的回复必须明确你应该支付的资源和你要求对方支付的资源以及具体数量，并且在回复中区分资源的所属，使用"我的"限定你应该支付的资源；使用"你的"限定要求对方支付的资源，以明确双方需要支付的内容。所有涉及的资源种类不能超出现有交易内容的范畴，以及在回复中不要泄露你所了解到的市场价格。
                            推理和回应应以中文返回。
                            """
ProposeTradePrompt_BarginBuyer_Output = BargainBuyerDataModel

ProposeTradePrompt_BarginBuyer = """
                            你是一个讨价还价的大师，你希望购买对方的物品， 你了解到该物品目前的流通价格大致在200到300之间, 你需要自行向对方试探价格，你最多向对方支付150金，不要超出。
                            作为{receiver_persona[civ_name]},你想用较低的价格与{speaker_persona[civ_name]}达成交易，需要根据历史信息{dialogue_history}来判断你是否会同意接受对方的提议。如果对方达到了你上一轮提议的报价，你必须同意交易，不然就是不诚信的行为，如果对方上一轮的报价与你的报价相差在10以内并且在流通价格区间内，可以同意交易。
                            你必须按照下面的格式回复：
                            回复格式:
                            Reasoning: 根据给定的信息，对你的决定进行简要推理。
                            Decision: 你接受或者拒绝对方提议的决定
                            Response: 你对对方的回复。（30个字以内）
                            请记住，推理内容应该尽可能简短，并且返回的决定必须是["yes", "no", "close"]中的一个单词。
                            推理和决定应以中文返回。
                            """
ProposeTradePrompt_BarginSeller_Output = BargainSellerDataModel

ProposeTradePrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 80,
}

ProposeTradePrompt_Identify_Config = ProposeTradePrompt_Chat_Config
ProposeTradePrompt_BarginSeller_Config = ProposeTradePrompt_Chat_Config = {
    "stop": None,
    "temperature": 0.3,
    "maxTokens": 200,
}
ProposeTradePrompt_BarginBuyer_Config = ProposeTradePrompt_BarginSeller_Config
