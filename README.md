# GameMaster-GPT
GameMaster-GPT is an exciting new open-source project aimed at revolutionizing the world of role-playing games (RPGs) by introducing an AI-powered Game Master. With the power of OpenAI's cutting-edge language model, this project enables the creation and facilitation of immersive RPG adventures like never before.

## Requirements
- Tested on Python 3.7.4 and 3.10.11
- An OpenAI secret key, retrievable at [platform.openai.com](https://platform.openai.com/account/api-keys). Rename [oauth_secret.py.dist](https://github.com/dmkilday/GameMaster-GPT/blob/main/oauth_secret.py.dist) to *oauth_secret.py*, and copy your key into the *secret_key* variable within.

To install required libraries, run "pip install -r requirements.txt".

## How to play
1. At the command line type "python gm-gpt.py".
2. When prompted for a character sheet type the name of a text file (in the Data directory) containing the character's details.
3. When prompted, enter an adventure premise. To have the DM generate a premise based on your character sheet, just hit enter when prompted for the premise.
4. Once a premise has been specified, the GM will start your adventure. When prompted to roll, simply type your roll in the format [die count]d[die size]. For example, to roll one 20 sided die, you would type 1d20 (or just d20 if you are only rolling 1 die) and hit Enter. The program will roll for you and report back to the DM your roll results.

## Notes and Todo
**Player Menu**
- Character Generation
  - Input your name, race, class, & background (let me provide ones)
  - Input your Level 1 stats (or let me provide one)
    - What level is your character now?
      - Input level-up stat increases or optional feats (or I can provide them for you).
  - Input your backstory and description (height/hair color/eye color/gender), or let me provide one.
    - For user-provided backstory, process length and content, optionally prompt to offer expansion if it's short.
  - Input known/learned spells for spellcasters (or let me pick)
  - Input equipment in addition to class/background equipment (or let provide it)
    - Your L1 character started with X gold/silver/copper. Do you have any other items of value?
      - Do you want to spend any of that to buy more equipment now (I can make recommendations too)?
  - Input your flaws, bonds, and other features (or let me suggest a few based on your backstory (and the backstories of other players in the case of bonds)).

## Credits
Written by Damian Kilday and Daniel Powell
