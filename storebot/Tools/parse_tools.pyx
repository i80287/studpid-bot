import re

from emoji import demojize
from nextcord import Emoji
from nextcord.ext.commands import Bot

cimport cython

cdef:
    _CUSTOM_EMOJI_PATTERN = re.compile(r"\d+", flags=re.RegexFlag.MULTILINE | re.RegexFlag.IGNORECASE)
    _DEFAULT_EMOJI_PATTERN = re.compile(r":[A-Za-z\d_]+:", flags=re.RegexFlag.MULTILINE | re.RegexFlag.IGNORECASE)

def parse_emoji(bot: Bot, str string) -> Emoji | str | None:
    if string.isdigit():
        emoji = bot.get_emoji(int(string))
        if emoji:
            return emoji

    print(string)
    cdef:
        list finds = _CUSTOM_EMOJI_PATTERN.findall(string)
        size_t length = len(finds)
        size_t i
    
    if finds:
        i = 0
        while i < length:
            emoji = bot.get_emoji(int(finds[i]))
            if emoji:
                return emoji
            i += 1

    finds = _DEFAULT_EMOJI_PATTERN.findall(demojize(string))
    if finds:
        return finds[0]
    return None
