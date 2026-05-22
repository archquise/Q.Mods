__version__ = (1, 1, 4)

# █▀▀▄   █▀▄▀█ █▀█ █▀▄ █▀
# ▀▀▀█ ▄ █ ▀ █ █▄█ █▄▀ ▄█

# #### Copyright (c) 2026 Archquise #####

# 💬 Contact: https://t.me/archquise
# 🔒 Licensed under the GNU AGPLv3.
# 📄 LICENSE: https://raw.githubusercontent.com/archquise/Q.Mods/main/LICENSE
# ---------------------------------------------------------------------------------
# Name: QNotes
# Description: A notes module that just works
# Author: @quise_m
# ---------------------------------------------------------------------------------
# meta developer: @quise_m
# meta banner: https://raw.githubusercontent.com/archquise/qmods_meta/main/qnotes.png
# ---------------------------------------------------------------------------------

import logging
import re
import asyncio

from typing import cast
from datetime import date

from heroku import loader, utils

from herokutl.tl.functions.users import GetUsersRequest
from herokutl.tl.types import InputUserSelf

logger = logging.getLogger(__name__)


@loader.tds
class QNotes(loader.Module):
    """A notes module that just works\nUsage: #notetag in any chat"""

    strings = {
        "name": "QNotes",
        "topic_desc": "Stores your notes content\nUsage: #notetag in any chat",
        "wrongargs": "<emoji document_id=5980953710157632545>❌</emoji> <b>Wrong arguments. Check command usage.</b>",
        "not_exist": "There is no such note!",
        "no_reply": "No reply! Reply to the message, which text will become a note.",
        "already_exists": "Seems like note with the same tag already exists. Overwrite?",
        "show_note_inline": "<blockquote>#{}</blockquote>\n\n<blockquote>{}</blockquote>",
        "notelist": "Note list:",
        "msg_not_found_inline": "Message with this note wasn't found. Probably, it was been removed. Note has been removed from the database.",
        "remnote_inline": "🗑 Remove",
        "close_inline": "❌ Close",
        "yes": "✔️ Yes",
        "no": "❌ No",
        "true": "yes",
        "false": "no",
        "saved": "Note saved!",
        "removed": "Note removed!",
        "nonotes": "You don't have any notes!",
        "privacy_switch": "Determines whose data will be used by the my_* placeholders\n\nTrue - the account that is issuing the note\nFalse - the account on which the userbot is running",
        "placeholders": """
        <b>Available placeholders</b>:

        about the account on which userbot is installed:
        {my_id} - ID
        @{my_username} - username, tag
        {my_phone} - phone number
        {my_premium} - premium status (yes/no)

        about reply author:
        {reply_id} - ID
        {reply_name} - name
        {reply_surname} - surname
        {reply_fullname} - full name (name + surname (if specified))
        @{reply_username} - username, tag
        {reply_phone} - phone number (if not hidden)
        {reply_premium} - premium status (yes/no)

        general:
        {today} - current date
        """,
    }

    strings_ru = {
        "_cls_doc": "Модуль для заметок, который просто работает\nИспользование: #тегзаметки в любом чате",
        "topic_desc": "Хранит содержимое ваших заметок\nИспользование: #тегзаметки в любом чате",
        "wrongargs": "<emoji document_id=5980953710157632545>❌</emoji> <b>Неверные аргументы. Проверьте использование команды.</b>",
        "no_reply": "Нет реплая! Ответьте на сообщение, текст которого станет заметкой.",
        "not_exist": "Такой заметки не найдено!",
        "already_exists": "Кажется, заметка с таким тегом уже существует. Перезаписать?",
        "show_note_inline": "<blockquote>#{}</blockquote>\n\n<blockquote>{}</blockquote>",
        "notelist": "Список заметок:",
        "msg_not_found_inline": "Сообщение с этой заметкой не было найдено. Вероятно, оно было удалено. Заметка очищена из базы данных.",
        "remnote_inline": "🗑 Удалить",
        "close_inline": "❌ Закрыть",
        "yes": "✔️ Да",
        "no": "❌ Нет",
        "saved": "Заметка сохранена!",
        "removed": "Заметка удалена!",
        "true": "да",
        "false": "нет",
        "nonotes": "Нет заметок!",
        "privacy_switch": "Влияет на то, чьи данные будут использовать my_* плейсхолдеры\n\nTrue - аккаунта, который вызывает заметку\nFalse - аккаунта на котором стоит юзербот",
        "placeholders": """
        <b>Доступные плейсхолдеры</b>:
    
        об аккаунте, на котором стоит юзербот:
        {my_id} - айди
        @{my_username} - юзернейм, тег
        {my_phone} - номер телефона
        {my_premium} - статус премиум (да/нет)

        об авторе реплая:
        {reply_id} - айди
        {reply_name} - имя
        {reply_surname} - фамилия
        {reply_fullname} - полное имя (имя + фамилия (если указана))
        @{reply_username} - юзернейм, тег
        {reply_phone} - номер телефона (если не скрыт)
        {reply_premium} - статус премиум (да/нет)

        общее:
        {today} - текущая дата
        """,
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "privacy_switch",
                True,
                lambda: self.strings["privacy_switch"],
                validator=loader.validators.Boolean(),  # type: ignore
            )
        )

    async def client_ready(self, client, db):  # type: ignore
        self._content_channel_id = await utils.wait_for_content_channel(self._db)
        self._notes_topic = await utils.asset_forum_topic(
            client=self._client,
            db=self._db,
            peer=self._content_channel_id,  # type: ignore
            title="QNotes | Storage",
            description=self.strings["topic_desc"],
            icon_emoji_id=5272001961326049733,
        )

        self.my_phone = (await self._client(GetUsersRequest(id=[InputUserSelf()])))[
            0
        ].phone

        self.placeholders = {
            "my_phone": self.my_phone,
            "my_username": self._client.heroku_me.username,
            "my_id": self.tg_id,
            "my_premium": self.strings["true"]
            if self._client.heroku_me.premium
            else self.strings["false"],
        }

        self._notemap = cast(dict, self.pointer("notemap", default={}))

    async def _ask_overwrite(self, message):

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        form = await self.inline.form(
            self.strings["already_exists"],
            message=message,
            reply_markup=[
                [
                    {
                        "text": self.strings["yes"],
                        "callback": (
                            lambda call, flag: (
                                future.set_result(flag) if not future.done() else None
                            )
                        ),
                        "args": (True,),
                    },
                    {
                        "text": self.strings["no"],
                        "callback": (
                            lambda call, flag: (
                                future.set_result(flag) if not future.done() else None
                            )
                        ),
                        "args": (False,),
                    },
                ]
            ],
        )

        try:
            async with asyncio.timeout(15):
                overwrite_answer = await future
        except TimeoutError:
            await form.delete()  # type: ignore
            return False, message

        if not overwrite_answer:
            await form.delete()  # type: ignore
            return False, form

        return True, form

    async def _show_note_inline(self, call, note, page=0):
        async def _remnote(call, notetag, note_msg):
            await note_msg.delete()
            self._notemap.pop(notetag, None)

            await call.edit(self.strings["removed"])

        note_msg = await self._client.get_messages(
            self._content_channel_id, ids=note[1]
        )

        if not note_msg:
            self._notemap.pop(note[0], None)

            await call.edit(
                self.strings["msg_not_found_inline"],
                reply_markup=[
                    {"text": "⬅️ Назад", "callback": self._list_page, "args": (page,)},
                    {"text": self.strings["close_inline"], "action": "close"},
                ],
            )
            return

        await call.edit(
            self.strings["show_note_inline"].format(note[0], note_msg.text),  # type: ignore
            reply_markup=[
                [
                    {"text": "⬅️ Назад", "callback": self._list_page, "args": (page,)},
                    {
                        "text": self.strings["remnote_inline"],
                        "callback": _remnote,
                        "args": (note[0], note_msg),
                    },
                ],
                [{"text": self.strings["close_inline"], "action": "close"}],
            ],
        )

    def _build_list_markup(self, page: int):
        items = list(self._notemap.items())
        total = -(-len(items) // 3)
        page = max(0, min(page, total - 1))
        rows = [
            [
                {
                    "text": notetag,
                    "callback": self._show_note_inline,
                    "args": ([notetag, msg_id], page),
                }
            ]
            for notetag, msg_id in items[page * 3 : (page + 1) * 3]
        ]
        return (
            rows
            + self.inline.build_pagination(
                callback=self._list_page,  # type: ignore
                total_pages=total,
                current_page=page + 1,
            )
            + [[{"text": self.strings["close_inline"], "action": "close"}]]
        )

    async def _list_page(self, call, page):
        await call.edit(
            text=self.strings["notelist"], reply_markup=self._build_list_markup(page)
        )

    @loader.command(
        ru_doc="Сохраняет заметку под тегом | Пример: .qnsave заметка",
        en_doc="Saves note by tag | Example: .qnsave note",
    )
    async def qnsave(self, message) -> None:
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings["wrongargs"])
            return

        current_message = message

        if not (reply := await message.get_reply_message()):
            await utils.answer(message, self.strings["no_reply"])
            return
        try:
            if args[0].strip() in self._notemap:
                need_overwrite, msg = await self._ask_overwrite(message)
                if not need_overwrite:
                    return
                old_note_message = await self._client.get_messages(
                    self._content_channel_id,
                    ids=self._notemap[args[0].strip()],
                )
                old_note_message and await old_note_message.delete()  # type: ignore
                current_message = msg

            note_message = await self._client.send_message(
                self._content_channel_id, reply.text, reply_to=self._notes_topic.id
            )
            self._notemap[args[0].strip()] = note_message.id

        except Exception as e:
            await utils.answer(current_message, f"Произошла ошибка: {e}")
            logger.exception("Произошла ошибка при сохранении заметки!")
            return
        await utils.answer(current_message, self.strings["saved"])

    @loader.command(
        ru_doc="Удаляет заметку по тегу | Пример: .qnrem заметка",
        en_doc="Removes note by tag | Example: .qnrem note",
    )
    async def qnrem(self, message) -> None:
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings["wrongargs"])
            return

        if args[0] not in self._notemap or not (
            note_message := await self._client.get_messages(
                self._content_channel_id,
                ids=self._notemap[args[0]],
            )
        ):
            await utils.answer(message, self.strings["not_exist"])
            return

        await note_message.delete()  # type: ignore
        self._notemap.pop(args[0], None)

        await utils.answer(message, self.strings["removed"])

    @loader.command(
        ru_doc="Выводит список всех заметок и позволяет управлять ими",
        en_doc="Shows note list and allows managing them",
    )
    async def qnlist(self, message) -> None:
        if self._notemap:
            await self.inline.form(
                text=self.strings["notelist"],
                reply_markup=self._build_list_markup(0),
                message=message,
            )
            return
        await utils.answer(message, self.strings["nonotes"])

    @loader.command(
        ru_doc="Выводит список доступных плейсхолдеров",
        en_doc="Displays a list of available placeholders",
    )
    async def qnp(self, message) -> None:
        await utils.answer(message, self.strings["placeholders"])

    @loader.watcher(startswith="#")
    async def _note_watcher(self, message):
        if not (
            await self._client.dispatcher.security.check(message, self._note_watcher)
        ):
            return

        notetag = message.text.split("#", maxsplit=1)[1]

        if notetag in self._notemap:
            if not (
                note_message := await self._client.get_messages(
                    self._content_channel_id,
                    ids=self._notemap[notetag],
                )
            ):
                self._notemap.pop(notetag, None)
                return
            notetext = note_message.text or ""  # type: ignore
            if re.search(r"\{\w+\}", notetext):
                if (
                    not self.config["privacy_switch"]
                    or message.sender_id == self._client.heroku_me.id
                ):
                    placeholders = {**self.placeholders}
                else:
                    message_author_entity = await self._client.get_entity(
                        message.sender_id
                    )
                    placeholders = {
                        "my_phone": (
                            await self._client(GetUsersRequest(id=[message.sender_id]))
                        )[0].phone,
                        "my_username": message_author_entity.username,
                        "my_id": message.sender_id,
                        "my_premium": self.strings["true"]
                        if message_author_entity.premium
                        else self.strings["false"],
                    }

                if reply_msg := await message.get_reply_message():
                    reply_user = await self._client.get_entity(reply_msg.sender_id)
                    placeholders = {
                        **placeholders,
                        "reply_id": reply_user.id,
                        "reply_fullname": " ".join(
                            filter(None, [reply_user.first_name, reply_user.last_name])
                        ),
                        "reply_name": reply_user.first_name,
                        "reply_surname": reply_user.last_name,
                        "reply_phone": (
                            await self._client(GetUsersRequest(id=[reply_user.id]))
                        )[0].phone,
                        "reply_username": reply_user.username,
                        "reply_premium": self.strings["true"]
                        if reply_user.premium
                        else self.strings["false"],
                    }

                placeholders = placeholders | {"today": date.today()}

                def replacer(match):
                    key = match.group(1)
                    if key not in placeholders or not placeholders[key]:
                        return match.group(0)
                    return utils.escape_html(str(placeholders[key]))

                notetext = re.sub(r"\{(\w+)\}", replacer, notetext)
            await utils.answer(message, notetext)
            return
