import os 

class Config:

    class config:
        APP_ID = 50807

        API_HASH = "......"
        
        BOT_TOKEN = "...."
        
        HOST = "127.0.0.1"

        PORT = os.getenv('PORT')

        ROOT_URI = f"http://dlstarus.dlgram.ml"


        ENCODING = "utf8"


        # ALLOWED_EXT = ["mkv", "mp4", "flv"]
