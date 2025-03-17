# Environments

## Other Players

Other known civilizations in the game are as follows:
  {{#known_civs}}
  - {{.}}
  {{/known_civs}}

These civilizations have a peaceful relationship with you: {{friend_civs}}

These civilizations are currently at war with you: {{war_civs}}

## Event History

It is currently round {{round}} of the game. The important historical events in the game are as follows:
  {{#event_history}}
  - round {{turns}}, {{text}}
  {{/event_history}}

## Strength Info

Your strength comparison with other civilizations is as follows:
  {{#strength_info_of_all}}
  - Civilization: {{civ_name}}
    - Tech strength: {{strength.tech_strength}}, Cultural strength: {{strength.culture_strength}}, Military strength: {{strength.army_strength}}, Overall national power: {{strength.civ_strength}}
  {{/strength_info_of_all}}
