from tests.dummy_variables import *

def get_guild() -> Guild:
    return guild

def get_bot() -> StoreBot:
    return bot

def get_test_role(member_has: bool = True) -> Role:
    return GUILD_ROLES[1] if member_has else GUILD_ROLES[GUILD_MEMBER_ROLES_COUNT + 1]

def build_interaction() -> DummyInteraction:
    dummy_interaction_payloads: InteractionPayLoads = build_interaction_payloads()
    return DummyInteraction(data=dummy_interaction_payloads, state=conn_state)
