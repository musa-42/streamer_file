import asyncio
import webgram
import aiohttp.web
import logging
from concurrent.futures import CancelledError
import signal

logging.basicConfig(level=logging.ERROR)
#logging.basicConfig(level=logging.DEBUG)

class AioHttpAppException(BaseException):
    """An exception specific to the AioHttp application."""


class GracefulExitException(AioHttpAppException):
    """Exception raised when an application exit is requested."""


class ResetException(AioHttpAppException):
    """Exception raised when an application reset is requested."""

def handle_sighup() -> None:
    logging.warning("Received SIGHUP")
    raise ResetException("Application reset requested via SIGHUP")


def handle_sigterm() -> None:
    logging.warning("Received SIGTERM")
    raise ResetException("Application exit requested via SIGTERM")


def cancel_tasks() -> None:
    for task in asyncio.Task.all_tasks():
        task.cancel()



loop = asyncio.get_event_loop()
loop.add_signal_handler(signal.SIGHUP, handle_sighup)
loop.add_signal_handler(signal.SIGTERM, handle_sigterm)
server = webgram.BareServer(loop)
        

if __name__ == "__main__":
        try:
            loop.run_forever()
        except ResetException:
            logging.warning("Reloading...")
            cancel_tasks()
            asyncio.set_event_loop(asyncio.new_event_loop())
        except GracefulExitException:
            logging.warning("Exiting...")
            cancel_tasks()
            loop.close()