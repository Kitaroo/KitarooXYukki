import random
from typing import Dict, List, Union

from pyrogram import filters
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import (CallbackQuery, InputMediaPhoto, Message)

from Yukki import BOT_ID, MUSIC_BOT_NAME, app, random_assistant
from Yukki.Database import get_assistant, save_assistant
from Yukki.Database import remove_active_chat
from Yukki.Utilities.assistant import get_assistant_details



def AssistantAdd(mystic):
    async def wrapper(_, message):
        _assistant = await get_assistant(message.chat.id, "assistant")
        if not _assistant:
            ran_ass = random.choice(random_assistant)
            assis = {
                "saveassistant": ran_ass,
            }
            await save_assistant(message.chat.id, "assistant", assis)
        else:
            ran_ass = _assistant["saveassistant"]
        if ran_ass not in random_assistant:
            ran_ass = random.choice(random_assistant)
            assis = {
                "saveassistant": ran_ass,
            }
            await save_assistant(message.chat.id, "assistant", assis)
        ASS_ID, ASS_NAME, ASS_USERNAME, ASS_ACC = await get_assistant_details(
            ran_ass
        )
        try:
            b = await app.get_chat_member(message.chat.id , ASS_ID) 
            if b.status == "banned":
                await app.unban_chat_member(message.chat.id, ASS_ID)
                invite_link = await app.export_chat_invite_link(message.chat.id)
                if "+" in invite_link:
                    kontol = (invite_link.replace("+", "")).split("t.me/")[1]
                    link_bokep = f"https://t.me/joinchat/{kontol}"
                await ASS_ACC.join_chat(link_bokep)
                await message.reply(f"{ASS_NAME} Berhasil Bergabung",) 
                await remove_active_chat(message.chat.id)
        except UserNotParticipant:
            try:
                invite_link = await app.export_chat_invite_link(message.chat.id)
                if "+" in invite_link:
                    kontol = (invite_link.replace("+", "")).split("t.me/")[1]
                    link_bokep = f"https://t.me/joinchat/{kontol}"
                await ASS_ACC.join_chat(link_bokep)
                await message.reply(f"{ASS_NAME} Berhasil Bergabung",) 
                await remove_active_chat(message.chat.id)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await message.reply_text(
                        f"""
**Asisten Gagal Bergabung**
**Alasan**:{e}
"""
                    )
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            return await message.reply_text(
                f"""
**Asisten Gagal Bergabung**
**Alasan**:{e}
"""
                )
            return
        return await mystic(_, message)

    return wrapper
