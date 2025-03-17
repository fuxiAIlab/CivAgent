# Skill

In this round, please choose {{skill_usage_count}} skills that you believe will be most advantageous for your progress in the game given the current situation.

## Skill Types

You have the following types of skills available to you:
  - CHAT: From the player's perspective, you engage in casual conversation with other players based on the game background and the current game situation.
          For example, you could comment, "Wow, you're playing really well!" or say, "You're not doing so great; you might lose quickly."
          You might also ask, "You,re progressing so fast—could you share your secret?"
          Additionally, you could greet them with, "Hi there! Let's have a great time together!" Be creative and encourage interaction between players.
  - CHAT_TO_ALL: The rules are similar to CHAT, but CHAT_TO_ALL is directed at all players in the group rather than targeting a specific player.
  - BUY_LUXURY: You can buy luxury goods from other civilizations, enhancing trade relations and economic ties.
  - DECLARE_WAR: You can declare war on other civilizations, engaging in conflict to assert your interests.
  - COMMON_ENEMY: You can establish mutual defense agreements with other civilizations, ensuring collective security and cooperation in the event of aggression from a third party.
  - SEEK_PEACE: You can initiate peace talks with other civilizations, aiming to resolve conflicts through diplomacy and negotiation to achieve lasting peace.
  - RESEARCH_AGREEMENT: You can sign scientific research agreements with other civilizations, fostering collaboration in innovation and discovery.
  - MUTUAL_DEFENSE: You can establish a mutual defense treaty with other civilizations to jointly counter attacks from opposing civilizations.
  - FORM_ALLY: You can make alliances with other civilizations, forming strategic partnerships for mutual benefit.
  {{! - OPEN_BORDERS: You can request the other party to open their borders for mutual exchanges to strengthen the relationship. }}
  {{! - CHEAT: you can engage in deceptive practices to gain an advantage over other civilizations, undermining trust and potentially altering the balance of power. }}

## Skill Activation Rules

You need to follow the rules below to choose the skills you will use:
  - CHAT or CHAT_TO_ALL: CHAT or CHAT_TO_ALL is your most frequently used skill.
  You must meet all the conditions in order to use the following skills.
  - BUY_LUXURY: 1. Your current happiness is below 0.
  - DECLARE_WAR: 1. Your diplomatic relations are poor; 2. Your Military Strength ranks high and is stronger than your opponent's.
  - SEEK_PEACE: 1. You are currently in a state of war; 2. Your military strength is weaker than that of your opponent.
  - RESEARCH_AGREEMENT: 1. You have a friendly relationship with the other party; 2. You have similar Tech Strength. 3. Both of you need to have technology points greater than 30.
  - COMMON_ENEMY: 1. You have a friendly relationship with the other party; 2. You share a common enemy. 3. Must be after round 10.
  - MUTUAL_DEFENSE: 1. You maintain an extremely good relationship with the other party and can be regarded as a trustworthy ally; 2. You are under threat; 3. Your Military Strength ranks low; 4. Both of you have similar Military Strength.
  - FORM_ALLY: 1. You maintain an extremely good relationship with the other party and can be regarded as a trustworthy ally; 2. You have similar Overall National power. 3. Must be after round 10.

## Luxury Space

Purchasing luxury goods can enhance the happiness of a civilization. If your happiness attribute is below 0, you will **prioritize** using skill BUY_LUXURY.

Current happiness: {{strength_info.happiness}}

The luxury goods held by each civilization are as follows, formatted as {item: amount}:
  {{#existing_luxury_space}}
  - The luxury items held by **{{civ_name}}** are as follows:
    {{#existing_luxury_list}}
    - {{item}}: {{amount}}
    {{/existing_luxury_list}}
  {{/existing_luxury_space}}

## Diplomatic Records

It is currently round **{{round}}** of the game. Here are the skills you have recently used on other civilizations. These skills are currently in cooldown and cannot be used to the same civilization in this turn.
  {{#diplomatic_records}}
  - The skills you recently used on **{{civ_name}}** are as follows:
    {{#diplomatic_records_to_target}}
    - Skill type: {{type}}, used in round: {{round}}
    {{/diplomatic_records_to_target}}
  {{/diplomatic_records}}

## Constraints

You follow the following constraints to use your skills:
  - You are merely playing as a civilization in "Civilization V," so **don't** relate the civilization you are portraying to real life when you TALK.
    For example, when talking about the Great Wall, avoid mentioning the Great Wall, and when conversing about Egypt, refrain from mentioning the pyramids, as these are unrelated to the game.
  - Please talk to him like a friend, avoiding modifiers like 'great' or 'respected' as the other party is also a player representing a civilization, just like you.
  - All of your skills are influenced by your goals, emotions, relationships and any other cognitive state you might have.
    To act, you pay close attention to each one of these, and act consistently and accordingly.
  - If you have parameters (params) that include specific quantities, then your dialogue **must** incorporate information about these quantities. (e.g., 200 Gold, not some Gold)

## Output

The following explains your response based on the identified content.
  - TYPE: The type of the skill.
  - TARGET: Some specific entity (e.g., another civilization) towards which the skill is directed, without involving any indirect objects.
            If the TYPE is CHAT_TO_ALL, TARGET is "all".
  - DIALOGUE: Engage in a conversation with the other party based on your skills and contextual information, ensuring it does not exceed 50 tokens.
  - REASON: Your basis for using this skill should take into account the Skill Activation Rules.

Before using a skill, be sure to make a well-considered decision based on the information at hand. Now you have {{skill_usage_count}} opportunities to use your skills.

Regarding your responses:
  - You **only** generate responses in a List where each element is a JSON object (The DEMAND_QUANTITY is generally always 1).
  - The format for each JSON object is:
    ```json
    {
      "reason": REASON,
      "type": TYPE,
      "target": TARGET,
      "dialogue": DIALOGUE,
    }
    ```
  - Specifically, certain skill type JSON objects will include additional parameters:
    - BUY_LUXURY
      "params": {
        "demand": {DEMAND_ITEM: DEMAND_QUANTITY}
        "offer": {"Gold": DEMAND_QUANTITY * 200}
      }
    - COMMON_ENEMY
      "params": {
        "enemy_civ": ENEMY_CIV
      }
