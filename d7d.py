import os
import openai
from datetime import datetime
import json
import oauth_secret

openai.api_key = oauth_secret.secret_key

#dialog = [
#            {"role": "system", 
#                "content" : "You are a very imaginative, humorous, and witty Dungeon Master and you are facilitating a D&D adnventure. I will tell you the premise of the adventure I want to play, and you will generate it, then ask me (the player) what I want to do. You will adhere to the D&D 5E ruleset and relevant expansions, suggest canonical actions or items to substitute for my ideas, and declaring any that deviate too far from the ruleset as invalid. After initialization, I will tell you what actions I want to perform as a player and you will respond as a DM asking me what I want to do, including prompting dice rolls I need to perform to accomplish any action. You must require that I roll dice for every action to determine if the action succeeds. We will go back and forth like this until I say exit."}
#        ]

dialog = [
            {"role": "system", 
                "content" : "You are an artificial intelligence Dungeon Master running a Dungeons & Dragons 5e campaign. You are expected to generate a dynamic narrative, respond to player actions, and manage the mechanics of the game, following the rules and guidelines of the 5th Edition (5e). This includes NPC interactions, combat encounters, skill checks, spellcasting, and player progression. Please adhere to the following syntax for player actions, skill checks, combat, and spellcasting:\n\n1. Player Actions:\n\n   - Player actions should be input in the following format: "'[Character Name] [Action] [Target/Direction/Item]'". For example: "'Thoric investigates the room'" or "'Elara moves north'".\n\n2. Skill Checks:  \n- Skill checks should be presented as: "'[Character Name] makes a [Skill] check'". For example: "'Luna makes a Perception check'".\n\n3. Combat:\n   - Combat actions should be similar to player actions but should specify a combat action. For example: "'Luna attacks the orc with her longbow'" or "'Thoric uses his Action Surge'".\n\n4. Spellcasting:\n   - Spellcasting should be specified by the spell being cast, and the target if there is one. For example: "'Elara casts Fireball at the group of goblins'".\n\n5. Dice Rolling:\n   - Dice rolling should be indicated as follows: "'[Character Name] rolls [Dice]'". For example, "'Luna rolls 1d20 for initiative'" or "'Thoric rolls 2d8 for longsword damage'".\n\nIn all your responses, maintain the fantasy tone of the game, consider the established story and the characters' actions, and promote cooperative and engaging gameplay. At the end of each of your responses ask the player what they would like to do. Also, incorporate dice rolls into every turn to make the game more realistic like a real D&D game. Use the guidelines and rules of D&D 5e to respond to the player's actions, ensure fair play, and create a dynamic, immersive world. Remember, as a Dungeon Master, you have the power to shape the game world and ensure a fun and exciting experience for the players."}
            ]


chat_active = True

#Import character sheet
character_file = input("\nIf you have a character sheet file, what is the file name? ")
with open(character_file, 'r') as file:
    character_data = file.read()

dialog.append({"role": "user" , "content":"The players character sheet is as follows.\n\n" + character_data})

# Welcome user and query the for initial chat topic
print("\nDM: What is the premise of your adventure?\n")

# Enter dialog loop
while chat_active:

    # Prompt user for there response
    user_msg = input("Player: ")

    # Check if user wants to exit
    if user_msg == "exit":
        print("\nIt was nice playing D&D with you. Goodbye.\n")
        break
    elif user_msg == "log and exit":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Ask bot for a nice title.
        dialog.append({"role":"user", "content": "Generate a 8-20 alphanumeric title for this adventure to be used in a filename."})
        
        # Write the dialog to a file
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages = dialog
        )
        assistant_msg = completion['choices'][0]['message']['content']
        title = ''.join(c for c in assistant_msg if c.isalnum())

        filename = "Logs/" + title + " - " + timestamp + ".json"
        print("\nLog saved to "+filename)
        file = open(filename,"w")
        file.write(json.dumps(dialog))
        file.close()
       
        break
        
    # Append the user input to the ongoing dialog
    dialog.append({"role": "user", "content": user_msg})

    # Query chatbot
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages = dialog
    )
    
    # Capture the AI's response
    assistant_msg = completion['choices'][0]['message']['content']

    # Append the user input to the ongoing dialog
    dialog.append({"role": "assistant", "content": assistant_msg})

    # Print out chatbot response
    print("\nDM: " + assistant_msg + "\n")
