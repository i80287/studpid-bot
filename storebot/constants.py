from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import LiteralString

import pathlib
CWD_PATH: str = pathlib.Path(__file__).parent.resolve().__str__()
DB_PATH: str = CWD_PATH + "/bases/bases_{0}/{0}.db"
BANNED_WORDS: LiteralString = r"""
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
(у?[её]б[аул])|
(лох)|
(жоп)|
(даун)|
(идиот)|
(дур[ао])|
(прон)|
(порн)|
(секс)|
(трах)|
(пенис)|
(член)""".replace("\r\n", "").replace('\n', "")