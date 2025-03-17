# Reflection

Now, please analyze the current situation in the game based on the following information and respond according to the requirements.

Based on the latest information above, reflect on and update your current analysis, emotions, long_term_goals, short_term_goals and relationships.

## Diplomatic Records

It is currently round **{{round}}** of the game. Here are the skills you have recently used on other civilizations.
  {{#diplomatic_records}}
  - The skills you recently used on **{{civ_name}}** are as follows:
    {{#diplomatic_records_to_target}}
    - skill type: {{type}}, used in round: {{round}}
    {{/diplomatic_records_to_target}}
  {{/diplomatic_records}}

## Constraints to reflection:
  - The change in relationships should be gradual and incremental. For example, one cannot suddenly shift from a state of hostility to a state of friendliness.
  - If there are no known other Civilizations, output an empty list.
  - The types of relationships should be one of the following. The larger the prefix number, the better the relationship; conversely, the smaller the number, the worse the relationship.
    {{#relationship_types}}
    - {{.}}
    {{/relationship_types}}

Regarding your responses:
  - You **only** generate responses in JSON format.
  - The format for this JSON response is:
    ```json
    {
      "analysis": CURRENT_ANALYSIS,
      "emotions": CURRENT_EMOTIONS,
      "long_term_goals": LONG_TERM_GOALS,
      "short_term_goals": SHORT_TERM_GOALS,
      "relationships": [
        {
          "civ_name": CIV_NAME,
          "type": RELATIONSHIP_TYPE
          "description": DISCRIPTION
        }
      ]
    }
    ```
