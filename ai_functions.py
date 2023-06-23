#### This file contains the functions which allows OpenAI API to control program flow
functions=[
    {
        "name": "roll_dice",
        "description": "Rolls dice. Only used when a player or DM wants to roll dice. Includes calls to in XdY format where Y is how many sides the die has and X is how many times it's rolled.",
        "parameters": {
            "type": "object",
            "properties": {
                "side_count": {
                    "type": "integer",
                    "enum": [4, 6, 8, 10, 12, 20, 100],
                },
                "roll_count": {
                    "type": "integer",
                    "descripton": "The number of times the dice should be rolled."
                },
            },
            "required": ["side_count", "roll_count"],
        }
    },
    {
    "name": "attack",
      "description": "Initiates an attack on an enemy.",
      "parameters": {
        "type": "object",
        "properties": {
          "attacker_statistics": {
            "type": "object",
            "properties": {
              "attack_power": { "type": "integer" },
              "accuracy": { "type": "integer" },
              "critical_chance": { "type": "integer" }
            },
            "required": ["attack_power", "accuracy", "critical_chance"]
          },
          "target_enemy_statistics": {
            "type": "object",
            "properties": {
              "defense": { "type": "integer" },
              "evasion": { "type": "integer" }
            },
            "required": ["defense", "evasion"]
          }
        },
        "required": ["attacker_statistics", "target_enemy_statistics"]
        }
    },]
