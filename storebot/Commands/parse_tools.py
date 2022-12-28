from re import RegexFlag, Pattern, compile, findall

from emoji import demojize
from nextcord import Emoji
from nextcord.ext.commands import Bot

class ParseTools:
    custom_emoji_pattern: Pattern = compile("\d+", flags=RegexFlag.MULTILINE | RegexFlag.IGNORECASE)
    default_emoji_pattern: Pattern = compile(":[A-Za-z\d_]+:", flags=RegexFlag.MULTILINE | RegexFlag.IGNORECASE)
        
    @classmethod
    def parse_emoji(cls, bot: Bot, string: str) -> Emoji | str | None:
        if string.isdigit() and (emoji := bot.get_emoji(int(string))):
            return emoji
        
        finds: list = findall(cls.custom_emoji_pattern, string)
        if finds and (emoji := bot.get_emoji(int(finds[0]))):            
            return emoji
        
        finds: list = findall(cls.default_emoji_pattern, string)
        if not finds:
            return None
        for sub_str in finds:
            if demojized := demojize(sub_str):
                return demojized
        
        return None
