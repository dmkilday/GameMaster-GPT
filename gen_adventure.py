import sys
import os
import openai
from datetime import datetime
import json
import re
import chat
import utils
import copy
import traceback

character_dir = "character/"
adventure_dir = "adventure/"

# Requests a character file from the user and returns the character data
def read_character_file():
    character_file = input("\nIf you have a character sheet file in the Data directory, enter the file name. Leave blank and hit Enter for me to generate a character on the fly: ")
    if character_file != "":
        character_file_path = character_dir + character_file
        if os.path.isfile(utils.get_file_path(character_file_path)):
            character_data = utils.read_file(utils.get_file_path(character_file_path))
        else:
            character_data = "The character is random. Please generate its name, race, class and other stats for me."
    else:
        character_data = "The character is random. Please generate its name, race, class and other stats for me"
    return character_data


# Generates the premise text of an adventure based on user input parameters
def get_premise_text(themes, stages, substage_min, substage_max, dialog):
   
    # Get premise example text file
    premise_example_file = utils.get_file_path("premise_example_small.txt")
    premise_example_small_text = utils.read_file(premise_example_file)
    
    # Set up the prompt
    adventure_dialog = dialog

    chat.append_dialog(adventure_dialog, "user", "Come up with a fun and cool outline for an RPG adventure using the following player information. Be sure to break the adventure into a summary introduction, stages and substages which are clearly identifiable, and a conclusion. Create " + str(stages) + " stages, each having a number of substages. There should be a random number of substages (between " + str(substage_min) + " and " + str(substage_max) + ") within each stage. All stages and substatges must have a title and description. Also, one of the substages will be the entry point for its parent stage. The remaining substages can be played in any order, but only one substage will provide what's needed to progress to the next stage. The entry stage and exit stage cannot be the same stage. Limit your response to 500 words. Here is a good example of an outline you can use as a model. Note, I would like you to emulate the outline example's structure, but not the content. Reminder: create the specified number of stages and substages mentioned earlier - i.e., DO NOT copy the number of substages from the outline example. \n\nOutline Example: " + premise_example_small_text)

    if (themes != ""):
       chat.append_dialog(adventure_dialog, "user", "Use the following list of keywords to influence the premise of the adventure. Keywords: " + themes)

    # Generate a premise for the character.
    print("\nGenerating adventure premise with the following parameters:\n")

    if (themes == ""):
        keywords = "None"
    else:
        keywords = themes

    print("Theme Keywords: " + keywords)
    print("# of Chapters: " + str(stages))
    print("# of Quests per Chapter: " + str(substage_min) + " - " + str(substage_max) + "...\n")

    completion = chat.safe_chat_completion(
        model="gpt-3.5-turbo", 
        max_tokens=2300, 
        messages=adventure_dialog,
        temperature=1
    )

    if completion == -1:
        premise_text = "Introduction:\n\nA chat bot was unable to create an adventure outline because of some error.."
    else:
        premise_text = chat.get_content(completion)

    # Get a title for the file
    title = chat.gen_title(premise_text)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    premise_text_file_name = adventure_dir + "Structure_" + timestamp + "_" + title + ".txt"

    # Write out the premise file
    utils.write_file(premise_text_file_name, premise_text)

    return premise_text_file_name


# Generates a JSON adventure structure file given the premise and an example
def get_premise_json(example_text_file, example_json_file, premise_text_file):

      # Set up the prompt
    messages = []
    chat.append_dialog(messages, "user", "I am going to give you a premise to a RPG adventure, and I want you to output a structured JSON array based on that premise. I will provide you an example     premise input with an example JSON output (which you must adhere to). Then I will provide you with the actual premise input for which I want you to generate the JSON output.")

    # Get example files and premise file data
    premise_example_small_text = utils.read_file(utils.get_file_path(example_text_file))
    premise_example_small_json = utils.read_file(utils.get_file_path(example_json_file))
    premise_text = utils.read_file(utils.get_file_path(premise_text_file))

    # Request data transformation to JSON
    structure_json = chat.transform_data(
                        premise_example_small_text, 
                        premise_example_small_json,
                        premise_text,
                        "",
                        1700)

    # Write out the adventure structure JSON to a file
    premise_json_file_name = premise_text_file.replace(".txt", ".json")
    utils.write_file(premise_json_file_name, structure_json)

    return premise_json_file_name 

# Generates the module JSON which will be used by the DM to facilitate the adventure
def get_module_json(character_data, structure_file):
    
    # Set up initial prompt
    adventure_dialog = []
    chat.append_dialog(adventure_dialog, "user", "You are a brilliant and extremely creative RPG Game Master creating an RPG adventure. You are expected to generate a dynamic narrative which flows logically and includes NPC interactions, combat encounters, skill checks, and player progression. Use the guidelines and rules of role playing games like D&D 5e to create a dynamic and immersive world. Remember, as a Game Master, you have the power to shape the game world and ensure a fun and exciting experience for the players.")

    # Add Character data to the dialog
    chat.append_dialog(adventure_dialog, "user", "The players character sheet is as follows:\n\n" + character_data)

    # Read the adventure structure JSON
    structure_file_path = utils.get_file_path(structure_file)
    with open(structure_file_path, 'r') as file:
        structure_data = json.load(file)

    # Count the number of low level nodes in the structure JSON
    global total_nodes
    global durations
    total_nodes = count_substages(structure_data)
 
    # Create a new dictionary that is a deep copy of the original
    module_obj = copy.deepcopy(structure_data)
    
    # Iterate over stages
    for key in structure_data.keys(): 
             
        # If there are substages in the node, then iterate through them
        # and build the expanded module JSON
        if 'Substages' in structure_data[key]:
            # Iterate over substages
            for substage in structure_data[key]['Substages'].keys():
                
                start_time = datetime.now() # Capture start time of leaf processing

                # Create new dictionary for output
                output_dict = {}
                output_dict['Introduction'] = structure_data['Introduction']

                # Add stage description and specific substage
                output_dict[key] = {
                    'Description': structure_data[key]['Description'],
                    'Substages': {
                        substage: structure_data[key]['Substages'][substage]
                    }
                }

                # Get the expanded dictionary for this stage
                module_node_str = get_module_node(structure_data, output_dict, substage)
                module_node_obj = json.loads(module_node_str)

                # Replace original substage value with expanded dictionary
                module_obj[key]['Substages'][substage] = module_node_obj

                end_time = datetime.now() # Capture end time of leaf processing
                
                # Calculate processing duration and output estimated remaining time  
                duration = utils.get_duration(start_time, end_time)
                durations.append(duration)  # Add duration to list
                print(f"\nQuest node {len(durations)}/{total_nodes} duration: {round(duration)} sec.")

                # Print average duration and estimated remaining time
                avg_duration = sum(durations) / len(durations)
                remaining_nodes = total_nodes - len(durations)
                est_remaining_time = remaining_nodes * duration
                print(f"Average time per node: {round(avg_duration)} sec.")
                print(f"Estimated remaining time: {round(est_remaining_time)} sec.")


    # Create the module JSON file
    fn_array = structure_file.split("_") 
    module_file_name = adventure_dir + "Module_" + fn_array[1] + "_" + fn_array[2] + "_" + fn_array[3] 
    module_file_path = utils.get_file_path(module_file_name)
    with open(module_file_path, 'w') as file:
        json.dump(module_obj, file, indent=4)

    return module_file_name


# Append new JSON node to existing JSON file 
def append_to_json(module_json_obj, node_json_obj):
       module_json_obj.append(node_json_obj)


# Build module JSON node from structure JSON node
def get_module_node(structure_obj, structure_node_obj, substage_title):

    structure_example = "structure_example.json"
    module_example = "module_example.json"

    # Load example source information
    example_source_data = utils.read_file(utils.get_file_path(structure_example))

    # Load example target information
    example_target_data = utils.read_file(utils.get_file_path(module_example))

    structure_str = json.dumps(structure_obj, indent=4)

    # Generate a summary of what has happened in the adventure up until now
    special_instructions = f"Write a summary of what has happened chronologically in the following JSON up to substage {substage_title}. The purpose of the summary to provide context to someone who is not familiar with the story to understand what has happened up to that point. In your summary, only include information from the JSON file up to that point."
    context = chat.gen_summary(structure_str, special_instructions, 100)

    structure_node_str = json.dumps(structure_node_obj, indent=4)

    special_instructions = f"Generate the target node for '{substage_title}'. Be sure to populate all fields with relevant information. This includes populating multiple rewards (e.g. gold, information, favors, items, etc.), and multiple NPCs in the output. And all NPCs should have a complete and relevant set of information (e.g. items, skills/abilities, backstory, etc.) and stats. \n\n Here is some additional information to let you know where we are in the story... {context}"  
    module_node = chat.transform_data(example_source_data, example_target_data, structure_node_str, special_instructions, 2500)

    return module_node


# Initialize node counter and durations to keep track of how long module JSON is taking
total_nodes = 0
durations = []

# Counts the number of substages in a JSON
def count_substages(data):
    count = 0
    for value in data.values():
        if 'Substages' in value:
            count += len(value['Substages'])
    return count

# Main process for generating the adventure
def process_adventure():

    # Set up initial prompt
    adventure_dialog = []
    chat.append_dialog(adventure_dialog, "user", "You are a brilliant and extremely creative Dungeon Master creating a Dungeons & Dragons adventure. You are expected to generate a dynamic narrative which flows logically and includes NPC interactions, combat encounters, skill checks, spellcasting, and player progression. Use the guidelines and rules of D&D 5e to create a dynamic and immersive world. Remember, as a Dungeon Master, you have the power to shape the game world and ensure a fun and exciting experience for the players.")

    print("\nLet's gather some basic information about the adventure so I can generate something awesome!")
    
    premise_example_text = "premise_example_small.txt"
    premise_example_json = "premise_example_small.json"
    
    # Read the premise example
    premise_example_small_text = utils.read_file(utils.get_file_path(premise_example_text))

    # Load player character data
    character_data = read_character_file()
    chat.append_dialog(adventure_dialog, "user", "The players character sheet is as follows:\n\n" + character_data)

    # Gather adventure generation parameters
    themes = input("\nEnter a comma separated list of keywords that you would like to influence the premise of the adventure (Optional): ")
    stages = int(input("\nEnter the number of stages (chapters) that you would like generated (recommend <=4, default is 3): ") or "3")
    substage_min = int(input("\nEnter the minimum number of substages (quests) per stage (recommend >=1, default is 3): ") or "3")
    substage_max = int(input("\nEnter the maximum number of substages (quests) per stage (recommend <=5, default is 3): ") or "3")
   
    # Get the premise text outline file
    premise_text_file_name = get_premise_text(themes, stages, substage_min, substage_max, adventure_dialog)
    print(f"\nCreated premise text file: {premise_text_file_name}\n")
    
    # Get the JSON structure file
    premise_json_file_name = get_premise_json(
        premise_example_text, 
        premise_example_json, 
        premise_text_file_name)
    print(f"\nCreated premise JSON file: {premise_json_file_name}\n")

    # Get the JSON module file
    module_json_file_name = get_module_json(character_data, premise_json_file_name)
    print(f"\nCreated module JSON file: {module_json_file_name}\n")

# Main process for generating the adventure
def process_adventure():
    try:
        # Set up initial prompt
        adventure_dialog = []
        chat.append_dialog(adventure_dialog, "user", "You are a brilliant and extremely creative Game Master creating a turn-based RPG adventure. You are expected to generate a dynamic narrative which flows logically and includes NPC interactions, combat encounters, skill checks, spellcasting, and player progression. Use the guidelines and rules of RPG games like D&D 5e to create a dynamic and immersive world. Remember, as a Game Master, you have the power to shape the game world and ensure a fun and exciting experience for the players.")

        print("\nLet's gather some basic information about the adventure so I can generate something awesome!")

        premise_example_text = "premise_example_small.txt"
        premise_example_json = "premise_example_small.json"

        # Read the premise example
        premise_example_small_text = utils.read_file(utils.get_file_path(premise_example_text))

        # Load player character data
        character_data = read_character_file()
        chat.append_dialog(adventure_dialog, "user", "The players character sheet is as follows:\n\n" + character_data)

        # Gather adventure generation parameters
        themes = input("\nEnter a comma separated list of keywords that you would like to influence the premise of the adventure (Optional): ")
        while True:
            try:
                stages = int(input("\nEnter the number of stages (chapters) that you would like generated (recommend <=4, default is 3): ") or "3")
                break
            except ValueError:
                print("Please enter a valid integer for the number of stages.")

        while True:
            try:
                substage_min = int(input("\nEnter the minimum number of substages (quests) per stage (recommend >=1, default is 3): ") or "3")
                break
            except ValueError:
                print("Please enter a valid integer for the minimum number of substages.")

        while True:
            try:
                substage_max = int(input("\nEnter the maximum number of substages (quests) per stage (recommend <=5, default is 3): ") or "3")
                break
            except ValueError:
                print("Please enter a valid integer for the maximum number of substages.")

        # Get the premise text outline file
        premise_text_file_name = get_premise_text(themes, stages, substage_min, substage_max, adventure_dialog)
        print(f"\nCreated premise text file: {premise_text_file_name}\n")

        # Get the JSON structure file
        premise_json_file_name = get_premise_json(
            premise_example_text,
            premise_example_json,
            premise_text_file_name)
        print(f"\nCreated premise JSON file: {premise_json_file_name}\n")

        # Get the JSON module file
        module_json_file_name = get_module_json(character_data, premise_json_file_name)
        print(f"\nCreated module JSON file: {module_json_file_name}\n")

    except FileNotFoundError as e:
        print("File not found. Please check the file paths.")
        print(str(e))
    except Exception as e:
        print("An unexpected error occurred.")
        print(str(e))


def main():
    try:
        
        process_adventure()
    
    except Exception as e:

        # Gather exception details
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno

        # Print out exception info
        print(f"An error occurred: {e}")
        print(f"Exception type: {exception_type}")
        print(f"File name: {filename}")
        print(f"Line number: {line_number}")
        
        Print out error trace
        print("Trace: \n")
        traceback.print_exc() # Print trace

if __name__ == "__main__":
    main()
