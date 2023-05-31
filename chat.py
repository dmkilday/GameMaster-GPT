# Local libs
import oauth_secret
import utils

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
response_len_max = 40
show_tok = True
active = True

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