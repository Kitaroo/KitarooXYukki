from Yukki import BOT_USERNAME
from Yukki.Core.Clients.cli import app
from config import LOG_GROUP_ID


async def LOG_CHAT(message, what):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    mention = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    logger_text = f"""
**👤 Nama pengguna:** {mention}
**🆔 ID pengguna:** `{message.from_user.id}`
**📍 Username pengguna:** @{message.from_user.username}

**👤 Nama grup:** {message.chat.title} 
**🆔 ID grup:** `{message.chat.id}`
**📍 Username grup:** @{message.chat.username}

**🤖 Bot:** @{BOT_USERNAME}

**✨ Permintaan:** {message.text}"""
    await app.send_message(
        LOG_GROUP_ID, f"{logger_text}", disable_web_page_preview=True
    )
