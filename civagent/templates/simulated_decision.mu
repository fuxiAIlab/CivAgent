# Simulated Decision

This is the change in strength after using the {{skill}} skill to over {{turns}} turns in the simulator:

  {{civ_strength_old}} -> {{civ_strength_new}}

Please consider whether to continue using this skill based on the above current analysis, emotions, long-term goals, short-term goals, relationships, and the results from the simulator.

## Output

The following explains your response based on the identified content.
  - DESICION_RESULT: The result for your choice (only 'yes' or 'no').
  - DESICION_REASON: The reason for your choice, ensuring it does not exceed 50 tokens.

Regarding your responses:
  - You **only** generate responses in JSON format.
  - The format for this JSON response is:
    ```json
    {
      "decision_result": DESICION_RESULT,
      "decision_reason": DESICION_REASON,
    }
    ```
