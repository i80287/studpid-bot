from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Literal, Optional, List, Any, Dict, Iterator
    from collections.abc import Iterable, Sequence

    from nextcord.member import Member
    from nextcord.types.snowflake import Snowflake
    from nextcord.mentions import AllowedMentions
    from nextcord.message import Attachment
    from nextcord.guild import Guild
    from nextcord.embeds import Embed
    from nextcord.role import Role
    from nextcord.ui import View
    from nextcord.state import ConnectionState
    from nextcord.http import HTTPClient, Route, Response

import asyncio
import aiohttp

from nextcord import utils
from nextcord.file import File
from nextcord.flags import ApplicationFlags
from nextcord.types.emoji import Emoji as EmojiPayload
from nextcord.enums import InteractionType
from nextcord.interactions import Interaction
from nextcord.user import ClientUser
from nextcord.interactions import InteractionResponse, _InteractionMessageState, PartialInteractionMessage, InteractionMessage
from nextcord.errors import InteractionResponded, InvalidArgument
from nextcord.types.guild import Guild as GuildPayloads
from nextcord.types.role import Role as RolePayloads
from nextcord.types.interactions import Interaction as InteractionPayLoads, ApplicationCommandInteractionData
from nextcord.types.member import Member as MemberPayLoads
from nextcord.types.user import User as UserPayloads
from nextcord.webhook.async_ import handle_message_parameters, async_context, MISSING
from nextcord.gateway import DiscordClientWebSocketResponse

from storebot.storebot import StoreBot

USER_ID: Literal[324902349023] = 324902349023
USER_USERNAME: Literal['3384924892304'] = "3384924892304"
USER_DISCRIMINATOR: Literal['3384'] = "3384"
USER_EMAIL: Literal['abc@nextcord.org'] = "abc@nextcord.org"

APPLICATION_ID: Literal[234234234] = 234234234
GUILD_ID: Literal[12345678] = 12345678
GUILD_NAME: Literal['92384943589'] = "92384943589"
GUILD_OWNER_ID: Literal[23480234] = 23480234
GUILD_AFK_CHANNEL_ID: Literal[2342390940] = 2342390940
GUILD_AFK_TIMEOUT: Literal[32348] = 32348
GUILD_SYSTEM_CHANNEL_ID: Literal[5943004505] = 5943004505
GUILD_SYSTEM_CHANNEL_FLAGS: Literal[0b10101] = 0b10101
GUILD_RULES_CHANNEL_ID: Literal[3218990234] = 3218990234
GUILD_PUBLIC_UPDATES_CHANNEL_ID: Literal[32982394089] = 32982394089

GUILD_ROLES_COLOR: Literal[42] = 42
GUILD_ROLES_PERMISSIONS: Literal['2199023255551'] = str((1 << 41) - 1) # type: ignore
GUILD_ROLES_COUNT: Literal[16] = 16
GUILD_ROLES_IDS: list[int] = [GUILD_ID] + [i << 32 for i in range(1, GUILD_ROLES_COUNT)]
GUILD_ROLES_NAMES: list[str] = ["@everyone"] + ["role {0}".format(i) for i in range(1, GUILD_ROLES_COUNT)]

GUILD_MEMBER_AVATAR: Literal['https://unix.png'] = "https://unix.png"
GUILD_MEMBER_NICK: Literal['3423989072384'] = "3423989072384"
GUILD_MEMBER_ROLES: list[int | str]
GUILD_MEMBER_ROLES_COUNT: Literal[4] = 4

INTERACTION_ID: Literal[3298900234] = 3298900234
INTERACTION_TOKEN: Literal['1248F'] = "1248F"
INTERACTION_TYPE: Literal[2] = InteractionType.application_command.value
INTERACTION_VERSION: Literal[1] = 1
APPLICATION_COMMAND_ID: Literal[8930489329] = 8930489329
APPLICATION_COMMAND_NAME: Literal['testcmd'] = "testcmd"
INTERACTION_CHANNEL_ID: Literal[328293489023] = 328293489023
GUILD_MEMBER_LOCALE: Literal['en-US'] = "en-US"
GUILD_LOCALE: Literal['en-US'] = "en-US"

BOT_ID: Literal[8054885002459] = 8054885002459
BOT_NAME: Literal['storebot'] = "storebot"
BOT_DISCRIMINATOR: Literal['8054'] = "8054"

views_queue: asyncio.Queue[View] = asyncio.Queue()

guild_roles_ids: Iterator[int] = iter(GUILD_ROLES_IDS)
guild_roles_names: Iterator[str] = iter(GUILD_ROLES_NAMES)
guild_roles_positions: Iterator[int] = iter(range(1, GUILD_ROLES_COUNT + 1))

dummy_roles_payloads: list[RolePayloads] = [
    RolePayloads(
        id=next(guild_roles_ids),
        name=next(guild_roles_names),
        color=GUILD_ROLES_COLOR,
        hoist=True,
        position=next(guild_roles_positions),
        permissions=GUILD_ROLES_PERMISSIONS,
        managed=False,
        mentionable=True
    ) for _ in range(GUILD_ROLES_COUNT)
]

GUILD_MEMBER_ROLES: list[int | str] = [role["id"] for role in dummy_roles_payloads[1:GUILD_MEMBER_ROLES_COUNT + 1]] # skip @everyone role

GUILD_EMOJI_ID: Literal[485998304] = 485998304
GUILD_EMOJI_NAME = "emojiName"
GUILD_EMOJI_ROLES: list[int | str] = [role["id"] for role in dummy_roles_payloads]

user_payloads: UserPayloads = UserPayloads(
    id=USER_ID,
    username=USER_USERNAME,
    discriminator=USER_DISCRIMINATOR,
    avatar=None,
    bot=False,
    system=False,
    mfa_enabled=False,
    verified=True,
    email=USER_EMAIL,
    premium_type=0
)

member_payloads: MemberPayLoads = MemberPayLoads(
    user=user_payloads,
    roles=GUILD_MEMBER_ROLES,
    joined_at="",
    deaf="",
    mute="",
    avatar=GUILD_MEMBER_AVATAR,
    nick=GUILD_MEMBER_NICK
)

bot_user_payloads: UserPayloads = UserPayloads(
    id=BOT_ID,
    username=BOT_NAME,
    discriminator=BOT_DISCRIMINATOR,
    avatar=None,
    bot=True,
    system=False,
    mfa_enabled=False,
    verified=False,
    email=None,
    premium_type=0
)

bot_member_payloads: MemberPayLoads = MemberPayLoads(
    user=bot_user_payloads,
    roles=[],
    joined_at="",
    deaf="",
    mute="",
    avatar="",
    nick=bot_user_payloads["username"],
    permissions=""
)

emoji_payload: EmojiPayload = EmojiPayload(
    id=GUILD_EMOJI_ID,
    name=GUILD_EMOJI_NAME,
    roles=GUILD_EMOJI_ROLES,
    user=user_payloads,
    require_colons=False,
    managed=True,
    animated=False,
    available=True
)

guild_payloads: GuildPayloads = GuildPayloads(
    id=GUILD_ID,
    name=GUILD_NAME,
    icon=None,
    splash=None,
    discovery_splash=None,
    emojis=[emoji_payload],
    features=[],
    description=None,
    owner_id=GUILD_OWNER_ID,
    region="str",
    afk_channel_id=GUILD_AFK_CHANNEL_ID,
    afk_timeout=GUILD_AFK_TIMEOUT,
    verification_level=0,
    default_message_notifications=0,
    explicit_content_filter=0,
    roles=dummy_roles_payloads,
    mfa_level=0,
    nsfw_level=0,
    application_id=APPLICATION_ID,
    system_channel_id=GUILD_SYSTEM_CHANNEL_ID,
    system_channel_flags=GUILD_SYSTEM_CHANNEL_FLAGS,
    rules_channel_id=GUILD_RULES_CHANNEL_ID,
    vanity_url_code=None,
    banner=None,
    premium_tier=0,
    preferred_locale="str",
    public_updates_channel_id=GUILD_PUBLIC_UPDATES_CHANNEL_ID,
    guild_scheduled_events=[],
    members=[member_payloads, bot_member_payloads]
)

bot: StoreBot = StoreBot()
conn_state: ConnectionState = bot._connection
data: dict[str, Any] = {
    "user": bot_user_payloads,
    "guilds": [guild_payloads]
}

# immitate conn_state.parse_ready(data)
if conn_state._ready_task is not None:
    conn_state._ready_task.cancel()

conn_state._ready_state = asyncio.Queue()
conn_state.clear(views=False)
conn_state.user = ClientUser(state=conn_state, data=data["user"])
conn_state.store_user(data["user"])

if conn_state.application_id is None:
    try:
        application = data["application"]
    except KeyError:
        pass
    else:
        conn_state.application_id = utils.get_as_snowflake(application, "id")
        # flags will always be present here
        conn_state.application_flags = ApplicationFlags._from_value(application["flags"])

for guild_data in data["guilds"]:
    conn_state._add_guild_from_data(guild_data)
# end immitate

http: HTTPClient = conn_state.http
http.__session = aiohttp.ClientSession(
    connector=http.connector,
    ws_response_class=DiscordClientWebSocketResponse
)
async def request(
    route: Route,
    *,
    files: Optional[Sequence[File]] = None,
    form: Optional[Iterable[Dict[str, Any]]] = None,
    **kwargs: Any,
) -> Any:
    return object()

http.request = request

guild: Guild = bot.guilds[0]
GUILD_ROLES: list[Role] = guild.roles

async def add_role(
    guild_id: Snowflake,
    user_id: Snowflake,
    role_id: Snowflake,
    *,
    reason: Optional[str] = None,
) -> Response[None]:
    _member: Member | None = guild.get_member(int(user_id))
    assert _member is not None
    _member._roles.add(int(role_id))

    return object() # type: ignore

http.add_role = add_role # type: ignore

async def remove_role(
    guild_id: Snowflake,
    user_id: Snowflake,
    role_id: Snowflake,
    *,
    reason: Optional[str] = None,
) -> Response[None]:
    _member: Member | None = guild.get_member(int(user_id))
    assert _member is not None
    _member._roles.remove(int(role_id))

    return object() # type: ignore

http.remove_role = remove_role # type: ignore

class DummyInteraction(Interaction):
    def __init__(self, *, data: InteractionPayLoads, state: ConnectionState) -> None:
        super().__init__(data=data, state=state)
        self.dummy_interaction_response: DummyInteractionResponse = DummyInteractionResponse(self)
        self.__payload: dict[str, Any] = {}
        self.__edit_payload: dict[str, Any] = {}

    @property
    def response(self) -> InteractionResponse:
        """:class:`InteractionResponse`: Returns an object responsible for handling responding to the interaction.

        A response can only be done once. If secondary messages need to be sent, consider using :attr:`followup`
        instead.
        """
        return self.dummy_interaction_response
    
    @property
    def payload(self) -> dict[str, Any]:
        return self.__payload

    @payload.setter
    def payload(self, value: dict[str, Any]) -> None:
        self.__payload = value
    
    @property
    def edit_payload(self) -> dict[str, Any]:
        return self.__edit_payload

    @edit_payload.setter
    def edit_payload(self, value: dict[str, Any]) -> None:
        self.__edit_payload = value

    async def edit_original_message(
        self,
        *,
        content: Optional[str] = MISSING,
        embeds: List[Embed] = MISSING,
        embed: Optional[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        attachments: List[Attachment] = MISSING,
        view: Optional[View] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> InteractionMessage:
        """|coro|

        Edits the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.edit` in case
        you do not want to fetch the message and save an HTTP request.

        This method is also the only way to edit the original message if
        the message sent was ephemeral.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content to edit the message with or ``None`` to clear it.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        file: :class:`File`
            The file to upload. This cannot be mixed with ``files`` parameter.
        files: List[:class:`File`]
            A list of files to send with the content. This cannot be mixed with the
            ``file`` parameter.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. To keep existing attachments,
            you must fetch the message with :meth:`original_message` and pass
            ``message.attachments`` to this parameter.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.
        view: Optional[:class:`~nextcord.ui.View`]
            The updated view to update this message with. If ``None`` is passed then
            the view is removed.

        Raises
        ------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        InvalidArgument
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``.
        ValueError
            The length of ``embeds`` was invalid.

        Returns
        -------
        :class:`InteractionMessage`
            The newly edited message.
        """

        previous_mentions: Optional[AllowedMentions] = self._state.allowed_mentions
        params = handle_message_parameters(
            content=content,
            file=file,
            files=files,
            attachments=attachments,
            embed=embed,
            embeds=embeds,
            view=view,
            allowed_mentions=allowed_mentions,
            previous_allowed_mentions=previous_mentions,
        )
        self.edit_payload = params.payload or {}

        adapter = async_context.get()

        # data = await adapter.edit_original_interaction_response(
        #     self.application_id,
        #     self.token,
        #     session=self._session,
        #     payload=params.payload,
        #     multipart=params.multipart,
        #     files=params.files,
        # )

        # # The message channel types should always match
        # message = InteractionMessage(state=self._state, channel=self.channel, data={})  # type: ignore
        # if view and not view.is_finished():
        #     self._state.store_view(view, message.id)
        
        # return message
        return None # type: ignore

class DummyInteractionResponse(InteractionResponse):
    def __init__(self, parent: DummyInteraction) -> None:
        super().__init__(parent)
    
    async def send_message(
        self,
        content: Optional[Any] = None,
        *,
        embed: Embed | None = None,
        embeds: List[Embed] | None = None,
        file: File | None = None,
        files: List[File] | None = None,
        view: View | None = None,
        tts: bool = False,
        ephemeral: bool = False,
        delete_after: Optional[float] = None,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> PartialInteractionMessage:
        if self._responded:
            raise InteractionResponded(self._parent)

        payload: Dict[str, Any] = {
            "tts": tts,
        }

        if embed is not None and embeds is not None:
            raise InvalidArgument("Cannot mix embed and embeds keyword arguments")

        if embed is not None:
            embeds = [embed]

        if embeds:
            payload["embeds"] = [e.to_dict() for e in embeds]

        if file is not None and files is not None:
            raise InvalidArgument("Cannot mix file and files keyword arguments")

        if file is not None:
            files = [file]

        if files and not all(isinstance(f, File) for f in files):
            raise TypeError("Files parameter must be a list of type File")

        if content is not None:
            payload["content"] = str(content)

        if ephemeral:
            payload["flags"] = 64

        if view is not None:
            payload["components"] = view.to_components()

        if allowed_mentions is None or allowed_mentions is None:
            if self._parent._state.allowed_mentions is not None:
                payload["allowed_mentions"] = self._parent._state.allowed_mentions.to_dict()
        else:
            if self._parent._state.allowed_mentions is not None:
                payload["allowed_mentions"] = self._parent._state.allowed_mentions.merge(
                    allowed_mentions
                ).to_dict()
            else:
                payload["allowed_mentions"] = allowed_mentions.to_dict()

        
        if files:
            for file in files:
                file.close()

        if view is not None:
            if ephemeral and view.timeout is None:
                view.timeout = 15 * 60.0

            views_queue.put_nowait(view)
            self._parent._state.store_view(view)

        self._responded = True

        if delete_after is not None:
            await self._parent.delete_original_message(delay=delete_after)

        state: _InteractionMessageState = _InteractionMessageState(self._parent, self._parent._state)
        if isinstance(self._parent, DummyInteraction):
            self._parent.payload = payload

        return PartialInteractionMessage(state)

def build_interaction_payloads() -> InteractionPayLoads:
    return InteractionPayLoads(
        id=INTERACTION_ID,
        application_id=APPLICATION_ID,
        type=INTERACTION_TYPE,
        token=INTERACTION_TOKEN,
        version=INTERACTION_VERSION,
        data=ApplicationCommandInteractionData(
            id=APPLICATION_COMMAND_ID,
            name=APPLICATION_COMMAND_NAME,
            type=1
        ),
        guild_id=GUILD_ID,
        channel_id=INTERACTION_CHANNEL_ID,
        member=member_payloads,
        user=user_payloads,
        locale=GUILD_MEMBER_LOCALE,
        guild_locale=GUILD_LOCALE
    )
