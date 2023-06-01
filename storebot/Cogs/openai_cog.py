from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal

    from ..storebot import StoreBot

import re
import openai
from asyncio import Lock, sleep

from nextcord import (
    slash_command,
    Embed,
    Locale,
    SlashOption,
    Interaction
)
from nextcord.ext.commands import Cog
from nextcord.channel import TextChannel
from nextcord.threads import Thread

from ..Tools.logger import (
    write_log_async,
    write_one_log_async
)
from ..constants import BANNED_WORDS
try:
    from ..config import OPENAI_API_KEY
except:
    from ..config_example import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
words_filter: re.Pattern[str] = re.compile(
    pattern=BANNED_WORDS,
    flags=re.RegexFlag.IGNORECASE | re.RegexFlag.MULTILINE
)
del OPENAI_API_KEY
del BANNED_WORDS

class OpenAICog(Cog):
    openai_lock: Lock = Lock()
    openai_cog_text: dict[int, dict[int, str]] = {
        0: {
            0: "**`Your query contains strange words...`**",
            1: "**`Question:`**\n{0}\n**`OpenAI thinks what to respond...`**",
            2: "**`Answer:`**\n{0}",
            3: "**`Sorry, but this command can't be used in this channel. Please, try use it in common text channel or thread`**",
            4: "**`System was not able to answer your question`**",
            5: "**`An error occurred during sending response`**"
        },
        1: {
            0: "**`В Вашем запросе есть странные слова...`**",
            1: "**`Вопрос:`**\n{0}\n**`OpenAI думает, что ответить...`**",
            2: "**`Ответ:`**\n{0}",
            3: "**`Извините, но эта команда не может быть использована в этом канале. Пожалуйста, попробуйте использовать её в обычном текстовом канале или ветке`**",
            4: "**`Системе не удалось ответить на Ваш вопрос`**",
            5: "**`При отправке ответа произошла ошибка`**"
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot
    
    # @slash_command(
    #     name="ask",
    #     description="Ask OpenAI anything",
    #     description_localizations={
    #         Locale.ru: "Спросить OpenAI о чём угодно"
    #     },
    #     dm_permission=False
    # )
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
        if not isinstance(channel := interaction.channel, (TextChannel, Thread)):
            await interaction.response.send_message(embed=Embed(description=self.openai_cog_text[lng][3]))
            return
        
        if words_filter.findall(question):
            await interaction.response.send_message(embed=Embed(description=self.openai_cog_text[lng][0]))
            return
        
        try:
            await interaction.response.send_message(embed=Embed(description=self.openai_cog_text[lng][1].format(question)))
        except Exception as ex:
            await write_one_log_async(
                "error.log",
                f"[FATAL] [ERROR] [could not response] [ask] [question: {question}] [guild: {interaction.guild_id}:{interaction.guild.name}] [{str(ex)}]\n"
            )
            await channel.send(embed=Embed(description=self.openai_cog_text[lng][4]))
            await interaction.response.defer()

        async with channel.typing():
            async with self.openai_lock:
                try:
                    response = openai.Completion.create(
                        model="text-davinci-003",
                        prompt=question,        
                        temperature=0.6,
                        max_tokens=1984,
                        top_p=1,
                        frequency_penalty=0.5,
                        presence_penalty=0.0
                    )
                except Exception as ex:
                    await write_one_log_async(
                        "error.log",
                        f"[FATAL] [ERROR] [ask] [question: {question}] [guild: {interaction.guild_id}:{interaction.guild.name}] [{str(ex)}]\n"
                    )
                    await interaction.followup.send(embed=Embed(description=self.openai_cog_text[lng][4]), ephemeral=True)
                    return

        answer: str = str(response.choices[0].text).strip('\n') # type: ignore
        try:
            if ((length := len(answer)) < 3900):
                await channel.send(embed=Embed(description=self.openai_cog_text[lng][2].format(answer)))
            else:
                await channel.send(embed=Embed(description=self.openai_cog_text[lng][2].format(answer[:3900])))
                for i in range(1, (length + 3899) // 3900 + 1):
                    if (ans_part := answer[(3900 * i):min(3900 * (i + 1), length)]):
                        await sleep(1.0)
                        await channel.send(embed=Embed(description=ans_part))
        except Exception as ex:
            await write_one_log_async(
                "error.log",
                f"[FATAL] [ERROR] [ask] [question: {question}] [answer: {answer}] [guild: {interaction.guild_id}:{interaction.guild.name}] [{str(ex)}]\n"
            )
            await interaction.followup.send(embed=Embed(description=self.openai_cog_text[lng][5]), ephemeral=True)
        else:
            await write_log_async(
                "openai_logs.log",
                f"member {interaction.user.id}:{interaction.user.name}",
                f"guild {interaction.guild_id}:{interaction.guild.name}",
                question,
                answer
            )


def setup(bot: StoreBot) -> None:
    bot.add_cog(OpenAICog(bot))
