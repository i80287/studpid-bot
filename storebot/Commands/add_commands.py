from sqlite3 import connect, Connection, Cursor
from contextlib import closing
from datetime import datetime

from nextcord import Embed, Emoji, Colour, SlashOption, Interaction, Status, slash_command, Locale
from nextcord.ext.commands import Bot, Cog

from Commands.parse_tools import ParseTools
from Variables.vars import path_to

text_slash = {
    0 : {
        0 : "Error",
        1 : "Help menu",
        2 : "Choose a category",
        3 : "Top members by level",
        4 : "Page 1 from ",
        5 : " place",
        6 : " level",
        7 : "Level info for {}",
        8 : "Level",
        9 : "Experience",
        10 : "Place in the rating",
        11 : "Emoji",
        12 : "**`Please, select emoji from any discord server where the bot is added`**",
        13 : "Information about the server",
        14 : "Server's id - ",
        15 : "**`Sorry, but you can't mute yourself`**",
        16 : "**`Mute-role isn't selected in the bot's settings`**",
        17 : "**`Bot doesn't have permission to manage roles on the server`**",
        18 : "**`Bot doesn't have permission to manage this role. Bot's role should be higher than this role`**",
        19 : "**`Selected in the bot's settings mute-role hasn't been found on the server`**",
        20 : "Member was muted",
        21 : "**`You gave timeout to the `**{}\n**`for {} hours, {} minutes, {} seconds`**",
        #22 : "**`Member `**{}**` already has mute-role`**",
        #23 : "Current mute-role",
        #24 : "**`Selected in the settings mute-role: `**{}\n",
        #25 : "**`Selected mute-role: `**{}\n",
        #26 : "**`Mute-role was reseted`**",
        22 : "**`Bot can't mute selected member. Please, report server admin about that (for example, `**<@594845341484974100>**`)`**",
        23 : "Member was unmuted",
        24 : "**`You retracted timeout from the `**{}",
        27 : "Current ignored channels",
        28 : "**`No channel was selected`**",
        29 : "{}**` was added to the list of ignored channels`**",
        30 : "{}**` already in the list of ignored channels`**",
        31 : "{}**` was removed from the list of ignored channels`**",
        32 : "**`Channel `**{}**` wasn't found in the list of ignored channels`**",
        33 : "Current notification channel",
        34 : "**`No notification channel was selected`**",
        35 : "**`Selected in the settings notification channel: `**{}\n",
        36 : "**`Selected notification channel: `**{}",
        37 : "**`Notification channel was reseted`**",
        38 : "**`This user not found on the server`**",
        39 : "**`Please, use correct arguments for command`**",
        40 : "**`This command not found`**",
        41 : "**`This user not found`**",
        42 : "**`This role not found`**",
        43 : "**`This channel not found`**",
        44 : "**`Please, wait before reusing this command`**",
        50 : "**`Sorry, but you don't have enough permissions to use this command`**",
        51 : "**`Default Discord emoji: `**{}",
    },
    1 : {
        0 : "Ошибка",
        1 : "Меню помощи",
        2 : "Выберите категорию",
        3 : "Топ пользователей по уровню",
        4 : "Страница 1 из ",
        5 : " место",
        6 : " уровень",
        7 : "Информация об уровне пользователя {}",
        8 : "Уровень",
        9 : "Опыт",
        10 : "Место в рейтинге",
        11 : "Эмодзи",
        12 : "**`Пожалуйста, укажите эмодзи с дискорд сервера, на котором есть бот`**",
        13 : "Информация о сервере",
        14 : "Id сервера - ",
        15 : "**`Извините, но Вы не можете замьютить самого себя`**",
        16 : "**`Мут-роль не выбрана в настройках сервера`**",
        17 : "**`У бота нет права управлять ролями на сервере`**",
        18 : "**`У бота нет прав управлять этой ролью. Роль бота должна быть выше, чем указанная Вами роль`**",
        19 : "**`Указанная в настройках бота мут-роль не найдена на сервере`**",
        20 : "Пользователь был замьючен",
        21 : "**`Вы выдали таймаут пользователю `**{}\n**`на {} часов, {} минут, {} секунд`**",
        #22 : "**`У пользователя `**{}**` уже есть мут-роль`**",
        #23 : "Текущая мут-роль",
        #24 : "**`Указанная в настройках мут-роль: `**{}\n",
        #25 : "**`Выбранная Вами мут-роль: `**{}",
        #26 : "**`Мут-роль была сброшена`**",
        22 : "**`Бот не может выдать таймаут пользователю. Пожалуйста, сообщите об этом админу (например, `**<@594845341484974100>**`)`**",
        23 : "Пользователь был размьючен",
        24 : "**`Вы сняли таймаут с `**{}",
        27 : "Текущие игнорируемые каналы",
        28 : "**`Не выбрано ни одного канала`**",
        29 : "{}**` был добавлен в список игнорируемых каналов`**",
        30 : "{}**` уже в списке игнорируемых каналов`**",
        31 : "{}**` был убран из списка игнорируемых каналов`**",
        32 : "{}**` нет в списке игнорируемых каналов`**",
        33 : "Текущий канал для оповещений",
        34 : "**`Не выбрано ни одного канала`**",
        35 : "**`Указанный в настройках канал: `**{}\n",
        36 : "**`Выбранный Вами канал: `**{}",
        37 : "**`Канал был сброшен`**",
        38 : "**`На сервере не найден такой пользователь`**",
        39 : "**`Пожалуйста, укажите верные аргументы команды`**",
        40 : "**`Такая команда не найдена`**",
        41 : "**`Такой пользователь не найден`**",
        42 : "**`Такая роль не найдена`**",
        43 : "**`Такой канал не найден`**",
        44 : "**`Пожалуйста, подождите перед повторным использованием команды`**",
        50 : "**`Извините, но у Вас недостаточно прав для использования этой команды`**",
        51 : "**`Дефолтное эмодзи Дискорда: `**{}"
    }           
}        
        
sm = {
    0 : {
        0 : "Members' info",
        1 : "Users",
        2 : "Bots", 
        3 : "Total",
        4 : "Channels",
        5 : "Text channels",
        6 : "Voice channels",
        7 : "Total",
        8 : "Emojis and stickers",
        9 : "Emojis",
        10 : "Stickers",
        11 : "Total",
        12 : "Members' status",
        13 : "Online",
        14 : "Idle",
        15 : "Dnd",
        16 : "Offline",
        17 : "Creation date",
        18 : "Verification level",
        19 : "Files' size limit",
        20 : "Server's boosters and boost level"
    },
    1 : {
        0 : "Информация об участниках",
        1 : "Пользователей",
        2 : "Ботов",
        3 : "Всего",
        4 : "Каналы",
        5 : "Текстовых каналов",
        6 : "Голосовых каналов",
        7 : "Всего",
        8 : "Эмодзи и стикеры",
        9 : "Эмодзи",
        10 : "Стикеров",
        11 : "Всего",
        12 : "Статус участников",
        13 : "Онлайн",
        14 : "Неактивны",
        15 : "Не беспокоить",
        16 : "Оффлайн",
        17 : "Дата создания",
        18 : "Уровень верификации",
        19 : "Лимит размера загружаемых файлов",
        20 : "Бустеры сервера и уровень буста"
    }
}

emojis = [
    "👤", "<:bot:995804039000359043>", "<:sum:995804781006290974>",
    "<:text:995806008960094239>", "<:voice:995804037351997482>", "<:summ:995804781006290974>", 
    "<a:emoji:995806881048170518>", "<:sticker:995806680505921639>",  "<:summ:995804781006290974>",
    "<:online:995823257993363587>", "<:idle:995823256621813770>", "<:dnd:995823255199957032>", "<:offline:995823253878738944>"
]

months = {
    0 : ["January {}", "February {}", "Mart {}", "April {}", "May {}", "June {}", "Jule {}", "August {}", "September {}", "October {}", "November {}", "December {}"],
    1 : ["{} Января", "{} Февраля", "{} Марта", "{} Апреля", "{} Мая", "{} Июня", "{} Июля", "{} Августа", "{} Сентября", "{} Октября", "{} Ноября", "{} Декабря"]
}


class AdditionalCommandsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @staticmethod
    def check_user(base: Connection, cur: Cursor, memb_id: int):
        member = cur.execute('SELECT * FROM users WHERE memb_id = ?', (memb_id,)).fetchone()
        if not member:
            cur.execute('INSERT INTO users(memb_id, money, owned_roles, work_date, xp) VALUES(?, ?, ?, ?, ?)', (memb_id, 0, "", 0, 0))
            base.commit()
        else:
            if member[1] is None or member[1] < 0:
                cur.execute('UPDATE users SET money = ? WHERE memb_id = ?', (0, memb_id))
                base.commit()
            if member[2] is None:
                cur.execute('UPDATE users SET owned_roles = ? WHERE memb_id = ?', ("", memb_id))
                base.commit()
            if member[3] is None:
                cur.execute('UPDATE users SET work_date = ? WHERE memb_id = ?', (0, memb_id))
                base.commit()
            if member[4] is None:
                cur.execute('UPDATE users SET xp = ? WHERE memb_id = ?', (0, memb_id))
                base.commit()

    
    @slash_command(
        name="emoji", 
        description="Fetchs emoji's png and url",
        description_localizations={
            Locale.ru : "Показывает png и url эмодзи"
        }
    )
    async def emoji(
        self, 
        interaction: Interaction, 
        emoji_str: str = SlashOption(
            name="emoji",
            description="Select emoji or it's id from any discord server, where bot is added", 
            description_localizations={
                Locale.ru: "Выберите эмодзи или его id c любого дискорд сервера, где есть бот"
            },
            required=True
        )
    ):
        lng = 1 if "ru" in interaction.locale else 0
        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                AdditionalCommandsCog.check_user(base=base, cur=cur, memb_id=interaction.user.id)
        
        emoji = ParseTools.parse_emoji(self.bot, emoji_str)        
        if emoji is None:
            emb = Embed(title=text_slash[lng][0], colour=Colour.red(), description=text_slash[lng][12])
            await interaction.response.send_message(embed=emb, ephemeral=True)
        elif isinstance(emoji, Emoji):
            emoji_url = emoji.url + "?quality=lossless"
            emoji_str = emoji.__str__()
            created_at: str = emoji.created_at.strftime("%d/%m/%Y, %H:%M:%S")
            emb = Embed(
                title=text_slash[lng][11], 
                description=f"**`Emoji:`** {emoji_str}\n\
                            **`Raw string:`** \{emoji_str}\n\
                            **`Emoji id:`** {emoji.id}\n\
                            **`Created at:`** {created_at}\n\
                            **`URL:`** {emoji_url}"
            )
            emb.set_image(url=emoji_url)
            await interaction.response.send_message(embed=emb)
        else:
            emb = Embed(description=text_slash[lng][51].format(emoji))
            await interaction.response.send_message(embed=emb)
    
    @slash_command(
        name="server",
        description="Shows an information about the server",
        description_localizations={
            Locale.ru : "Показывает информацию о сервере"
        }
    )
    async def server(self, interaction: Interaction):
        lng = 1 if "ru" in interaction.locale else 0

        with closing(connect(f"{path_to}/bases/bases_{interaction.guild_id}/{interaction.guild_id}.db")) as base:
            with closing(base.cursor()) as cur:
                AdditionalCommandsCog.check_user(base=base, cur=cur, memb_id=interaction.user.id)

        emb = Embed(title=text_slash[lng][13], colour=Colour.dark_purple())
        guild = interaction.guild

        onl = 0; idl = 0; dnd = 0; ofl = 0

        for m in guild.members:
            st = m.status
            if st == Status.online:
                onl += 1
            elif st == Status.idle:
                idl += 1
            elif st == Status.dnd:
                dnd += 1
            else:
                ofl += 1

        ca = guild.created_at
        time = f"{ca.strftime('%Y-%m-%d %H:%M:%S')}\n{months[lng][ca.month-1].format(ca.day)}, {ca.year}"
        
        vls = [len(guild.humans), len(guild.bots), len(guild.text_channels), len(guild.voice_channels), len(guild.emojis), len(guild.stickers),
        time, guild.verification_level, guild.filesize_limit >> 20, f"`{len(guild.premium_subscribers)}` - `{guild.premium_tier}{text_slash[lng][6]}`"]

        if guild.icon != None:
            emb.set_thumbnail(url=guild.icon.url)
        lc_s = sm[lng]

        for i in (0,):
            emb.add_field(name=lc_s[i * 4], value=f"{emojis[i*3]}`{lc_s[i * 4 + 1]}` - `{vls[i * 2]}`\n{emojis[i*3+1]}`{lc_s[i * 4 + 2]}` - `{vls[i * 2 + 1]}`\
            \n{emojis[i*3+2]}`{lc_s[i * 4 + 3]}` - `{vls[i * 2] + vls[i * 2 + 1]}`")

        emb.add_field(name=lc_s[12], value=f"{emojis[9]}`{lc_s[13]}` - `{onl}`\n{emojis[10]}`{lc_s[14]}` - `{idl}`\n{emojis[11]}`{lc_s[15]}` - `{dnd}`\n{emojis[12]}`{lc_s[16]}` - `{ofl}`")

        for i in (1, 2):
            emb.add_field(name=lc_s[i * 4], value=f"{emojis[i*3]}`{lc_s[i * 4 + 1]}` - `{vls[i * 2]}`\n{emojis[i*3+1]}`{lc_s[i * 4 + 2]}` - `{vls[i * 2 + 1]}`\
            \n{emojis[i*3+2]}`{lc_s[i * 4 + 3]}` - `{vls[i * 2] + vls[i * 2 + 1]}`")
        
        for i in (17, 18):
            emb.add_field(name=lc_s[i], value=f"`{vls[i - 11]}`")

        emb.add_field(name=lc_s[19], value=f"`{vls[8]} mb`")
        emb.add_field(name=lc_s[20], value=vls[9])
        emb.set_footer(text=f"{text_slash[lng][14]}{guild.id}")

        await interaction.response.send_message(embed=emb)
    
def setup(bot: Bot):
    bot.add_cog(AdditionalCommandsCog(bot))
