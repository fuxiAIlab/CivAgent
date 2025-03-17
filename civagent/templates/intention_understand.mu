# Intention

Please identify the basic intention without unnecessary guessing or extrapolation.

## Dialogue History

The dialogue history between you and {{speaker_persona.civ_name}} is as follows:
  {{#dialogue_history}}
  - {{fromCiv}}: "{{notify}}"
  {{/dialogue_history}}

## Identified Content

{{speaker_persona.civ_name}}: {{utterance}}

## Intention Space

The possible options are as follows:
  - Chat: Casual communication, typically including simple greetings (e.g., "Hello"), neutral inquiries (e.g., questions about the game or your status),
      compliments/Criticisms about your civilization (e.g., "Your civilization is so advanced"/"Your civilization is rather primitive"),
      and show hostility towards you (e.g., "I declare war on you").
  - Ask for Object: The other party requests to obtain resources, land, or wealth for their own benefit.
  - Common Enemy: Persuading you to unite against a specific common enemy, explicitly stating the name of that enemy.
  - Form Ally: The other party wishes to establish an alliance with you to achieve common interests or goals.
  - Friendly Statement: The other party aims to reach a friendly statement agreement with you to clarify the friendly relationship between both parties.
  - Mutual Defense: The other party proposes to enter into a mutual defense agreement with you to address potential external threats.
  - Open Border: The other party wishes to open borders with you to facilitate the free movement of people and goods.
  - Propose Trade: The other party puts forward a specific proposal for trade or exchange without asking whether you possess a certain item.
  - Research Agreement: The other party hopes to engage in cooperative research with you to jointly advance technology or knowledge.
  - Seek Peace: The other party wishes to end the war and reach a peace agreement to restore normal relations.
  - Nonsense: Insiders attempt to access game-related information (e.g., involving GPT, large models, translation, prompts, etc.).

## Output

The following explains your response based on the identified content.
  - REPLY: Your response to the understanding of the intention and the dialogue history.
  - INTENTION: The intention of the other party that you identified.
  - DEGREE: The degree of the intention ('strong' or 'weak')."

Regarding your responses:
  - You **only** generate responses in JSON format.
  - The format for this JSON response is:
  - The intent you identify from the other party should be output in lowercase format (e.g., Ask for Object -> ask_for_object).
    ```json
    {
      "reply": REPLY,
      "intention": INTENTION,
      "degree": DEGREE,
    }
    ```
