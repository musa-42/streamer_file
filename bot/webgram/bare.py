import telethon
from telethon import errors, functions, types, events , helpers
import asyncio
import aiohttp
import urllib.parse
from . import (
    Config, StreamTools
)
import io
import re
import os.path
import requests
from telethon.sessions import StringSession

class BareServer(Config, StreamTools):
    client: telethon.TelegramClient
    
    def __init__(self, loop: asyncio.AbstractEventLoop):
        
        self.client = telethon.TelegramClient(
            StringSession(), #self.config.SESS_NAME,
            self.config.APP_ID,
            self.config.API_HASH,
            loop=loop
        ).start(bot_token=self.config.BOT_TOKEN)
        
        
        @self.client.on(events.NewMessage)
        async def download(event : events.NewMessage.Event):
            if event.is_private :
                try:
                    await event.client(functions.channels.GetParticipantRequest(channel=self.config.channel,user_id=event.sender_id))
                except errors.UserNotParticipantError:
                    await event.reply(f"First join to our official channel to access the bot or get the newest news about the bot\n\n@{self.config.channel}\n\nAfter that /start the bot aging.")
                    return
                if event.file :
                    hash = self.encode(f"{event.sender_id}:{event.id}")
                    url = f"{hash}/{urllib.parse.quote(self.get_file_name(event))}"
                    await event.reply(f"Link to download file: \n\n🌍 : {self.config.ROOT_URI}/w/{url}")
                    return

                await event.reply("Send an image or file to get a link to download it")
