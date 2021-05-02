import asyncio
import webgram
import aiohttp.web
import logging
from concurrent.futures import CancelledError

logging.basicConfig(level=logging.ERROR)
#logging.basicConfig(level=logging.DEBUG)

loop = asyncio.get_event_loop()
server = webgram.BareServer(loop=loop)

async def main():
    app = aiohttp.web.Application(client_max_size=1024*1024*20)
    app.add_routes([
        aiohttp.web.get('/', server.hello),
        aiohttp.web.get('/w/{hash}', server.watch_stream),
        aiohttp.web.get('/w/{hash}/{name}', server.watch_stream),
        aiohttp.web.get('/test_upload', server.test_upload),
        aiohttp.web.post('/upload_big', server.upload_big),
        aiohttp.web.post('/upload', server.upload),
    
    ])
    return app

