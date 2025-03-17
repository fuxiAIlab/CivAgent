# Doublecheck

## Dialogue History

The dialogue history between you and {{speaker_persona.civ_name}} is as follows:
  {{#dialogue_history}}
  - {{fromCiv}}: "{{notify}}"
  {{/dialogue_history}}

Please correctly identify 'you' and 'I' in the conversation and don't confuse the roles. Remember, you are **{{civ_name}}**.

## Output

Please determine whether {{utterance}} is affirmative or negative based on your previous conversations.
  - If it is affirmative, return "yes".
  - If it is negative, return "no". If there is a modification to the proposal based on the negation, such as bargaining, return "continue".
  - If it is off-topic, meaning the response content is unrelated to the question, return "none".

Regarding your responses:
  - You **only** generate responses in JSON format.
  - The format for this JSON response is:
    ```json
    {
      "doublecheck": DOUBLECHECK,
    }
    ```
