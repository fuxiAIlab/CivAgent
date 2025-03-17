# Identify

Please extract the specific entities and their quantities involved in the transaction details. 

## Dialogue History

The dialogue history between you and {{speaker_persona.civ_name}} is as follows:
  {{#dialogue_history}}
  - {{fromCiv}}: "{{notify}}"
  {{/dialogue_history}}

## Identified Content

{{speaker_persona.civ_name}}: {{utterance}}

## Luxury Space

You have access to the following types of Luxury Space:
  - Ivory
  - Citrus
  - Furs
  - Silk
  - Dyes
  - Copper
  - Salt
  - Silver
  - Stone
  - Gems
  - Truffles
  - Spices
  - Marble
  - Sugar
  - Whales
  - Porcelain
  - Crab
  - Pearls
  - Cotton
  - Jewelry
  - Incense
  - Wine

## Resource Space

You have access to the following types of Resource Space:
  - Iron
  - Horse
  - Oil
  - Uranium
  - Coal
  - Aluminum

## Output

The following explains your response based on the identified content and the dialogue history.
  - OFFER: A List of items and their quantities provided by the other party.
  - DEMAND: A List of Items and their quantities requested by us.
  - ITEM: One item in the Item Resource Space, Luxury Space, or Gold.
  - AMOUNT: The quantity of ITEM.
  - If the amount is not mentioned in the Identified Content, it is considered **Any**.

Regarding your responses:
  - You **only** generate responses in JSON format.
  - The format for this JSON response is:
    ```json
    {
      "offer": List[dict],
      "demand": List[dict],
    }
    ```
  - The format of each dict in the List. 
    ```json
    {
      "item": ITEM,
      "amount": AMOUNT,
    }
    ```
