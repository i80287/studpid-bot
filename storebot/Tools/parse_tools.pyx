from re import RegexFlag, Pattern, compile, findall

from emoji import demojize
from nextcord import Emoji
from nextcord.ext.commands import Bot

cimport cython

class ParseTools:
    custom_emoji_pattern: Pattern = compile("\d+", flags=RegexFlag.MULTILINE | RegexFlag.IGNORECASE)
    default_emoji_pattern: Pattern = compile(":[A-Za-z\d_]+:", flags=RegexFlag.MULTILINE | RegexFlag.IGNORECASE)
    
    @cython.profile(False)
    @cython.nonecheck(False)
    @cython.wraparound(False) # Deactivate negative indexing.
    @cython.boundscheck(False) # Deactivate bounds checking    
    @classmethod
    def parse_emoji(cls, bot: Bot, str string) -> Emoji | str | None:
        if string.isdigit():
            emoji = bot.get_emoji(int(string))
            if emoji:
                return emoji

        cdef:
            list finds = findall(cls.custom_emoji_pattern, string)
        if finds:
            emoji = bot.get_emoji(int(finds[0]))
            if emoji:
                return emoji
        
        finds = findall(cls.default_emoji_pattern, demojize(string))
        if not finds:
            return None        
        return finds[0]
