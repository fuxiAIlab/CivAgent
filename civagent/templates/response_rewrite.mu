# Response Rewrite

**{{speaker_persona.civ_name}}** has made a request regarding **{{skill}}** to you.

## Decision

Your decision result: {{decision_result}}.

Your decision reason: {{decision_reason}}.

## Output

Please respond by combining your decision_result and decision_reason:
  - Remember to adjust your tone and attitude based on your relationship and past conversations.
  - During the conversation, please take on the roles and use the first and second person for the dialogue.
  - Please note that this is the final response, and do not extend into a new dialogue.
  - Ensure your response does not exceed 50 tokens.

Regarding your responses:
  - You **only** generate responses in JSON format.
  - The format for this JSON response is:
    ```json
    {
      "reply": REPLY,
    }
    ```
