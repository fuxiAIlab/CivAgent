# Development

Please consider your current objectives and your relationships with other civilizations to determine which technologies and resources you should prioritize for development.

If relations are tense, focus on strengthening military capabilities; if they are stable, you can prioritize enhancing non-military capabilities.

Remember, you can only choose one area to develop: either Technology or Production.

## Technology

You have access to the following types of technologies:
  {{#available_technologies}}
  - {{.}}
  {{/available_technologies}}

## Production

You have access to the following types of productions for each city:
  {{#productions}}
  - City: {{city}}
    {{#available_productions}}
    - {{.}}
    {{/available_productions}}
  {{/productions}}

Regarding your responses:
  - You **only** generate responses in JSON format.
  - The format for this JSON response is: 
    ```json
    {
      "technology_choose": TECHNOLOGY,
      "production_choose":{
        CITY: PRODUCTION
      }
    }
    ``` 