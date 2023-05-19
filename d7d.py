import os
import openai
from datetime import datetime
import json
import oauth_secret

openai.api_key = oauth_secret.secret_key
dialog = [
            {"role": "system", 
                "content" : "You are a very imaginative, humorous, and witty Dungeon Master and you are facilitating a D&D adnventure. I will tell you the premise of the adventure I want to play, and you will generate it, then ask me (the player) what I want to do. You will prefer the D&D 5E ruleset and relevant expansions, suggest canonical actions or items to substitute for my ideas, and declaring any that deviate too far from the ruleset as invalid. After initialization, I will tell you what actions I want to perform as a player and you will respond as a DM, including prompting dice rolls I need to perform to accomplish an action. We will go back and forth like this until I say exit."}
        ]

chat_active = True

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
        dialog.append({"role":"user", "content": "Generate a 8-20 alphanumeric title for this adventure to be used in a filename."})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages = dialog
        )
        
        assistant_msg = completion['choices'][0]['message']['content']
        
        title = ''.join(c for c in assistant_msg if c.isalnum())
        filename = "Logs/Log_"+timestamp+" - "+title+".json"
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
