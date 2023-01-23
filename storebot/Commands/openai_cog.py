import re
import openai
from asyncio import Lock
from typing import Literal

from nextcord import (
    slash_command,
    Locale,
    Interaction,
    SlashOption,
    Embed
)
from nextcord.ext.commands import Cog

from storebot import StoreBot
from Tools.logger import Logger
from Variables.vars import BANNED_WORDS
from config import OPENAI_API_KEY


class OpenAICog(Cog):
    openai_lock: Lock = Lock()
    openai_cog_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Your query contains strange words...`**",
            1: "**`Question:`**\n{0}\n**`OpenAI thinks what to respond...`**",
            2: "**`Answer:`**\n{0}",
        },
        1: {
            0: "**`В Вашем запросе есть странные слова...`**",
            1: "**`Вопрос:`**\n{0}\n**`OpenAI думает, что ответить...`**",
            2: "**`Ответ:`**\n{0}",
        }
    }
    words_filter: re.Pattern[str] = re.compile(
        pattern=BANNED_WORDS,
        flags=re.RegexFlag.IGNORECASE | re.RegexFlag.MULTILINE
    )

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot
        openai.api_key = OPENAI_API_KEY
    
    @slash_command(
        name="ask",
        description="Ask OpenAI anything",
        description_localizations={
            Locale.ru: "Спросить OpenAI о чём угодно"
        },
        dm_permission=False
    )
    async def ask_openai(
        self,
        interaction: Interaction,
        question: str = SlashOption(
            name="question",
            name_localizations={
                Locale.ru: "вопрос"
            },
            description="Question for the OpenAI",
            description_localizations={
                Locale.ru: "Вопрос к OpenAI"
            },
            required=True,
            min_length=1,
            max_length=420
        )
    ) -> None:
        assert interaction.user is not None
        assert interaction.guild is not None
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        if self.words_filter.findall(question):
            await interaction.response.send_message(embed=Embed(description=self.openai_cog_text[lng][0]))
            return
        
        await interaction.response.send_message(embed=Embed(description=self.openai_cog_text[lng][1].format(question)))
        async with self.openai_lock:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=question,        
                temperature=0.6,
                max_tokens=1984,
                top_p=1,
                frequency_penalty=0.5,
                presence_penalty=0.0
            )
        answer: str = response.choices[0].text.strip('\n') # type: ignore
        await interaction.followup.send(embed=Embed(description=self.openai_cog_text[lng][2].format(answer)))
        await Logger.write_log_async(
            "openai_logs.log",
            f"member {interaction.user.id}:{interaction.user.name}",
            f"guild {interaction.guild_id}:{interaction.guild.name}",
            question,
            answer
        )


def setup(bot: StoreBot) -> None:
    bot.add_cog(OpenAICog(bot))
