import re

from emoji import demojize
from nextcord import Emoji
from nextcord.ext.commands import Bot


cdef:
    findall_id = re.compile(r"\d+", flags=re.RegexFlag.MULTILINE | re.RegexFlag.IGNORECASE).findall
    findall_emoji = re.compile(r":[A-Za-z\d_]+:", flags=re.RegexFlag.MULTILINE | re.RegexFlag.IGNORECASE).findall

def parse_emoji(bot: Bot, str string) -> Emoji | str | None:
    if string.isdecimal() is True:
        emoji = bot.get_emoji(int(string))
        if emoji is not None:
            return emoji

    cdef:
        list finds = findall_id(string)
        size_t length = len(finds)
        size_t i = 0

    # More predicted branch, but we dont want
    # to call slow <demojize> function first
    if length == 0:
        finds = findall_emoji(demojize(string))
        return finds[0] if finds else None

    get_emoji = bot.get_emoji
    while (i < length):
        emoji = get_emoji(int(finds[i]))
        if emoji is not None:
            return emoji
        i += 1

    return None
