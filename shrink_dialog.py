# Local libs
import utils
import messages

# Built-in libs
import os
import openai
from datetime import datetime
import json
import random
import glob
import tiktoken
from dotenv import load_dotenv

# PyPI libs
import re
from colorama import Fore
from colorama import Style

openai.api_key = os.getenv('OPENAI_API_KEY')
os.system('color')
show_tok = True
active = True

# Shrink's dialog by x number of 
def shrink_dialog(dialog, dialog_size, token_limit, model_name):
    # Check if the chat dialog is already within the token limit
    if dialog_size <= token_limit:
        return chat_dialog

    summary_token_size = 200 # limit summary to 200 tokens

    # Identify chat messages that must be consolidated to meet the specified token limit
    
    # Identify average token size of messages
    avg_msg_size = dialog_size / len(dialog) 

    # Determine how many messages need to be consolidated to meet token limit
    # Algebra: 
    # 200 - x*avg_msg_size + (len(dialog)-x)*avg_msg_size = 1000
    # -2x(avg_msg_size) + 200 + len(dialog)*avg_msg_size = 1000
    # x = ((len(dialog)*avg_msg_size) - 800) / (2 * avg_msg_size)
    consolidation_count = ((len(dialog) * avg_msg_size) + summary_token_size - token_limit) / (2 * avg_msg_size)

    # Grab the number of messages to consolidate and summarize their text
    item_count = 0
    temp_dialog = []
    dialog_text = ""

    # Loop through the dialog items
    for record in dialog.values():
        item_count += 1
        temp_dialog.append(record)
        dialog_prefix = ""
        
        # Determine if the message is GM or Player
        if (record[0].value() == "assistant"):
            prefix = "\nGM: "
        else:
            prefix = "\nPlayer: "
        
        # Append the item to dialog text
        dialog_text += prefix + record[1].value() + "\n"

        # Brek out of loop once we;ve reach the number of items to summarize
        if (item_count == consolidation_count):
            break

    # Create a new summarized message
    instructions = "Summarize this dialog between the GM and the player, telling a story of what happened as if it happened in the past."
    summary_text = chat.get_summary(dialog, instructions, summary_token_size)

    print(f"\nSummary Text: {summary_text}")

    # TODO: Replace summarized messages with the summary message

#    # Start grouping and summarizing from the oldest message
#    new_dialog = []
#    temp_group = []
#    temp_group_content = ''
#    for msg in chat_dialog:
#        temp_group.append(msg)
#        temp_group_content += ' ' + msg['content']
#
#        if count_tokens(temp_group_content, model_name) > token_limit:
#            # If adding a new message exceeds the limit, 
#            # summarize the group without the last message and start a new group
#            summarized_content = summarize_text(temp_group_content[:-len(msg['content'])], token_limit)
#            new_dialog.append({'id': temp_group[0]['id'], 'role': 'system', 'content': summarized_content})
#            
#            temp_group = [msg]  # start new group with the last message
#            temp_group_content = msg['content']
#
#    # Don't forget to process the last group
#    if temp_group:
#        summarized_content = summarize_text(temp_group_content, token_limit)
#        new_dialog.append({'id': temp_group[0]['id'], 'role': 'system', 'content': summarized_content})
#
    return new_dialog


