import os
import utils
from dotenv import load_dotenv
from dotenv import set_key
from pathlib import Path

OPENAI_API_KEY='sk-******'
DISCORD_TOKEN='**********'

if os.path.isfile("oauth_secret.py"):
    env_file_path = Path("./.env")
    if not os.path.isfile(env_file_path):
        # Create new .env file and populate with defaults from above.
        template = utils.read_file(".env.template")
        utils.write_file_nd(".env",template)
        print("Copied .env.template to .env for defaults.")
       
    else:
        try:
            OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        except:
            print("Did not find OPENAI_API_KEY or DISCORD_TOKEN in .env file.\n\nReading from oauth_secret if they exist,\nor leaving non-working defaults.")
        
    user_msg = input("We will be migrating oauth_secret.py contents into .env.\n\n"
        "If you are paranoid about this, make a backup of oauth_secret.py outside the application directory "
        "or be ready to regenerate another from https://platform.openai.com/account/api-keys")
    
    import oauth_secret
    
    print("Importing keys from oauth_secret...")
    try:
        if oauth_secret.secret_key != OPENAI_API_KEY:
            set_key(dotenv_path=env_file_path,key_to_set="OPENAI_API_KEY", value_to_set=oauth_secret.secret_key)
        print("oauth_secret.secret_key successfully imported to .env file.")
    
    except:
        print("oauth_secret.secret_key not found. Unable to import key value to .env file.")
    
    try:
        if oauth_secret.DISCORD_TOKEN != DISCORD_TOKEN:
            set_key(dotenv_path=env_file_path,key_to_set="DISCORD_TOKEN", value_to_set=oauth_secret.DISCORD_TOKEN)
        print("oauth_secret.DISCORD_TOKEN successfully imported to .env file.")

    except:     
        print("oauth_secret.DISCQRD_TOKEN not found. Unable to import key value to .env file.")

    print("oauth_secret key value import complete!")
    os.remove("oauth_secret.py")
