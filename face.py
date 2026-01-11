# ###########█▀▀▄   █▀▄▀█ █▀█ █▀▄ █▀###########
# ###########▀▀▀█ ▄ █ ▀ █ █▄█ █▄▀ ▄█###########

# #### Copyright (c) 2026 Archquise #####

# 💬 Contact: https://t.me/archquise
# 🔒 Licensed under the GNU AGPLv3.
# 📄 LICENSE: https://raw.githubusercontent.com/archquise/Q.Mods/main/LICENSE
# ---------------------------------------------------------------------------------
# Name: face
# Description: Random face
# Author: @quise_m
# ---------------------------------------------------------------------------------
# meta developer: @quise_m
# meta banner: https://raw.githubusercontent.com/archquise/qmods_meta/main/face.png
# requires: aiohttp
# ---------------------------------------------------------------------------------

import logging

import aiohttp
import re
import random

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class face(loader.Module):
    """random face"""

    strings = {
        "name": "face",
        "loading": (
            "<emoji document_id=5348399448017871250>🔍</emoji> I'm looking for you kaomoji"
        ),
        "random_face": (
            "<emoji document_id=5208878706717636743>🗿</emoji> Here is your random one kaomoji\n<code>{}</code>"
        ),
        "error": "An error has occurred!",
    }

    strings_ru = {
        "loading": (
            "<emoji document_id=5348399448017871250>🔍</emoji> Ищю вам kaomoji"
        ),
        "random_face": (
            "<emoji document_id=5208878706717636743>🗿</emoji> Вот ваш рандомный kaomoji\n<code>{}</code>"
        ),
        "error": "Произошла ошибка!",
    }

    @loader.command(
        ru_doc="Рандом kaomoji",
        en_doc="Random kaomoji",
    )
    async def rfacecmd(self, message):
        await utils.answer(message, self.strings("loading"))

        url = "https://files.archquise.ru/kaomoji.txt"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.text()
                    kaomoji_list = [s.strip() for s in re.split(r'[\t\r\n]+', data) if s.strip()]
                    kaomoji = random.choice(kaomoji_list)
                    await utils.answer(
                        message, self.strings("random_face").format(kaomoji)
                    )
                else:
                    await utils.answer(message, self.strings("error"))
