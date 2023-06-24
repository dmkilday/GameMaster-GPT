import os
from dotenv import load_dotenv
from dotenv import set_key
from pathlib import Path

OPENAI_API_KEY='sk-******'
DISCORD_TOKEN='**********'

if os.path.isfile("oauth_secret.py"):
    env_file_path = Path("./.env")
    if not os.path.isfile(env_file_path):
        # Create new .env file and populate with defaults from above.
        rfile = open("./.env.template","r")
        template = rfile.read()
        rfile.close()
        wfile = open(env_file_path,"w")
        wfile.write(template)
        wfile.close()
        
    else:
        try:
            OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
            DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
        except:
            print("Did not find OPENAI_API_KEY or DISCORD_TOKEN in .env file.\n\nReading from oauth_secret if they exist,\nor leaving non-working defaults.")
        
    
    import oauth_secret
    if oauth_secret.secret_key != OPENAI_API_KEY:
        set_key(dotenv_path=env_file_path,key_to_set="OPENAI_API_KEY", value_to_set=oauth_secret.secret_key)
        
    if oauth_secret.DISCORD_TOKEN != DISCORD_TOKEN:
        set_key(dotenv_path=env_file_path,key_to_set="DISCORD_TOKEN", value_to_set=oauth_secret.DISCORD_TOKEN)
        
    print("Created .env file and imported keys from 'oauth_secret'")    
    exit()
    os.remove("oauth_secret.py")