# Template for the Telegram Bot
To proceed implement the following steps:
1. Change the BOT_TOKEN in the config.ini
2. Create an environment to make things consistent
3. Adjust commands if necessary, since currently /start is the default one
4. If you want to include database – create Firebase and then download Account Creads JSON to the app/constants with serviceAccount.json name. Make sure to include the database url in the config.ini. If you want to use SQLite -> remove default db.py and unpack SQLite folder with the existing template. Also make sure to create a database there.

# RAG system
- Before you run RAG system make sure to upload docs to app/constants/docs and change the DOC_NAME variable inside the config.ini file.
- Make sure to run ollama locally or implement subprocess command for it to serve and then terminate the session.
- If you changed doc content for RAG, make sure to delete the cache to avoid any possile troubles with it. Cache generates automatically, no need to perform any actions here
- To run RAG just use the appropriate `ask_llm()` function inside the app/utils/ai.py
- Make sure to parse llm response, since it's a list of answers (to make easier for AI, I've separated questions with question mark..)

# What stack used
- Aiogram
- Google Firebase (or SQLite; customizable)
- Configparser (by default all secured stuff is saved in the config.ini)

