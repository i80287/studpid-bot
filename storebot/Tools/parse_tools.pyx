import re

from emoji import demojize
from nextcord import Emoji
from nextcord.ext.commands import Bot

cimport cython

cdef:
    _CUSTOM_EMOJI_PATTERN = re.compile("\d+", flags=re.RegexFlag.MULTILINE | re.RegexFlag.IGNORECASE)
    _DEFAULT_EMOJI_PATTERN = re.compile(":[A-Za-z\d_]+:", flags=re.RegexFlag.MULTILINE | re.RegexFlag.IGNORECASE)

@cython.profile(False)
@cython.nonecheck(False)
@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def parse_emoji(bot: Bot, str string) -> Emoji | str | None:
    if string.isdigit():
        emoji = bot.get_emoji(int(string))
        if emoji:
            return emoji

    cdef:
        list finds = _CUSTOM_EMOJI_PATTERN.findall(string)
    if finds:
        emoji = bot.get_emoji(int(finds[0]))
        if emoji:
            return emoji
    
    finds = _DEFAULT_EMOJI_PATTERN.findall(demojize(string))
    if finds:
        return finds[0]
    return None
