import os
CWD_PATH: str = os.getcwd()
bot_guilds: set[int] = set()
ignored_channels: dict[int, set[int]] = dict()