# Must come first!! We can delete this and the file once we're confident nobody is using oauth_secret.py anymore.
import init_env

# Local libs
import messages
import utils
import chat
import ai_functions

# Built-in libs
import os
import random
from datetime import datetime
import json
import glob
from dotenv import load_dotenv

# PyPI libs
import re
import openai
from colorama import Fore
from colorama import Style

# Load environment variables
load_dotenv()
FAST_LLM_MODEL = os.getenv('FAST_LLM_MODEL')
SMART_LLM_MODEL = os.getenv('SMART_LLM_MODEL')
DETERMINISTIC_TEMPURATURE = os.getenv('DETERMINISTIC_TEMPURATURE')
CREATIVE_TEMPERATURE = os.getenv('CREATIVE_TEMPERATURE')


os.system('color')

# Set up main variables
player_file_check = True
skip_menu = False
prev_session = False
log_dir = "log"
data_dir = "data"
character_dir = "character"
log_file_name = ""
i_main = 5
    
# Initialize the in-game gialog
dialog = [{"role": "system", "content" : messages.initialize}]

# Initialize the out of character dialog
ooc_dialog = [{"role": "system", "content" : messages.initialize}]

# Requests response from GM
def invoke_gm(gm_player_dialog, user_msg, function_call, full_text_log):
  
    # Add player message to ongoing dialog and text log
    chat.append_dialog(gm_player_dialog, "user", user_msg)
    full_text_log += "Player: " + user_msg + "\n\n"

    # Call chat completion API
    completion = chat.safe_chat_completion(
        model=FAST_LLM_MODEL,
        messages=dialog,
        function_call=function_call
    )
     
    # Debug chat completion
    #print(f"\n{completion}\n")
    
    finish_reason = chat.get_finish_reason(completion)
    
    error_prefix = "Chat Complete Finish Reason"

    error_suffix = "Please try again."
    
    #    Every response will include a finish_reason. The possible values for finish_reason are:
    #
    #    stop: API returned complete message, or a message terminated by one of the stop sequences provided via the stop parameter
    #    length: Incomplete model output due to max_tokens parameter or token limit
    #    function_call: The model decided to call a function
    #    content_filter: Omitted content due to a flag from our content filters
    #    null: API response still in progress or incomplete

    # Handle responses from the Chat Completion API
    match finish_reason:
        
        case "length":
            print(f"{error_prefix}: length - Incomplete model output due to max_tokens parameter or token limit. {error_suffix}")

        case "content_filter":
            print("{error_prefix}: content_filter - Omitted content due to a flag from our content filters. {error_suffix}")
        
        case "null":
            print("{error_prefix}: null - API response still in progress or incomplete. {error_suffix}")
        
        case "stop":
            assistant_msg = chat.get_content(completion)
            if assistant_msg != -1:
                chat.append_dialog(gm_player_dialog, "assistant", assistant_msg)
                full_text_log += "GM: " + assistant_msg + "\n\n"
   
    return completion


# Rolls the dice for a player
def roll_dice(die_count, die_size):
    
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

    #print("\nPlayer: " + rollString)
    
    # Set the user message to the roll results
    return rollString


# Initiates the adventure generator
# TODO: This function is no currently working
def generate_adventure():
    with open("gen_adventure.py", 'r') as f:
        gen_adventure = f.read()
    #continue
    exec(gen_adventure)
    return True

# Initiates re-entry into a saved adventure
def start_saved_adventure():
    global dialog
    
    # Read from previous logfile and attempt to continue the adventure from where it left off.
    if os.path.exists(log_dir + "/") == False:
        os.mkdir(log_dir)
        
    res = []
    n = 0

    # Get the list of files from the log directory
    files = os.listdir(log_dir)
    #print(files)
    
    # If there are no log files, let the user know
    if not files:
        print("GM: There are no previous log files.")
        #continue
        return True
    # Otherwise, show the list of adventure log files
    else:
        outp = "\nFiles and directories in '" + log_dir + "':\n"
        for path in files:
            #if os.path.isfile(os.path.join(log_dir,path)):
                res.append(path)
                outp += "\n" + str(n) +". " + path
                n+=1
                
        print(outp)

        # Prompt the user to select an adventure  log file to load
        read_num = input("GM: Enter the number of the log you want to view or B(b) to go back.\n\nPlayer: ")
        
        # Go back to previous menu if the user wants to go back
        if read_num == "B" or read_num == "b":
            #continue
            return True

        # Otherwise load the log file
        elif utils.is_integer(read_num) and int(read_num) < len(res) and int(read_num) >= 0:
            #print("GM: Opening " + res[int(read_num)] + "...\n")
            #print(res)
            file = open(log_dir + "/" + res[int(read_num)],"r")
            print("GM: Loaded " + res[int(read_num)] + "!\n\nDo you want to play this adventure? (Y/N)\n\n")
            cont_adv = input("Player (enter 'Y' or 'N'): ")
            if cont_adv == "Y" or cont_adv == "y":
                log_file_name = res[int(read_num)]
                dialog = json.loads(file.read())
                #print(dialog)
                i_main = 1
                skip_menu = True
                prev_session = True
                #print(dialog[-1])
                if dialog[-1]['role'] == "user":
                    dialog.pop() # remove last user prompt from the list.
                    # print("... Deleted last user prompt\n") 
            #continue
            #return True
            # Start the adventure
            full_text_log = ""
            start_adventure(full_text_log)

        else:
            print("GM: That's not a real entry. You should have entered the line number of the file you want to read.")
            #continue
            return True


# Initiates a general chat with the GM
def start_chat():
    dialog = [] # blank the array. we don't want it to be a GM, but just a standard ol' chatbot..
    print("\n")
    while chat.active:
        user_msg = input("Player: ")
        if user_msg == "exit":
            break
        else:
            if not dialog:
                dialog = [
                    {"role":"system",
                        "content":user_msg
                    }
                ]
            else:
                dialog.append({"role": "user", "content": user_msg})
                
                
            completion = chat.safe_chat_completion(
                model=FAST_LLM_MODEL,
                messages = dialog
            )
            if completion == -1:
                continue
                #return True
                
            # Capture the AI's response
            assistant_msg = chat.get_content(completion)
            if assistant_msg != -1:
                # Append the user input to the ongoing dialog
                dialog.append({"role": "assistant", "content": assistant_msg})

                # Print out chatbot response
                print("\nGM: " + assistant_msg + "\n")


# Initiates an adventure for the user
def initiate_new_adventure():
    global dialog
    global ooc_dialog
    global log_file_name
    
    full_text_log = ""

    character_file = input("\nGM: If you have a character sheet file in the Data/character directory, what is the file name? Leave blank and hit Enter for me to generate a character.\n\nPlayer: ")
    character_data = ""
    
    #Import character sheet if provided by user
    if character_file != "":
        while player_file_check:
            if os.path.isfile(data_dir + "/" + character_dir + "/" + character_file):    
                with open(data_dir + "/" + character_dir + "/" + character_file, 'r') as file:
                    character_data = file.read()
                break
            else:
                utils.color_print(f"\n{Fore.RED}Error{Style.RESET_ALL}: Sorry, I couldn't find that file. Try again? Leave blank and hit Enter for me to generate a character.")
                character_file = input("\nPlayer: ")
                if character_file != "":
                    continue
                else: # Can't open character sheet so generate one
                    # Generate a character
                    character_prompt = "The character is random. Please generate its name, race, class and other stats for me."
                    character_data = chat.gen_character(dialog, character_prompt, full_text_log)
                    break
    else:
        # Generate a character
        character_prompt = "The character is random. Please generate its name, race, class and other stats for me"
        character_data = chat.gen_character(dialog, character_prompt, full_text_log)

    dialog.append({"role": "user" , "content":"The players character sheet is as follows:\n\n" + character_data})

    # Display character sheet
    print(f"\nHere is your character information:\n\n{character_data}\n")

    # Query the user for the premise of their adventure
    print("\nGM: What is the premise of your adventure? Leave blank and hit Enter for me to generate a premise.\n")

    # Prompt user for a premise
    user_msg = input("Premise: ")

    # If they didn't enter a premise, let's ask the API to generate one.
    if (user_msg == ""):

        adventure_dialog = [
                            {"role": "user", 
                             "content": "Come up with a cool premise for a RPG adventure using the following character. " + character_data}]
    
        completion = chat.safe_chat_completion(
            model=FAST_LLM_MODEL,  
            messages = adventure_dialog
        )
        adventure_premise = chat.get_content(completion)
      
        #print(f"\nPremise Response: {completion}\n")

    # Set the premise to whatever the user entered
    else:
        
        adventure_premise = user_msg

    # Show welcome message and adventure premise.
    dialog.append({"role":"user", "content": adventure_premise}) 
    utils.color_print(messages.welcome + adventure_premise)
    
    # Start the adventure
    start_adventure(full_text_log)
       
# Starts the adventure after it has been loaded
def start_adventure(full_text_log):

    global dialog
    global ooc_dialog
    global log_file_name
        
    # Enter game dialog loop
    dialog_token_limit = 2000 # This is the max we will allow the dialog to grow before summarizing

    # Initialize last_finish_reason
    last_finish_reason = "start"
    
    # Give the player the starting point of the adventure 
    print(f"\nGM: {chat.get_adventure_hook(dialog, full_text_log)}\n")

    while chat.active:

        # Prompt user for there response
        user_msg = input("Player: ")
      
        # Check if user wants to exit
        if user_msg == "exit":
            print("\nIt was nice playing with you. Goodbye.\n")
            break

        # Check if user wants to log their adventure then exit
        elif user_msg == "log and exit":
            if log_file_name == "":
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                
                # Ask bot for a nice title.
                dialog.append({"role":"user", "content": "Generate a 8-20 character alphanumeric title for this adventure to be used in a filename."})
                
                # Exit with generated title        
                completion = chat.safe_chat_completion(
                    model=FAST_LLM_MODEL,
                    messages = dialog
                )

                if completion == -1:
                    assistant_msg = "ExitedWithError"
                else:
                    assistant_msg = chat.get_content(completion)
                
                if os.path.exists(log_dir + "/") == False:
                    os.mkdir(log_dir)
                    
                title = ''.join(c for c in assistant_msg if c.isalnum())
                log_file_name = timestamp + "_" + title + ".json"
            
            print("\nGM: Saving log to "+log_file_name)
            file = open(log_dir + "/" + log_file_name,"w")
            file.write(json.dumps(dialog))
            file.close()   
            break

        # Check if the user wants to generate a dall-e image
        elif user_msg == "dall-e":
            # Use sparingly! Expensive AND the prompt length max is insanely short.
            if full_text_log == "":
                print("GM: No prompt has been built yet. Please play a bit before generating an image.\n")
            else:
                response = openai.Image.create(
                    prompt=full_text_log,
                    n=1,
                    size="512x512"
                )
                image_url = response['data'][0]['url']
                print(f"\nGM: Go to {image_url} to see what I think the current scene looks like.")
            last_finish_reason = "system_command"

        # TODO: Comment this condition (what is error test?)
        elif user_msg == "error_test":
            completion = chat.safe_chat_completion(
                model=FAST_LLM_MODEL,
                messages = "error_test"
            )
            continue

            last_finish_reason = "system_command"


        # Check if the user is talking to the GM out of character (OOC)
        elif utils.is_ooc(user_msg):
            ooc_table = re.split(r'ooc(\/clear)?\s+',user_msg)
            if ooc_table == "/clear":
                ooc_dialog = [] # clear the dialog.
            print(user_msg)
            ooc_dialog.append({"role":"user", "content":str(ooc_table[2])})
            completion = chat.safe_chat_completion(
                model=FAST_LLM_MODEL,
                messages = ooc_dialog
            )
            if completion == -1:
                continue
                
            assistant_msg = chat.get_content(completion)
            dialog.append({"role": "assistant", "content": assistant_msg})
            print("\nGM: " + assistant_msg + "\n")
            full_text_log += "GM: " + assistant_msg + "\n\n"
            continue
        
            last_finish_reason = "ooc"

        # There are no system commands, so determine what the user wants to do 
        else:

            #TODO: Summarize beginning of log as we approach context window limit
            # Identify dialog token size
            #token_size = chat.get_token_size_messages(dialog, FAST_LLM_MODEL)
            # Summarize old dialog if we've reached the limit 
            #if (token_size > dialog_token_limit):
            #    chat.shrink_dialog(dialog, token_size, 1000, FAST_LLM_MODEL) # Shrink dialog to under 1,000 tokens

            # Send message to GM
            user_message = user_msg + " " + messages.reminder
            
            # If the last call was a function call, then suppress functions
            if last_finish_reason == "function_call":
                completion = invoke_gm(dialog, user_message, "none", full_text_log)
            else:   
                completion = invoke_gm(dialog, user_message, "auto", full_text_log)
            
            assistamt_msg = ""

            # If the API response is a function call, execute the function
            if chat.is_function_call(completion):
                   
                # Get function being called and arguments
                function = chat.get_function(completion)
                args = chat.get_function_args(completion)
                
                # Handle responses from the Chat Completion API
                match function:
                    
                    case "roll_dice":
                        
                        # Get the arguments
                        die_to_roll = args['side_count']
                        times_to_roll = args['roll_count']
                        
                        # Let user know they are rolling the dice
                        print(f"\nRolling the {die_to_roll}-sided die {times_to_roll} time(s)...")
                        
                        # Roll the dice the specified number of times
                        dice_outcome = roll_dice(times_to_roll, die_to_roll)           
                        
                        # Show user what they got on their roll
                        print(f"\nPlayer: {dice_outcome}")
                        
                        # Let the GM know what the roll was
                        completion = invoke_gm(dialog, dice_outcome, "none", full_text_log)
                        
                        # Show the GM's response
                        assistant_msg = chat.get_content(completion)
                        print("\nGM: " + assistant_msg + "\n")
                  
                    #case "determine_initiative":
                        
                        # Get list of players and NPCs

                        # Roll initiative for each and put characters in order dict array with stats

                    case "attack":
                        
                        print("You are attacking...need to add handler code.")
                        
                        # Enter combat loop
                        in_combat = True
                        #while in_combat:
                            
                            # Get the attackers info
                            
                            # Get the target info

                            # Attacker roll attack dice

                            # GM evaluate target AC plus modifiers

                            # If attack roll beats target defense

                                # Attacker roll for damage

                                # Adjust target hitpoint
                            
                            # Else

                                # Respond with attacker miss message

                            # If bad guys are dead or retreated

                                # End combat (set in_combat = True)
                            
                            # Else

                                # Go to next Attacker in initiative list

                                # Attacker determine target
                                # If attacker is player
                                    # let them pick target from list
                                # Else
                                    # let AI pick target from list

                    case _:
                        print("The API returned a function call, but I don't have a case specified for '{case}'.") 
            
                last_finish_reason = "function_call"

            # It's not a function call so just process the GM's response
            else:
                    
                # Capture the GM's response
                try: 
                    # Print out chatbot response
                    assistant_msg = chat.get_content(completion)
                    print("\nGM: " + assistant_msg + "\n")

                except:

                    print("Unable to get the GM's response. Try again...")
                
                last_finish_reason = "stop"


# Continue looping while the play is having dialog with the GM.
while True:

    # Show initial player menu to user
    if skip_menu == False:
        i_main = 5 # Default menu item -- Number of menu items plus one (for default)
        main_menu = input(
            "1. Initiate a new adventure\n" +
            "2. Play a previous session\n" +
            "3. General Chat\n" +
            "> "
        )
        
        if utils.is_integer(main_menu):
            i_main = int(main_menu)
    else:
        skip_menu = False
        
    # Initiate the user's selection
    continue_loop = False
    if i_main == 2: # Enter into a previous session if it is selected
        start_saved_adventure()
    elif i_main == 3: # Enter into general chat if it is selected
        start_chat()
    elif i_main == 1: # Start an adventure if it is selected
        initiate_new_adventure()
    else: # Exit the program
        print("Thanks for playing!")
        exit()
