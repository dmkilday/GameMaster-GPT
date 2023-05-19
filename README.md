# faith-n-tech_d7d
Running a D&amp;D bot via OpenAI API 

## Requirements
- Tested on Python 3.7.4
- An OpenAI secret key, retrievable at [platform.openai.com](https://platform.openai.com/account/api-keys). Paste this into the *secret_key* variable within [oauth_secret.py](https://github.com/depwl9992/faith-n-tech_d7d/blob/main/oauth_secret.py.dist)

`pip install openai`

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
