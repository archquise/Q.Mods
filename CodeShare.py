# █▀▀▄   █▀▄▀█ █▀█ █▀▄ █▀
# ▀▀▀█ ▄ █ ▀ █ █▄█ █▄▀ ▄█

# #### Copyright (c) 2026 Archquise #####

# 💬 Contact: https://t.me/archquise
# 🔒 Licensed under the GNU AGPLv3.
# 📄 LICENSE: https://raw.githubusercontent.com/archquise/Q.Mods/main/LICENSE
# ---------------------------------------------------------------------------------
# Name: CodeShare
# Description: Uploads your code at the kmi.aeza.net (Pastebin and GitHub Gist alternative)
# Author: @quise_m
# ---------------------------------------------------------------------------------
# meta developer: @quise_m
# meta banner: https://raw.githubusercontent.com/archquise/qmods_meta/main/CodeShare.png
# requires: aiofiles
# ---------------------------------------------------------------------------------

import logging
from http import HTTPStatus
from pathlib import Path

import aiofiles
import aiohttp
from telethon.types import MessageMediaDocument

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class CodeShareMod(loader.Module):
    """Uploads your code at the kmi.aeza.net (Pastebin and GitHub Gist alternative)."""

    strings = {  # noqa: RUF012
        "name": "CodeShare",
        "invalid_args": "<emoji document_id=5854929766146118183>❌</emoji> There is no arguments or reply with a file, or they are invalid",
        "_cls_doc": "Uploads your code at the kmi.aeza.net (Pastebin and GitHub Gist alternative)",
        "link_ready": "<emoji document_id=5854762571659218443>✅</emoji> <b>Code uploaded! Link:</b> <code>{}</code>",
    }

    strings_ru = {  # noqa: RUF012
        "_cls_doc": "Загружает ваш код на kmi.aeza.net (альтернатива Pastebin и GitHub Gist)",
        "invalid_args": "<emoji document_id=5854929766146118183>❌</emoji> Нет аргументов или реплая с файлом, или они неверны",
        "link_ready": "<emoji document_id=5854762571659218443>✅</emoji> <b>Код загружен! Ссылка:</b> <code>{}</code>",
    }

    async def upload_to_kmi(self, content: str) -> str:
        """Upload text to kmi.aeza.net."""
        url = "https://kmi.aeza.net"
        data = aiohttp.FormData()
        data.add_field("kmi", content)

        async with (
            aiohttp.ClientSession() as session,
            session.post(url, data=data) as response,
        ):
            if response.status == HTTPStatus.OK:
                return await response.text()
            logger.error("Error occurred! Status code: %s", response.status)
            return None

    @loader.command(
        ru_doc="Загрузка кода на сайт",
        en_doc="Upload code to the site",
    )
    async def codesharecmd(self, message) -> None:  # noqa: ANN001, D102
        args = utils.get_args(message)
        reply = await message.get_reply_message()
        if args:
            async with (
                aiohttp.ClientSession() as session,
                session.get(args[0]) as response,
            ):
                if response.status == HTTPStatus.OK:
                    content = await response.text()
                    link = await self.upload_to_kmi(content)
                    await utils.answer(message, self.strings["link_ready"].format(link))
                    return
                logger.error("Error occurred! Status code: %s", response.status)
                return
        if reply and isinstance(reply.media, MessageMediaDocument):
            file_name = await reply.download_media()
            async with aiofiles.open(file_name) as f:
                content = await f.read()
            try:
                Path(file_name).unlink()
            except Exception as e:  # noqa: BLE001
                logger.warning(e)
            link = await self.upload_to_kmi(content)
            await utils.answer(message, self.strings["link_ready"].format(link))
            return
        await utils.answer(message, self.strings["invalid_args"])
