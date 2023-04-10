from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from datetime import datetime
    from typing import Literal

    from nextcord import (
        Role,
        Guild,
    )
    from ..storebot import StoreBot

from nextcord import (
    User,
    Embed,
    Emoji,
    Colour,
    Member,
    SlashOption,
    Status,
    slash_command,
    Locale,
    Interaction,
    Permissions
)
from nextcord.ext.commands import Cog

from ..Modals.feedback import FeedbackModal
from ..Tools.db_commands import check_member_async
from ..Tools.parse_tools import parse_emoji


class AdditionalCommandsCog(Cog):
    text_slash: dict[int, dict[int, str]] = {
        0: {
            0: "Error",
            1: "Help menu",
            2: "Choose a category",
            3: "Top members by level",
            4: "Page 1 from ",
            5: " place",
            6: " level",
            7: "Level info for {}",
            8: "Level",
            9: "Experience",
            10: "Place in the rating",
            11: "Emoji",
            12: "**`Please, select emoji from any discord server where the bot is added`**",
            13: "Information about the server",
            14: "Server's id - ",
            15: "**`Sorry, but you can't mute yourself`**",
            16: "**`Mute-role isn't selected in the bot's settings`**",
            17: "**`Bot doesn't have permission to manage roles on the server`**",
            18: "**`Bot doesn't have permission to manage this role. Bot's role should be higher than this role`**",
            19: "**`Selected in the bot's settings mute-role hasn't been found on the server`**",
            20: "Member was muted",
            21: "**`You gave timeout to the `**{}\n**`for {} hours, {} minutes, {} seconds`**",
            #22: "**`Member `**{}**` already has mute-role`**",
            #23: "Current mute-role",
            #24: "**`Selected in the settings mute-role: `**{}\n",
            #25: "**`Selected mute-role: `**{}\n",
            #26: "**`Mute-role was reseted`**",
            22: "**`Bot can't mute selected member. Please, report server admin about that (for example, `**<@594845341484974100>**`)`**",
            23: "Member was unmuted",
            24: "**`You retracted timeout from the `**{}",
            27: "Current ignored channels",
            28: "**`No channel was selected`**",
            29: "{}**` was added to the list of ignored channels`**",
            30: "{}**` already in the list of ignored channels`**",
            31: "{}**` was removed from the list of ignored channels`**",
            32: "**`Channel `**{}**` wasn't found in the list of ignored channels`**",
            33: "Current notification channel",
            34: "**`No notification channel was selected`**",
            35: "**`Selected in the settings notification channel: `**{}\n",
            36: "**`Selected notification channel: `**{}",
            37: "**`Notification channel was reseted`**",
            38: "**`This user not found on the server`**",
            39: "**`Please, use correct arguments for command`**",
            40: "**`This command not found`**",
            41: "**`This user not found`**",
            42: "**`This role not found`**",
            43: "**`This channel not found`**",
            44: "**`Please, wait before reusing this command`**",
            50: "**`Sorry, but you don't have enough permissions to use this command`**",
            51: "**`Default Discord emoji: `**{}",
        },
        1: {
            0: "Ошибка",
            1: "Меню помощи",
            2: "Выберите категорию",
            3: "Топ пользователей по уровню",
            4: "Страница 1 из ",
            5: " место",
            6: " уровень",
            7: "Информация об уровне пользователя {}",
            8: "Уровень",
            9: "Опыт",
            10: "Место в рейтинге",
            11: "Эмодзи",
            12: "**`Пожалуйста, укажите эмодзи с дискорд сервера, на котором есть бот`**",
            13: "Информация о сервере",
            14: "Id сервера - ",
            15: "**`Извините, но Вы не можете замьютить самого себя`**",
            16: "**`Мут-роль не выбрана в настройках сервера`**",
            17: "**`У бота нет права управлять ролями на сервере`**",
            18: "**`У бота нет прав управлять этой ролью. Роль бота должна быть выше, чем указанная Вами роль`**",
            19: "**`Указанная в настройках бота мут-роль не найдена на сервере`**",
            20: "Пользователь был замьючен",
            21: "**`Вы выдали таймаут пользователю `**{}\n**`на {} часов, {} минут, {} секунд`**",
            #22: "**`У пользователя `**{}**` уже есть мут-роль`**",
            #23: "Текущая мут-роль",
            #24: "**`Указанная в настройках мут-роль: `**{}\n",
            #25: "**`Выбранная Вами мут-роль: `**{}",
            #26: "**`Мут-роль была сброшена`**",
            22: "**`Бот не может выдать таймаут пользователю. Пожалуйста, сообщите об этом админу (например, `**<@594845341484974100>**`)`**",
            23: "Пользователь был размьючен",
            24: "**`Вы сняли таймаут с `**{}",
            27: "Текущие игнорируемые каналы",
            28: "**`Не выбрано ни одного канала`**",
            29: "{}**` был добавлен в список игнорируемых каналов`**",
            30: "{}**` уже в списке игнорируемых каналов`**",
            31: "{}**` был убран из списка игнорируемых каналов`**",
            32: "{}**` нет в списке игнорируемых каналов`**",
            33: "Текущий канал для оповещений",
            34: "**`Не выбрано ни одного канала`**",
            35: "**`Указанный в настройках канал: `**{}\n",
            36: "**`Выбранный Вами канал: `**{}",
            37: "**`Канал был сброшен`**",
            38: "**`На сервере не найден такой пользователь`**",
            39: "**`Пожалуйста, укажите верные аргументы команды`**",
            40: "**`Такая команда не найдена`**",
            41: "**`Такой пользователь не найден`**",
            42: "**`Такая роль не найдена`**",
            43: "**`Такой канал не найден`**",
            44: "**`Пожалуйста, подождите перед повторным использованием команды`**",
            50: "**`Извините, но у Вас недостаточно прав для использования этой команды`**",
            51: "**`Дефолтное эмодзи Дискорда: `**{}"
        }
    }
    emojis: tuple[str, ...] = (
        "👤", "<:bot:995804039000359043>", "<:sum:995804781006290974>",
        "<:text:995806008960094239>", "<:voice:995804037351997482>", "<:summ:995804781006290974>", 
        "<a:emoji:995806881048170518>", "<:sticker:995806680505921639>",  "<:summ:995804781006290974>",
        "<:online:995823257993363587>", "<:idle:995823256621813770>", "<:dnd:995823255199957032>", "<:offline:995823253878738944>"
    )
    months: dict[int, tuple[str, ...]] = {
        0: ("January {}", "February {}", "Mart {}", "April {}", "May {}", "June {}", "Jule {}", "August {}", "September {}", "October {}", "November {}", "December {}"),
        1: ("{} Января", "{} Февраля", "{} Марта", "{} Апреля", "{} Мая", "{} Июня", "{} Июля", "{} Августа", "{} Сентября", "{} Октября", "{} Ноября", "{} Декабря")
    }
    server_info_text: dict[int, dict[int, str]] = {
        0: {
            0: "Members' info",
            1: "Users",
            2: "Bots", 
            3: "Total",
            4: "Channels",
            5: "Text channels",
            6: "Voice channels",
            7: "Total",
            8: "Emojis and stickers",
            9: "Emojis",
            10: "Stickers",
            11: "Total",
            12: "Members' status",
            13: "Online",
            14: "Idle",
            15: "Dnd",
            16: "Offline",
            17: "Creation date",
            18: "Verification level",
            19: "Files' size limit",
            20: "Server's boosters and boost level"
        },
        1: {
            0: "Информация об участниках",
            1: "Пользователей",
            2: "Ботов",
            3: "Всего",
            4: "Каналы",
            5: "Текстовых каналов",
            6: "Голосовых каналов",
            7: "Всего",
            8: "Эмодзи и стикеры",
            9: "Эмодзи",
            10: "Стикеров",
            11: "Всего",
            12: "Статус участников",
            13: "Онлайн",
            14: "Неактивны",
            15: "Не беспокоить",
            16: "Оффлайн",
            17: "Дата создания",
            18: "Уровень верификации",
            19: "Лимит размера загружаемых файлов",
            20: "Бустеры сервера и уровень буста"
        }
    }
    member_info_description_lines: dict[int, dict[int, str]] = {
        0: {
            0: "**User:** <@{0}> **`{0}`**",
            1: "**Pfp url is:** [Link to php]({0})",
            2: "**Creation date: `{0}`**",
            3: "**Join server at: `{0}`**",
            4: "**Nick on the server: `{0}`**",
            5: "**Status: `{0}`**",
            6: "**Status:** {0}",
            7: "**Activity: `{0}`**",
            8: "**`User is a bot`**",
            9: "**`User is not a bot`**",
            10: "**`Member's roles:`**"
        },
        1: {
            0: "**Пользователь:** <@{0}> **`{0}`**",
            1: "**URL аватарки:** [Ссылка]({0})",
            2: "**Дата создания: `{0}`**",
            3: "**Присоединился к серверу: `{0}`**",
            4: "**Ник на сервере: `{0}`**",
            5: "**Статус: `{0}`**",
            6: "**Статус:** {0}",
            7: "**Активность: `{0}`**",
            8: "**`Пользователь - бот`**",
            9: "**`Пользователь не бот`**",
            10: "**`Роли участника сервера:`**"
        }
    }
    u_ec_cmds: dict[int, tuple[tuple[str, str], ...]] = {
        0 : (
            ("`/store`", "Show store"),
            ("`/buy`", "Make a role purchase"),
            ("`/buy_by_number`", "Make a role purchase. Role is selected by number in the store"),
            ("`/sell`", "Sell the role"),
            ("`/sell_to`", "Sell the role to the selected member by selected price"),
            ("`/accept_request`", "Accept role purchase request made by another member for you"),
            ("`/decline_request`", "Decline role purchase request made by another member for you or delete you role sale request"),
            ("`/leaders`", "Show top members by balance/xp"),
            ("`/slots`", "Starts 'slots' game"),
            ("`/roulette`", "Starts 'roulette' game"),
        ),
        1 : (
            ("`/store`", "Открывает меню магазина"),
            ("`/buy`", "Совершает покупку роли"),
            ("`/buy_by_number`", "Совершает покупку роли. Роль выбирается по номеру из магазина."),
            ("`/sell`", "Совершает продажу роли"),
            ("`/sell_to`", "Создаёт запрос продажи роли указанному участнику за указанную цену"),
            ("`/accept_request`", "Принимает запрос покупки роли, сделанный Вам другим участником"),
            ("`/decline_request`", "Отклоняет запрос покупки роли, сделанный Вам другим участником, или отменяет Ваш запрос продажи роли"),
            ("`/leaders`", "Показывет топ пользователей по балансу/опыту"),
            ("`/slots`", "Начинает игру в 'слоты'"),
            ("`/roulette`", "Начинает игру в рулетку"),
        ),
    }
    u_pers_cmds: dict[int, tuple[tuple[str, str], ...]] = {
        0 : (
            ("`/profile`", "Show your profile"), 
            ("`/work`", "Start working, so you get salary"),
            ("`/collect`", "Same as `/work`"),
            ("`/transfer`", "Transfer money to another member"), 
            ("`/duel`", "Make a bet"),
        ),
        1 : (
            ("`/profile`", "Показывает меню Вашего профиля"), 
            ("`/work`", "Начинает работу, за которую Вы полчите заработок"),
            ("`/collect`", "То же, что и `/work`"),
            ("`/transfer`", "Совершает перевод валюты другому пользователю"), 
            ("`/duel`", "Делает ставку"),
        ),
    }
    u_other_cmds: dict[int, tuple[tuple[str, str], ...]] = {
        0 : (
            ("`/poll`", "Make a poll"), 
            ("`/server`", "Show information about the server"),
            ("`/emoji`", "Show information about the emoji"),
            ("`/ask`", "Asks OpenAI anything"),
            ("`/member_info`", "Shows information about selected member or command caller"),
            ("`/user_info`", "Shows brief information about any Discord user or command caller"),
        ),
        1 : (
            ("`/poll`", "Создаёт полл (опрос)"), 
            ("`/server`", "Показывает информацию о сервере"),
            ("`/emoji`", "Показывает информацию о эмодзи"),
            ("`/ask`", "Спрашивает OpenAI о чём угодно"),
            ("`/member_info`", "Показывает информацию о выбранном участнике сервера или участнике, вызвавшем команду"),
            ("`/user_info`", "Показывает краткую информацию о любом пользователе Дискорда или пользователе, вызвавшем команду"),
        )
    }
    m_cmds: dict[int, tuple[tuple[str, str], ...]] = {
        0 : (
            ("`/guide`", "Show guide about bot's system"), 
            ("`/settings`", "Call bot's settings menu"),
        ),
        1 : (
            ("`/guide`", "Показывает гайд о системе бота"), 
            ("`/settings`", "Вызывает меню настроек бота"),
        )
    }
    guide_text: dict[int, dict[int, str]] = {
        0 : {
            0 : "The guide",
            1 : "Economic operations with the roles",
            2 : "In order to make role able to be bought and sold on the server and it could bring money you should add it to the list of roles, available for the purchase/sale in the \
                menu **`/settings`** -> \"💰\" -> \"🛠️\". Also in this menu you can manage added roles",
            3 : "Bot devides roles on three types:",
            4 : "1, 2 and 3",
            5 : "Type 1",
            6 : "\"Nonstacking\" roles, that are not stacking in the store (are shown as different items in the store)",
            7 : "Type 2",
            8 : "\"Stacking\" roles that are stacking in the store (are shown as one item with quantity)",
            9 : "Type 3",
            10 : "\"Infinite\" roles that can't run out in the store (you can buy them endless times)",
            11 : "Salary of the roles",
            12 : "Each role can have passive salary: once per every cooldown time, set in the menu **`/settings`** -> \"💰\" -> \"🛠️\", members that have this role on their balance will \
                gain money (salary) that is selected in the menu **`/settings`** -> \"💰\" -> \"🛠️\"",
            13 : "Work",
            14 : "Members can gain money by using **`/work`** command. Amount of gained money is set in the menu **`/settings`** -> \"💰\" -> \"💹\". Cooldown \
                for the command is set in the menu **`/settings`** -> \"💰\" -> \"⏰\"",
            15 : "Rank system",
            16 : "For each message member gains amount of xp set in the menu **`/settings`** -> \"📈\" -> \"✨\" After achieving \"border\" of the level set in the menu \
                **`/settings`** -> \"📈\" -> \"✨\" member's level growths. For each new level bot can add role (and for old - remove, if new role is added) set in the menu \
                **`/settings`** -> \"📈\" -> \"🥇\" for each level separately",
            17 : "Money for messages",
            18 : "Besides the xp member can gain money for every message. Amount of money gained from message is set in the menu **`/settings`** -> \"💰\" -> \"💸\"\
                If you want to turn off this function you can make this value equal to 0",
            19 : "Polls",
            20 : "Members can create polls via **`/poll`**. They can be open/anonymous and have one/multiple choice. After creation poll will be posted in verification channel set \
                in the menu **`/settings`** -> \"📊\" -> \"🔎\". After being approved by moderator poll will be posted in channel for publishing polls set in the \
                menu **`/settings`** -> \"📊\" -> \"📰\""
        },
        1 : {
            0 : "Гайд",
            1 : "Экономические операции с ролями",
            2 : "Чтобы роль можно было покупать и продавать на сервере, а также она могла приносить заработок, нужно добавить её в список ролей, \
                доступных для покупки/продажи на сервере при помоши меню **`/settings`** -> \"💰\" -> \"🛠️\". В этом же меню можно и управлять добавленными ролями",
            3 : "Бот делит роли на 3 типа:",
            4 : "1, 2 и 3",
            5 : "Тип 1",
            6 : "\"Нестакающиеся\" роли, которые не стакаются в магазине (т.е. отображаются как отдельные товары)",
            7 : "Тип 2",
            8 : "\"Стакающиеся\" роли, которые стакаются в магазине (т.е. отображаются как один товар с указанным количеством)",
            9 : "Тип 3",
            10 : "\"Бесконечные\" роли, которые не заканчиваются в магазине (т.е. их можно купить бесконечное количество раз)",
            11 : "Заработок роли",
            12 : "Каждая роль может иметь пассивный заработок: раз в некоторое установленное время, установленное в меню **`/settings`** -> \"💰\" -> \"🛠️\", участники, на балансе \
                которых находится эта роль, получают заработок, установленный для каждой роли отдельно в меню **`/settings`** -> \"💰\" -> \"🛠️\"",
            13 : "Работа",
            14 : "Пользователи могут получать деньги за использование команды **`/work`**. Заработок от команды устанавливается в меню **`/settings`** -> \"💰\" -> \"💹\". Кулдаун команды \
                устанавливается в меню **`/settings`** -> \"💰\" -> \"⏰\"",
            15 : "Система рангов",
            16 : "За каждое сообщение на сервере пользователь получает количество опыта, установленное в меню **`/settings`** -> \"📈\" -> \"✨\" По достижении \"границы\" уровня, \
                установленной в меню **`/settings`** -> \"📈\" -> \"✨\", уровень пользователя повышается. За каждый новый уровень бот может выдавать роль (а за пройденный - снимать, \
                если выдана новая), установленную в меню **`/settings`** -> \"📈\" -> \"🥇\" для каждого уровня отдельно",
            17 : "Деньги за сообщения",
            18 : "За каждое сообщение пользователь получает не только опыт, но и деньги. Количество денег, получаемое за сообщение, устанавливается в меню **`/settings`** -> \"💰\" -> \"💸\"\
                Если Вы хотите отключить эту функцию, Вы можете установить это значение равным нулю",
            19 : "Поллы",
            20 : "Пользователи могут создавать поллы (опросы) при помощи **`/poll`**. Они могут быть открытыми/анонимными и содержать один или несколько вариантов выбора. После создания \
                полл будет отправлен на верификацию в канал, установленный в меню **`/settings`** -> \"📊\" -> \"🔎\". Если полл будет одобрен модератором, то он будет отправлен в \
                канал для публикаций, установленный в меню  **`/settings`** -> \"📊\" -> \"📰\""
        }
    }
    help_cmd_text: dict[int, dict[int, str]] = {
        0 : {
            0 : "User's commands",
            1 : "Mod's commands",
            2 : "Economy",
            3 : "Personal",
            4 : "Other",
        },
        1 : {
            0 : "Команды пользователей",
            1 : "Команды модераторов",
            2 : "Экономика",
            3 : "Персональные",
            4 : "Остальные",
        }
    }

    def __init__(self, bot: StoreBot) -> None:
        self.bot: StoreBot = bot
    
    @slash_command(
        name="emoji", 
        description="Fetchs emoji's info",
        description_localizations={
            Locale.ru: "Показывает информацию о эмодзи"
        },
        dm_permission=False
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
    ) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        await check_member_async(guild_id=interaction.guild_id, member_id=interaction.user.id)

        emoji: Emoji | str | None = parse_emoji(self.bot, emoji_str)        
        if emoji is None:
            emb: Embed = Embed(title=self.text_slash[lng][0], colour=Colour.red(), description=self.text_slash[lng][12])
            await interaction.response.send_message(embed=emb, ephemeral=True)
        elif isinstance(emoji, Emoji):
            emoji_url: str = emoji.url + "?quality=lossless"
            emoji_raw_str: str = emoji.__str__()
            created_at: str = emoji.created_at.strftime("%d/%m/%Y, %H:%M:%S")
            emb = Embed(
                title=self.text_slash[lng][11], 
                description=f"**`Emoji:`** {emoji_raw_str}\n\
**`Raw string:`** \\{emoji_raw_str}\n\
**`Emoji id:`** {emoji.id}\n\
**`Created at:`** {created_at}\n\
**`URL:`** {emoji_url}"
            )
            emb.set_image(url=emoji_url)
            await interaction.response.send_message(embed=emb)
        else:
            emb = Embed(description=self.text_slash[lng][51].format(emoji))
            await interaction.response.send_message(embed=emb)
    
    @slash_command(
        name="server",
        description="Shows an information about the server",
        description_localizations={
            Locale.ru: "Показывает информацию о сервере"
        },
        dm_permission=False
    )
    async def server(self, interaction: Interaction) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        await check_member_async(guild_id=interaction.guild_id, member_id=interaction.user.id)

        emb: Embed = Embed(title=self.text_slash[lng][13], colour=Colour.dark_purple())
        guild: Guild = interaction.guild

        onl: int = 0; idl: int = 0; dnd: int = 0; ofl: int = 0
        for m in guild.members:
            st: Status | str = m.status
            if st == Status.online:
                onl += 1
            elif st == Status.idle:
                idl += 1
            elif st == Status.dnd:
                dnd += 1
            else:
                ofl += 1

        ca: datetime = guild.created_at
        time: str = f"{ca.strftime('%Y-%m-%d %H:%M:%S')}\n{self.months[lng][ca.month-1].format(ca.day)}, {ca.year}"
        
        vls: list[int | str] = [len(guild.humans), len(guild.bots), len(guild.text_channels), len(guild.voice_channels), len(guild.emojis), len(guild.stickers),
        time, guild.verification_level, guild.filesize_limit >> 20, f"`{len(guild.premium_subscribers)}` - `{guild.premium_tier}{self.text_slash[lng][6]}`"]

        if guild.icon is not None:
            emb.set_thumbnail(url=guild.icon.url)
        
        lc_s: dict[int, str] = self.server_info_text[lng]
        i: int = 0
        emb.add_field(name=lc_s[i * 4], value=f"{self.emojis[i*3]}`{lc_s[i * 4 + 1]}` - `{vls[i * 2]}`\n{self.emojis[i*3+1]}`{lc_s[i * 4 + 2]}` - `{vls[i * 2 + 1]}`\n{self.emojis[i*3+2]}`{lc_s[i * 4 + 3]}` - `{vls[i * 2] + vls[i * 2 + 1]}`") # type: ignore

        emb.add_field(name=lc_s[12], value=f"{self.emojis[9]}`{lc_s[13]}` - `{onl}`\n{self.emojis[10]}`{lc_s[14]}` - `{idl}`\n{self.emojis[11]}`{lc_s[15]}` - `{dnd}`\n{self.emojis[12]}`{lc_s[16]}` - `{ofl}`")

        for i in (1, 2):
            emb.add_field(name=lc_s[i * 4], value=f"{self.emojis[i*3]}`{lc_s[i * 4 + 1]}` - `{vls[i * 2]}`\n{self.emojis[i*3+1]}`{lc_s[i * 4 + 2]}` - `{vls[i * 2 + 1]}`\n{self.emojis[i*3+2]}`{lc_s[i * 4 + 3]}` - `{vls[i * 2] + vls[i * 2 + 1]}`") # type: ignore
        
        for i in (17, 18):
            emb.add_field(name=lc_s[i], value=f"`{vls[i - 11]}`")

        emb.add_field(name=lc_s[19], value=f"`{vls[8]} mb`")
        emb.add_field(name=lc_s[20], value=vls[9])
        emb.set_footer(text=f"{self.text_slash[lng][14]}{guild.id}")

        await interaction.response.send_message(embed=emb)

    @slash_command(
        name="member_info",
        description="Shows info about server member",
        description_localizations={
            Locale.ru: "Показывает информацию об участнике сервера"
        },
        dm_permission=False
    )
    async def member_info(
        self,
        interaction: Interaction,
        member: Member | None = SlashOption(
            name="member",
            description="Member to show info about",
            description_localizations={
                Locale.ru: "Пользователь, о котором надо показать информацию"
            },
            required=False,
            default=None
        )
    ) -> None:
        assert interaction.guild_id is not None
        assert interaction.guild is not None
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        if not member:
            member = interaction.user
        
        if isinstance(member, User):
            await self.user_info(interaction, member)
            return

        member_id: int = member.id
        await check_member_async(guild_id=interaction.guild_id, member_id=member_id)
        info_description_lines: dict[int, str] = self.member_info_description_lines[lng]
        description_lines: list[str] = [
            info_description_lines[0].format(member_id),
            info_description_lines[1].format(member.display_avatar.url),
            info_description_lines[2].format(member.created_at.strftime("%d/%m/%Y %H:%M:%S"))
        ]
        if (joined_at := member.joined_at):
            description_lines.append(info_description_lines[3].format(joined_at.strftime('%d/%m/%Y %H:%M:%S')))
        description_lines.append(info_description_lines[4].format(member.display_name))
        if isinstance(status := member.status, Status):
            description_lines.append(info_description_lines[5].format(status))
        else:
            description_lines.append(info_description_lines[6].format(status))
        if (activities := member.activities):
            activity_report: str = info_description_lines[7]
            description_lines.extend(activity_report.format(name) for activity in activities if (name := activity.name))
        if member.bot:
            description_lines.append(info_description_lines[8])
        else:
            description_lines.append(info_description_lines[9])
        
        g: Guild = interaction.guild
        roles: list[Role] = sorted([role for role_id in member._roles if (role := g.get_role(role_id))])
        if roles:
            description_lines.append(info_description_lines[10])
            description_lines.extend("<@&" + str(role.id) + ">" for role in roles)
        
        emb: Embed = Embed(
            title=member.name + "#" + member.discriminator,
            description = '\n'.join(description_lines),
            colour = member.color
        )
        avatar_url: str = member.display_avatar.url
        emb.set_author(name=member.display_name, url=avatar_url, icon_url=avatar_url)
        emb.set_thumbnail(banner.url if (banner := member.banner) is not None else avatar_url)
        
        await interaction.response.send_message(embed=emb)
    
    @slash_command(
        name="user_info",
        description="Shows info about anu discord user",
        description_localizations={
            Locale.ru: "Показывает информацию о произвольном пользователе"
        },
        dm_permission=False
    )
    async def user_info(
        self,
        interaction: Interaction,
        user: User | None = SlashOption(
            name="user",
            description="User or user id to show info about",
            description_localizations={
                Locale.ru: "Пользователь или его id, о котором надо показать информацию"
            },
            required=False,
            default=None
        )
    ) -> None:
        assert interaction.locale is not None
        assert isinstance(interaction.user, Member)
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        if user is None:
            await self.member_info(interaction, interaction.user)
            return

        info_description_lines: dict[int, str] = self.member_info_description_lines[lng]
        user_id: int = user.id
        user_name: str = user.name
        avatar_url: str = user.display_avatar.url
        description_lines: list[str] = [
            info_description_lines[0].format(user_id),
            info_description_lines[1].format(avatar_url),
            info_description_lines[2].format(user.created_at.strftime("%d/%m/%Y %H:%M:%S"))
        ]
        description_lines.append(info_description_lines[8] if user.bot else info_description_lines[9])
        emb: Embed = Embed(
            title=user_name + "#" + user.discriminator,
            description='\n'.join(description_lines),
            colour=user.color
        )

        emb.set_author(name=user_name, url=avatar_url, icon_url=avatar_url)
        emb.set_thumbnail(banner.url if (banner := user.banner) is not None else avatar_url)

        await interaction.response.send_message(embed=emb)

    @slash_command(
        name="guide",
        description="show guide about bot's system",
        description_localizations={
            Locale.ru: "показывает гайд о системе бота"
        },
        dm_permission=False
    )
    async def guide(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        local_guide_text: dict[int, str] = self.guide_text[lng]
        emb: Embed = Embed(title=local_guide_text[0])
        for i in range(1, 20, 2):
            emb.add_field(name=local_guide_text[i], value=local_guide_text[i + 1], inline=False)
        await interaction.response.send_message(embed=emb)

    @slash_command(
        name="help", 
        description="Calls menu with commands",
        description_localizations={
            Locale.ru : "Вызывает меню команд"
        },
        dm_permission=False
    )
    async def help(self, interaction: Interaction) -> None:
        lng: Literal[1, 0] = 1 if "ru" in str(interaction.locale) else 0
        emb1: Embed = Embed(title=self.help_cmd_text[lng][0], description=self.help_cmd_text[lng][2])
        emb2: Embed = Embed(description=self.help_cmd_text[lng][3])
        emb3: Embed = Embed(description=self.help_cmd_text[lng][4])
        emb4: Embed = Embed(title=self.help_cmd_text[lng][1])
        for n, v in self.u_ec_cmds[lng]:
            emb1.add_field(name=n, value=v, inline=False)
        for n, v in self.u_pers_cmds[lng]:
            emb2.add_field(name=n, value=v, inline=False)
        for n, v in self.u_other_cmds[lng]:
            emb3.add_field(name=n, value=v, inline=False)
        for n, v in self.m_cmds[lng]:
            emb4.add_field(name=n, value=v, inline=False)
        await interaction.response.send_message(embeds=[emb1, emb2, emb3, emb4])

    @slash_command(
        name="feedback",
        description="Sends a feedback to the support server",
        description_localizations={
            Locale.ru: "Отправляет отзыв на сервер поддержки"
        },
        dm_permission=False,
        default_member_permissions=Permissions.administrator.flag
    )
    async def feedback(self, interaction: Interaction) -> None:
        assert interaction.user is not None
        assert interaction.locale is not None
        lng: Literal[1, 0] = 1 if "ru" in interaction.locale else 0
        feedback_modal: FeedbackModal = FeedbackModal(bot=self.bot, lng=lng, auth_id=interaction.user.id)
        await interaction.response.send_modal(modal=feedback_modal)

def setup(bot: StoreBot) -> None:
    bot.add_cog(AdditionalCommandsCog(bot))
