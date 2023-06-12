# Local libs
import oauth_secret
import utils
import messages

# Built-in libs
import os
import openai
from datetime import datetime
import json
import random
import glob

# PyPI libs
import re
from colorama import Fore
from colorama import Style

openai.api_key = oauth_secret.secret_key
os.system('color')
show_tok = True
active = True

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
        if show_tok:
            tok_prompt = apiresponse['usage'].prompt_tokens
            tok_complt = apiresponse['usage'].completion_tokens
            tok_total = apiresponse['usage'].total_tokens
            utils.color_print(f"\n{Fore.YELLOW}[Prompt:{Fore.WHITE}{Style.BRIGHT}{tok_prompt}{Fore.YELLOW}{Style.NORMAL}, Completions:{Fore.WHITE}{Style.BRIGHT}{tok_complt}{Fore.YELLOW}{Style.NORMAL}, Total:{Fore.WHITE}{Style.BRIGHT}{tok_total}{Fore.YELLOW}{Style.NORMAL}]{Style.RESET_ALL}")
        content = apiresponse['choices'][0]['message']['content']
    return content
    
def safe_chat_completion(model, messages, max_tokens=-1, temperature=1):
    if messages == "error_test":
        utils.color_print(f"{Fore.RED}Test Error{Style.RESET_ALL}: We're not sending anything to OpenAI. This should be red!")
        return -1
    else:
        try:
            if max_tokens == -1:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
            else:
                response = openai.ChatCompletion.create(
                    model=model,
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
                model="gpt-3.5-turbo",
                max_tokens=max_tokens,
                messages=messages,
                temperature=0
                )

    # Return the tranformed data
    return get_content(response)

# Generates a summary for a text string within a given number of words.
def gen_summary(text, special_instructions, max_words):

    # Set up prompt
    messages = []
    append_dialog(messages, "user", f"I am going to give you a string of text and I want you to return a summary paragraph in {max_words} words or less. Return no other information.")
    append_dialog(messages, "user", f"Special Instructions: {special_instructions}")
    append_dialog(messages, "user", f"Here is the text to be summarized: \"\"\"{text}\"\"\"")

    # Debug
    #print(messages)

    # Call the chat bot
    completion = safe_chat_completion(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000,
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
        model="gpt-3.5-turbo",
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
