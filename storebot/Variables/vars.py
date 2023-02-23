import os
CWD_PATH: str = os.getcwd()
BANNED_WORDS: str = r"""
(relig)|
(slave)|
(war)|
(blood)|
(traum)|
(violence)
(weapon)|
(kill)|
(dynamite)|
(bomb)|
(death)|
(dead)|
(terror)|
(destoy)|
(drug)|
(dirty old man)|
(down'?s? syndrome)|
(dwarf)|
(duffer)|
(hussy)|
(ass)|
(stupid)|
(fuck)|
(motherf[0-9a-z]*)|
(dick)|
(pron)|
(porn)|
(sex)|
(раб)|
(религ)|
(оруж)|
(кров[0-9a-z]+)|
(убит)|
(динамит)|
(бомб)|
(смерт)|
(терро)|
(войн)|
(разруш)|
(нарко)|
(пизд)|
([её]бл)|
(лох)|
(жоп)|
(даун)|
(идиот)|
(дур[ао])|
(прон)|
(порн)|
(секс)|
(пенис)|
(член)""".replace("\r\n", "").replace('\n', "")