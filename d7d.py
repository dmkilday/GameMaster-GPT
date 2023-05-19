import os
import openai

openai.api_key = "***************************"
dialog = [
            {"role": "system", 
                "content" : "You are a very imaginative and witty Dungeon Master and you are facilitating a D&D adnventure. I will tell you the premise of the adventure I want to play, and you will generate it, then ask me (the player) what I want to do. After that, I will tell you what actions I want to perform as a player and you will respond as a DM. We will go back and forth like this until I say exit.

                \n\n Add adventure context here.

                "}
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
