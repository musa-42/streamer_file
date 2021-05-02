from telethon.tl.types import MessageMediaDocument
from telethon.tl.types import Message
from telethon.tl import functions
from aiohttp import web
from telethon.tl import types
import typing
import re
import telethon
import io
import urllib
import asyncio
import random

if typing.TYPE_CHECKING:
    import webgram


RANGE_REGEX = re.compile(r"bytes=([0-9]+)-")
BLOCK_SIZE = telethon.client.downloads.MAX_CHUNK_SIZE


class Streamer:
    
    async def hello(self: 'webgram.BareServer', request: web.Request) -> web.Response:
    	return web.Response(text="Hello, world")

    async def watch_stream(self: 'webgram.BareServer', request: web.Request) -> web.Response:
            
        if request.match_info.get("hash"):
            hash = self.decode(request.match_info["hash"]).split(":")
            peer = self.to_int_safe(hash[0])
            mid = hash[1]
            
        else:
            return web.Response(text="This link is no longer supported, please create a new link")
            
        if not mid.isdigit() or not await self.validate_peer(peer):
            return web.HTTPNotFound()
            
        message: Message = await self.client.get_messages(peer, ids=int(mid))

        if not message or not message.file :
            return web.HTTPNotFound()

        offset = request.headers.get("Range", 0)

        if not isinstance(offset, int):
            matches = RANGE_REGEX.search(offset)

            if matches is None:
                return web.HTTPBadRequest()

            offset = matches.group(1)

            if not offset.isdigit():
                return web.HTTPBadRequest()

            offset = int(offset)

        file_size = message.file.size
        download_skip = (offset // BLOCK_SIZE) * BLOCK_SIZE
        read_skip = offset - download_skip
        
        if request.match_info.get("name"):
            name = request.match_info["name"]
        else:
            name = self.get_file_name(message)

        if download_skip >= file_size:
            return web.HTTPRequestRangeNotSatisfiable()

        if read_skip > BLOCK_SIZE:
            return web.HTTPInternalServerError()

        resp = web.StreamResponse(
            headers={
                'Content-Type': message.file.mime_type, #'application/octet-stream',
                'Accept-Ranges': 'bytes',
                'Content-Range': f'bytes {offset}-{file_size}/{file_size}',
                "Content-Length": str(file_size),
                "Content-Disposition": f'attachment; filename={name}',
            },

            status=206 if offset else 200,
        )

        await resp.prepare(request)

        cls = self.client.iter_download(message.media, offset=download_skip)

        async for part in cls:
            if len(part) < read_skip:
                read_skip -= len(part)

            elif read_skip:
                await resp.write(part[read_skip:])
                read_skip = 0

            else:
                await resp.write(part)

        return resp

    async def grab_m3u(self: 'webgram.BareServer', request: web.Request) -> web.Response:
        peer = self.to_int_safe(request.match_info["peer"])

        if not await self.validate_peer(peer):
            return web.HTTPNotFound()

        resp = web.StreamResponse(
            status=200,
            headers={
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': f'filename={peer}.m3u'
            }
        )

        await resp.prepare(request)

        async for messages in self.iter_files(peer):
            for part in self.messages_to_m3u(messages, peer):
                await resp.write(part.encode(self.config.ENCODING))
                await resp.write(b"\n")

            await resp.drain()

        return resp

    async def test_upload(self: 'webgram.BareServer', request: web.Request) -> web.Response:
        f = open("webgram/app.html","r")
        text = f.read()
        return web.Response(text=text,content_type='text/html')

    async def upload_big(self: 'webgram.BareServer', request: web.Request) -> web.Response:
            data = await request.post()
            input_file = data["file"].file
            content = input_file.read()
            file_id = int(data["file_id"])
            part =  int(data["part"])
            parts =  int(data['parts'])
            end = int(data["end"])
            size = int(data["size"])
            r = await self.client(functions.upload.SaveBigFilePartRequest(
                        file_id,part,parts, content))
            # print(r , end ,size , part , parts)
            if end == size:
                r = types.InputFileBig(int(data["file_id"]),int(data['parts']) ,data["filename"])
                msg = await self.client.send_file(self.config.STATS_CHANNEL,r)
                hash = self.encode(f"{msg.chat_id}:{msg.id}")
                link = f"{hash}/{urllib.parse.quote(self.get_file_name(msg))}"
                return web.Response(text=f'{end} {size} link {self.config.ROOT_URI}/watch/{link}' , content_type='text/html')

            return web.Response(text=f"{end} {size} {end*100 // size}")

    async def upload(self: 'webgram.BareServer', request: web.Request) -> web.Response:
            data = await request.post()
            input_file = data["file"].file
            content = input_file.read()
            f = io.BytesIO(content)
            f.name = data["filename"]
            end = int(data["end"])
            msg = await self.client.send_file(self.config.STATS_CHANNEL,file=f)
            hash = self.encode(f"{msg.chat_id}:{msg.id}")
            link = f"{hash}/{urllib.parse.quote(self.get_file_name(msg))}"
            return web.Response(text=f'{end} {end} link {self.config.ROOT_URI}/watch/{link}' , content_type='text/html')
