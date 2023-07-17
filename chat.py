# Local libs
import utils
import messages
import ai_functions

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

# Load environment variables
load_dotenv()
FAST_LLM_MODEL = os.getenv('FAST_LLM_MODEL')
SMART_LLM_MODEL = os.getenv('SMART_LLM_MODEL')
CREATIVE_TEMPERATURE = int(os.getenv('CREATIVE_TEMPERATURE'))
DETERMINISTIC_TEMPERATURE = int(os.getenv('DETERMINISTIC_TEMPERATURE'))
SHOW_TOKEN_STATUS = os.getenv("SHOW_TOKEN_STATUS")

openai.api_key = os.getenv('OPENAI_API_KEY')

os.system('color')
active = True

# Generates a character sheet based on a prompt
def gen_character(dialog, character_prompt, full_text_log):
    
    character_data = ""
    
    # Default character data as error condition. We will update to the 
    # actual character data if we are successful in retreiving it.
    character_data = "Unable to generate a character."

    # Add player message to ongoing dialog and text log
    append_dialog(dialog, "user", character_prompt)
 
    # Call chat completion API
    completion = safe_chat_completion(
        model=FAST_LLM_MODEL,
        messages=dialog,
        function_call="none"
    )
     
    # Debug chat completion
    #print(f"\n{completion}\n")
    
    finish_reason = get_finish_reason(completion)
    
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
            assistant_msg = get_content(completion)
            if assistant_msg != -1:
                append_dialog(dialog, "assistant", assistant_msg)
                full_text_log += "GM: " + assistant_msg + "\n\n"
                character_data = assistant_msg
    
    return character_data


# Returns s description of the start of the adventure
def get_adventure_hook(dialog, full_text_log):
    
    # Default adventure hook as error condition. We will update to the 
    # actual hook if we are successful in retreiving it.
    adventure_hook = "Unable to retrieve adventure start information."
    
    user_msg = "Provide a brief two sentence description of the player's starting point for the adventure."

    # Add player message to ongoing dialog and text log
    append_dialog(dialog, "user", user_msg)
 
    # Call chat completion API
    completion = safe_chat_completion(
        model=FAST_LLM_MODEL,
        messages=dialog,
        function_call="none"
    )
     
    # Debug chat completion
    #print(f"\n{completion}\n")
    
    finish_reason = get_finish_reason(completion)
    
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
            assistant_msg = get_content(completion)
            if assistant_msg != -1:
                append_dialog(dialog, "assistant", assistant_msg)
                full_text_log += "GM: " + assistant_msg + "\n\n"
                adventure_hook = assistant_msg
    
    return adventure_hook


# Returns the finish reason in the chat completion
def get_finish_reason(completion):
    finish_reason = ""
    try:
        finish_reason = completion.choices[0].finish_reason
    except:
        print("Unable to get finish reason. Please try again.")
    return finish_reason

# Determines if the chat completion is returning a function call
def is_function_call(completion):
    is_function = False
    if get_finish_reason(completion) == "function_call":
        is_function = True
    return is_function

# Returns the name of the function being called from the chat completion
def get_function(completion):
    reply_content = completion.choices[0].message 
    function_name = reply_content.to_dict()['function_call']['name']
    return function_name
 
# Returns a JSON dict of arguments in the chat completion function call
def get_function_args(completion):
    reply_content = completion.choices[0].message 
    arguments = reply_content.to_dict()['function_call']['arguments']
    args = json.loads(arguments)
    return args

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
    summary_text = get_summary(dialog, instructions, summary_token_size)

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


# Returns the number of tokens in a chat dialog.
def get_token_size_messages(messages, model="gpt-3.5-turbo"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return get_token_size_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return get_token_size_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def get_token_size_string(string: str, model_name: str) -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


# Appends messages to dialog array
def append_dialog(dialog, role, content):

    # If dialog is empty, add the system starting message
    if len(dialog) == 0:
        dialog.append({"role": "system", "content": messages.system_initialize})
    
    # Append the requested message
    dialog.append({"role": role, "content": content})


# Retrieves the content from OpenAI API response
def get_content(apiresponse):
    if apiresponse == -1:
        content = -1
    else:
        content = apiresponse['choices'][0]['message']['content']
    return content
    
def safe_chat_completion(model, messages, max_tokens=-1, temperature=1, function_call="none"):
    if messages == "error_test":
        utils.color_print(f"{Fore.RED}Test Error{Style.RESET_ALL}: We're not sending anything to OpenAI. This should be red!")
        return -1
    else:
        try:
            if max_tokens == -1:
                response = openai.ChatCompletion.create(
                    model=model,
                    functions=ai_functions.functions,
                    function_call=function_call,
                    messages=messages,
                    temperature=temperature
                )
            else:
                response = openai.ChatCompletion.create(
                    model=model,
                    functions=ai_functions.functions,
                    function_call=function_call,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
        except openai.error.APIError as e:
            utils.color_print(f"{Fore.RED}OpenAI API returned an API Error{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.APIConnectionError as e:
            utils.color_print(f"{Fore.RED}Failed to connect to OpenAI API{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.RateLimitError as e:
            utils.color_print(f"{Fore.RED}OpenAI API request exceeded rate limit{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.Timeout as e:
            utils.color_print(f"{Fore.RED}OpenAI API request timed out{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.InvalidRequestError as e:
            utils.color_print(f"{Fore.RED}Invalid request to OpenAI API{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.AuthenticationError as e:
            utils.color_print(f"{Fore.RED}Authentication error with OpenAI API{Style.RESET_ALL}: {e}")
            return -1
        except openai.error.ServiceUnavailableError as e:
            utils.color_print(f"{Fore.RED}OpenAI API service unavailable{Style.RESET_ALL}: {e}")
            return -1
        else:
            # Show tokens if this is enabled.
            if SHOW_TOKEN_STATUS == "True":
                tok_prompt = response['usage'].prompt_tokens
                tok_complt = response['usage'].completion_tokens
                tok_total = response['usage'].total_tokens
                utils.color_print(f"\n{Fore.YELLOW}[Prompt:{Fore.WHITE}{Style.BRIGHT}{tok_prompt}{Fore.YELLOW}{Style.NORMAL}, Completions:{Fore.WHITE}{Style.BRIGHT}{tok_complt}{Fore.YELLOW}{Style.NORMAL}, Total:{Fore.WHITE}{Style.BRIGHT}{tok_total}{Fore.YELLOW}{Style.NORMAL}]{Style.RESET_ALL}")

            return response

# Generates an output based on an source example, target example, and source data
def transform_data(example_source, example_target, source, special_instructions, max_tokens):
   
    # Set up the prompt
    messages = []
    append_dialog(messages, "user", "I am going to give you some data, and I want you to to transform that data into another format using an example. I will provide you an example input with a cooresponding example output (which you must strictly adhere to). Then I will provide you with the actual input for which I want you to generate the output.")
    append_dialog(messages, "user", f"Here is the example input: \"\"\"{example_source}\"\"\"")
    append_dialog(messages, "user", f"Here is the example output: \"\"\"{example_target}\"\"\"")
    
    if (special_instructions != ""):
        append_dialog(messages, "user", f"Special Instructions: {special_instructions}")

    append_dialog(messages, "user", f"Important Reminder: do not provide any other information in your response other than what I have specified. Here is the actual input for which you will generate the output: \"\"\"{source}\"\"\"")

    # Call the API to perform the transformation
    response = safe_chat_completion(
                model=FAST_LLM_MODEL,
                max_tokens=max_tokens,
                messages=messages,
                temperature=DETERMINISTIC_TEMPERATURE
                )

    # Return the tranformed data
    return get_content(response)

# Generates a summary for a text string within a given number of words.
def gen_summary(text, special_instructions, max_tokens):

    # Set up prompt
    messages = []
    append_dialog(messages, "user", f"I am going to give you a string of text and I want you to return a summary paragraph. Return no other information.")
    append_dialog(messages, "user", f"Special Instructions: {special_instructions}")
    append_dialog(messages, "user", f"Here is the text to be summarized: \"\"\"{text}\"\"\"")

    # Debug
    #print(messages)

    # Call the chat bot
    completion = safe_chat_completion(
        model=FAST_LLM_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=1
    )
    
    # Check for error
    if completion == -1:
        assistant_msg = "ExitedWithError"
    else:
        assistant_msg = get_content(completion)

    #print("\nCompleted summarization.\n")

    return assistant_msg

# Generates a title for a given string of text
def gen_title(text):
    
    # Set up prompt
    messages = []
    append_dialog(messages, "user", f"Generate an 8-15 character alphanumeric title for this adventure to be used in a filename. Only respond with the actual title (e.g. don't respond with the word 'Title:' before the actual title). Adventure Premise: {text}")

    # Call the chat bot
    completion = safe_chat_completion(
        model=FAST_LLM_MODEL,
        messages=messages,
        max_tokens=10,
        temperature=0
    ) 
  
    # Check for error
    if completion == -1:
        assistant_msg = "ExitedWithError"
    else:
        assistant_msg = get_content(completion)

    # Srtip all whitespaces and special characters
    stripped_response = ''.join(e for e in assistant_msg if e.isalnum())
    
    # Remove "Title" from the beginning of the response if it's there
    if stripped_response.startswith("Title"):
        title = stripped_response[len("Title"):]
    else:
        title = stripped_response

    return title
