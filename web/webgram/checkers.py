import typing

if typing.TYPE_CHECKING:
    import webgram


class Checkers:
    async def validate_peer(self: 'webgram.BareServer', peer: str) -> bool:
        try:
            await self.client.get_peer_id(peer)
            return True

        except ValueError:
            return False

    @staticmethod
    def check_int(x: str) -> bool:
        if x[0] in ('-', '+'):
            return x[1:].isdigit()

        return x.isdigit()

    def to_int_safe(self: 'webgram.BareServer', x: str) -> typing.Union[str, int]:
        return int(x) if self.check_int(x) else x
