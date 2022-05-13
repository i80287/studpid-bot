import os
try:
    for filename in os.listdir("./shop/commands"):
         if filename.endswith(".py"):
            bot.load_extension(f"commands.{filename[:-3]}", extras={"prefix": prefix, "in_row": in_row, "currency": currency})
except Exception as e:
    f = open('er.txt', 'w')
    f.write(str(e))
    f.close()
