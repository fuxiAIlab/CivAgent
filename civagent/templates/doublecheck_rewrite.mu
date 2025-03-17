# DoublecheckRewrite

**{{speaker_persona.civ_name}}** has made a request to you, and you think the other party's possible intention is {{intention}}.

## Output

You need to initiate an inquiry with the other party to reconfirm this request: {{response}}.

Remembering to adjust your tone and attitude based on your relationship and past conversations, ensuring it does not exceed 20 tokens.

Regarding your responses:
  - You **only** generate responses in JSON format.
  - The format for this JSON response is:
    ```json
    {
      "reply": REPLY,
    }
    ```
    