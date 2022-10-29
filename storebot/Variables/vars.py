import os
path_to: str = os.getcwd()
bot_guilds: set[int] = set()
ignored_channels: dict[int, set[int]] = dict()