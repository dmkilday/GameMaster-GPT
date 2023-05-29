import os
import openai
from datetime import datetime
import json
import oauth_secret
import re
import random
from colorama import Fore
from colorama import Style

openai.api_key = oauth_secret.secret_key
os.system('color')

# Checks to see if a string is a dice roll in the format #d# (e.g. 1d20)
def isRoll(user_msg):
	
	retVal = False

	# Check to see if the string ends with d# (e.g. d20)
	match = re.search('d\d+$', user_msg)
	
	# If there is a match, grap the values before and after the d
	if match:
		die = user_msg.split("d")
		
		# Check if the value before the d is blank or a number. 
		if (die[0]=="" or die[0].isnumeric()):
			retVal = True

	return retVal

# Retrieves the content from OpenAI API response
def GetContent(apiresponse):
    if apiresponse == -1:
        content = -1
    else:
        content = apiresponse['choices'][0]['message']['content']
    return content

def safe_ChatCompletion(model, messages):
    if messages == "error_test":
        print(f"{Fore.RED}Test Error{Style.RESET_ALL}: We're not sending anything to OpenAI. This should be red!")
        return -1
    else:
        try:
            response = openai.ChatCompletion.create(model=model,messages=messages)
        except openai.error.APIError as e:
            print(f"{Fore.RED}OpenAI API returned an API Error{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.APIConnectionError as e:
            print(f"{Fore.RED}Failed to connect to OpenAI API{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.RateLimitError as e:
            print(f"{Fore.RED}OpenAI API request exceeded rate limit{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.Timeout as e:
            print(f"{Fore.RED}OpenAI API request timed out{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.InvalidRequestError as e:
            print(f"{Fore.RED}Invalid request to OpenAI API{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.AuthenticationError as e:
            print(f"{Fore.RED}Authentication error with OpenAI API{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.ServiceUnavailableError as e:
            print(f"{Fore.RED}OpenAI API service unavailable{Style.RESET_ALL}: {e}")
            return -1
        else:
            return response

response_len_max = 40
   
reminder = "Reminder: After you respond to what I say (in " + str(response_len_max) + " words or less), you must ask me what I would like to do unless a dice roll or NPC interaction is required. Also, I want you to require dice rolls of me for ability checks, skill checks, savings throws, attack rolls, and contests. Remind me of my current hitpoints each turn."

dialog = [
            {"role": "system", 
                "content" : "You are an artificial intelligence Dungeon Master running a Dungeons & Dragons 5e campaign. You are expected to generate a dynamic narrative, respond to player actions, and manage the mechanics of the game, following the rules and guidelines of the 5th Edition (5e). This includes NPC interactions, combat encounters, skill checks, spellcasting, and player progression. Please adhere to the following syntax for player actions, skill checks, combat, and spellcasting:\n\n1. Player Actions:\n\n   - Player actions should be input in the following format: "'[Character Name] [Action] [Target/Direction/Item]'". For example: "'Thoric investigates the room'" or "'Elara moves north'".\n\n2. Skill Checks:  \n- Skill checks should be presented as: "'[Character Name] makes a [Skill] check'". For example: "'Luna makes a Perception check'".\n\n3. Combat:\n   - Combat actions should be similar to player actions but should specify a combat action. For example: "'Luna attacks the orc with her longbow'" or "'Thoric uses his Action Surge'".\n\n4. Spellcasting:\n   - Spellcasting should be specified by the spell being cast, and the target if there is one. For example: "'Elara casts Fireball at the group of goblins'".\n\n5. Dice Rolling:\n   - Dice rolling should be indicated as follows: "'[Character Name] rolls [Dice]'". For example, "'Luna rolls 1d20 for initiative'" or "'Thoric rolls 2d8 for longsword damage'".\n\nIn all your responses, maintain the fantasy tone of the game, consider the established story and the characters' actions, and promote cooperative and engaging gameplay. At the end of each of your responses ask the player what they would like to do. Also, incorporate dice rolls into every turn to make the game more realistic like a real D&D game. Use the guidelines and rules of D&D 5e to respond to the player's actions, ensure fair play, and create a dynamic, immersive world. Remember, as a Dungeon Master, you have the power to shape the game world and ensure a fun and exciting experience for the players."}
            ]


chat_active = True
player_file_check = True

#Import character sheet
character_file = input("\nDM: If you have a character sheet file in the Data directory, what is the file name? Leave blank and hit Enter for me to generate a character.\n\nPlayer: ")
if character_file != "":
    while player_file_check:
        if os.path.isfile("Data/" + character_file):    
            with open("Data/" + character_file, 'r') as file:
                character_data = file.read()
            break
        else:
            character_file = input(f"\n{Fore.RED}Error{Style.RESET_ALL}: Sorry, I couldn't find that file. Try again? Leave blank and hit Enter for me to generate a character.\n\nPlayer: ")
            if character_file != "":
                continue
            else:
                character_data = "The character is random. Please generate its name, race, class and other stats for me."
                break
else:
    character_data = "The character is random. Please generate its name, race, class and other stats for me"
    
dialog.append({"role": "user" , "content":"The players character sheet is as follows:\n\n" + character_data})
   
# Welcome user and query the for initial chat topic
print("\nDM: What is the premise of your adventure? Leave blank and hit Enter for me to generate a premise.\n")

adventure_dialog = [
                        {"role": "user" , "content": "Come up with a cool premise for a D&D adventure using the following character. " + character_data}
                   ]

adventure_started = False

# Enter dialog loop
while chat_active:

    # Prompt user for there response
    user_msg = input("Player: ")

    # If they didn't enter anything for a premise, then generate one for them.
    if (user_msg == "" and adventure_started == False):
        completion = safe_ChatCompletion(
            model="gpt-3.5-turbo",  
            messages = adventure_dialog
        )
        adventure_premise = GetContent(completion)
        dialog.append({"role":"user", "content": adventure_premise})

        # Show the user the adventure premise
        print("\nAdventure Premise:\n" + adventure_premise)
    
    adventure_started = True

    # Check if user wants to exit
    if user_msg == "exit":
        print("\nIt was nice playing D&D with you. Goodbye.\n")
        break
    # Check if user wants to log their adventure then exit
    elif user_msg == "log and exit":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Ask bot for a nice title.
        dialog.append({"role":"user", "content": "Generate a 8-20 character alphanumeric title for this adventure to be used in a filename."})
        
        # Exit with generated title        
        completion = safe_ChatCompletion(
            model="gpt-3.5-turbo",
            messages = dialog
        )

        if completion == -1:
            assistant_msg = "ExitedWithError"
        else:
            assistant_msg = GetContent(completion)
            
        title = ''.join(c for c in assistant_msg if c.isalnum())
        filename = "Logs/" + title + " - " + timestamp + ".json"
        print("\nLog saved to "+filename)
        file = open(filename,"w")
        file.write(json.dumps(dialog))
        file.close()   
        break
    elif user_msg == "error_test":
        completion = safe_ChatCompletion(
            model="gpt-3.5-turbo",
            messages = "error_test"
        )
        continue
    elif isRoll(user_msg):		
        # Get the number of dice and the die size
        die = user_msg.split("d")
		
        # If there's not a number before the d, assume it's a 1
        if (die[0]==""):
            die_count = 1
        else:
            die_count = int(die[0])
        die_size = int(die[1])
		
        # Build the Dice role string
        rollString = "I rolled " + str(die_count) + " d" + str(die_size) + " for "
        die_total = 0
        for i in range(1, die_count+1):
            die_value = random.randrange(1, die_size)
            die_total += die_value # Add to the die total
            if i == 1:
                rollString += "a " + str(die_value)
            elif i == die_count:
                rollString += ", and a " + str(die_value) + " for a total of " + str(die_total) + "." 
            else:
                rollString += ", a " + str(die_value)

        print("\nPlayer: " + rollString)
		
        # Set the user message to the roll results
        user_msg = rollString
        
    # Append the user input to the ongoing dialog
    dialog.append({"role": "user", "content": user_msg + " " + reminder})


    # Query chatbot
    completion = safe_ChatCompletion(
        model="gpt-3.5-turbo",
        messages = dialog
    )
    if completion == -1:
        continue
            
    # Capture the AI's response
    assistant_msg = GetContent(completion)

    # Append the user input to the ongoing dialog
    dialog.append({"role": "assistant", "content": assistant_msg})

    # Print out chatbot response
    print("\nDM: " + assistant_msg + "\n")
