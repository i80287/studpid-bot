from .storebot import StoreBot

if __name__ == "__main__":
    bot: StoreBot = StoreBot()
    bot.load_extensions_from_module("storebot.Cogs")
    
    try:
        from .config import DEBUG
    except:
        from .config_example import DEBUG

    if DEBUG:
        from storebot.config import DEBUG_TOKEN
        bot.run(DEBUG_TOKEN)
    else:
        from storebot.config import TOKEN
        bot.run(TOKEN)