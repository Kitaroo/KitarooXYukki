import asyncio
from os import path

from pyrogram import filters
from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto, Message,
                            Voice)
from youtube_search import YoutubeSearch
from youtubesearchpython import VideosSearch

import Yukki
from Yukki import (BOT_USERNAME, DURATION_LIMIT, DURATION_LIMIT_MIN,
                   MUSIC_BOT_NAME, app, db_mem)
from Yukki.Core.PyTgCalls.Converter import convert
from Yukki.Core.PyTgCalls.Downloader import download
from Yukki.Core.PyTgCalls.Tgdownloader import telegram_download
from Yukki.Database import (get_active_video_chats, get_video_limit,
                            is_active_video_chat)
from Yukki.Decorators.assistant import AssistantAdd
from Yukki.Decorators.checker import checker
from Yukki.Core.Logger.logs import LOG_CHAT
from Yukki.Decorators.permission import PermissionCheck
from Yukki.Decorators.admins import AdminRightsCheck
from Yukki.Inline import (livestream_markup, playlist_markup, search_markup,
                          search_markup2, url_markup, url_markup2)
from Yukki.Utilities.changers import seconds_to_min, time_to_seconds
from Yukki.Utilities.chat import specialfont_to_normal
from Yukki.Utilities.stream import start_stream, start_stream_audio
from Yukki.Utilities.theme import check_theme
from Yukki.Utilities.thumbnails import gen_thumb
from Yukki.Utilities.url import get_url
from Yukki.Utilities.videostream import start_stream_video
from Yukki.Utilities.youtube import (get_yt_info_id, get_yt_info_query,
                                     get_yt_info_query_slider)

loop = asyncio.get_event_loop()


DISABLED_GROUPS = []
useer = "NaN"


@app.on_message(filters.command(["player", f"player@{BOT_USERNAME}"])& ~filters.edited & ~filters.bot & ~filters.private)
@AdminRightsCheck
async def music_onoff(_, message: Message):
    user_id = message.from_user.id
    chat_title = message.chat.title
    global DISABLED_GROUPS
    try:
        user_id
    except:
        return
    if len(message.command) != 2:
        return await message.reply_text(
            "😕 **Salah Penggunaan Perintah.**\n\n» Coba `/player on` atau `/player off`"
        )
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status in ("ON", "on", "On"):
        lel = await message.reply("`Processing...`")
        if not message.chat.id in DISABLED_GROUPS:
            return await lel.edit("» **Playermusik sudah nyala ya pren...**")
        DISABLED_GROUPS.remove(message.chat.id)
        await lel.edit(f"✅ **Musik dihidupin.**\n\n• Karna hidup ga sia sia...")

    elif status in ("OFF", "off", "Off"):
        lel = await message.reply("`Processing...`")

        if message.chat.id in DISABLED_GROUPS:
            return await lel.edit("» **Musiknya udah mati kek bapak lu...**")
        DISABLED_GROUPS.append(message.chat.id)
        await lel.edit(f"✅ **Musik dimatiin.**\n\n• Kalo Udah takdir kita bisa apa?")
    else:
        return await message.reply_text(
            "😕 **Salah Penggunaan Perintah.**\n\n» Coba `/player on` atau `/player off`",
        )


@app.on_message(
    filters.command(["play", f"play@{BOT_USERNAME}"]) & filters.group
)
@checker
@PermissionCheck
@AssistantAdd
async def play(_, message: Message):
    await message.delete()
    global useer 
    if message.chat.id in DISABLED_GROUPS: return await message.reply_text(f"😕 Maaf{message.from_user.mention} Musiknya dimatikan oleh admin")
    if message.chat.id not in db_mem:
        db_mem[message.chat.id] = {}
    if message.sender_chat:
        return await message.reply_text(
            "Anda seorang __Admin Anonymous__di grup Chat ini!\nKembali ke akun pengguna dari hak Admin."
        )
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    video = (
        (message.reply_to_message.video or message.reply_to_message.document)
        if message.reply_to_message
        else None
    )
    url = get_url(message)
    if audio:
        mystic = await message.reply_text(
            "🔄 Memproses Audio... Harap Tunggu!"
        )
        try:
            read = db_mem[message.chat.id]["live_check"]
            if read:
                return await mystic.edit(
                    "Live Streaming Bermain...Hentikan untuk memutar musik"
                )
            else:
                pass
        except:
            pass
        if audio.file_size > 1073741824:
            return await mystic.edit_text(
                "Ukuran File Audio harus kurang dari 150 mb"
            )
        duration_min = seconds_to_min(audio.duration)
        duration_sec = audio.duration
        if (audio.duration) > DURATION_LIMIT:
            return await mystic.edit_text(
                f"**Batas durasi terlampaui**\n\n**Durasi yang diperbolehkan: **{DURATION_LIMIT_MIN} menit\n**Durasi yang diterima:** {duration_min} menit"
            )
        file_name = (
            audio.file_unique_id
            + "."
            + (
                (audio.file_name.split(".")[-1])
                if (not isinstance(audio, Voice))
                else "ogg"
            )
        )
        file_name = path.join(path.realpath("downloads"), file_name)
        file = await convert(
            (await message.reply_to_message.download(file_name))
            if (not path.isfile(file_name))
            else file_name,
        )
        return await start_stream_audio(
            message,
            file,
            "smex1",
            "Given Audio Via Telegram",
            duration_min,
            duration_sec,
            mystic,
        )
    elif video:
        limit = await get_video_limit(141414)
        if not limit:
            return await message.reply_text(
                "**Tidak ada batas yang ditentukan untuk panggilan Video**\n\ndan Batas Jumlah Panggilan Video Maksimum yang diizinkan di Bot oleh /set_video_limit [Sudo Users Only]"
            )
        count = len(await get_active_video_chats())
        if int(count) == int(limit):
            if await is_active_video_chat(message.chat.id):
                pass
            else:
                return await message.reply_text(
                    "Maaf! Bot hanya mengizinkan panggilan video dalam jumlah terbatas karena masalah kelebihan CPU. Banyak obrolan lain yang menggunakan video call sekarang. Coba beralih ke audio atau coba lagi nanti"
                )
        mystic = await message.reply_text(
            "🔄 Memproses Video... Harap Tunggu!"
        )
        try:
            read = db_mem[message.chat.id]["live_check"]
            if read:
                return await mystic.edit(
                    "Live Streaming Bermain...Hentikan Untuk Memutar Musik"
                )
            else:
                pass
        except:
            pass
        file = await telegram_download(message, mystic)
        return await start_stream_video(
            message,
            file,
            "Given Video Via Telegram",
            mystic,
        )
    elif url:
        mystic = await message.reply_text("🔄 Memproses URL... Harap Tunggu!")
        if not message.reply_to_message:
            query = message.text.split(None, 1)[1]
        else:
            query = message.reply_to_message.text
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = get_yt_info_query(query)
        await mystic.delete()
        buttons = url_markup2(videoid, duration_min, message.from_user.id)
        return await message.reply_photo(
            photo=thumb,
            caption=f"📎**Judul:**{title}\n\n⏳**Durasi:** {duration_min} menit\n\n ✨ <b>__Powered By Scarlet__</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        if len(message.command) < 2:
            buttons = playlist_markup(
                message.from_user.first_name, message.from_user.id, "abcd"
            )
            await message.reply_photo(
                photo="https://telegra.ph/file/17c0479350089a08d8ba7.jpg",
                caption=(
                    "**Menggunakan:** /play [Nama musik atau Link Youtube atau Membalas Audio]\n\nJika Anda ingin memainkan Playlist! Pilih salah satu dari Bawah."
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            return
        what = "Query Given"
        await LOG_CHAT(message, what)
        mystic = await message.reply_text("🔍 **Mencari**...")
        query = message.text.split(None, 1)[1]
        user_id = message.from_user.id
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = get_yt_info_query(query)
        a = VideosSearch(query, limit=5)
        result = (a.result()).get("result")
        title1 = (result[0]["title"])
        duration1 = (result[0]["duration"])
        title2 = (result[1]["title"])
        duration2 = (result[1]["duration"])      
        title3 = (result[2]["title"])
        duration3 = (result[2]["duration"])
        title4 = (result[3]["title"])
        duration4 = (result[3]["duration"])
        title5 = (result[4]["title"])
        duration5 = (result[4]["duration"])
        ID1 = (result[0]["id"])
        ID2 = (result[1]["id"])
        ID3 = (result[2]["id"])
        ID4 = (result[3]["id"])
        ID5 = (result[4]["id"])
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        return await mystic.edit(
            f"🎧 **Silahkan pilih lagu yang ingin anda putar** 🎧:\n\n1️⃣ <b>[{title1[:27]}](https://www.youtube.com/watch?v={ID1})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID1})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n2️⃣ <b>[{title2[:27]}](https://www.youtube.com/watch?v={ID2})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID2})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n3️⃣ <b>[{title3[:27]}](https://www.youtube.com/watch?v={ID3})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID3})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n4️⃣ <b>[{title4[:27]}](https://www.youtube.com/watch?v={ID4})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID4})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n5️⃣ <b>[{title5[:27]}](https://youtube.com/watch?v={ID5})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID5})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )


@app.on_callback_query(filters.regex(pattern=r"MusicStream"))
async def Music_Stream(_, CallbackQuery):
    if CallbackQuery.message.chat.id not in db_mem:
        db_mem[CallbackQuery.message.chat.id] = {}
    try:
        read1 = db_mem[CallbackQuery.message.chat.id]["live_check"]
        if read1:
            return await CallbackQuery.answer(
                "Live Streaming Bermain...Hentikan Untuk Memutar Musik",
                show_alert=True,
            )
        else:
            pass
    except:
        pass
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id = CallbackQuery.message.chat.id
    chat_title = CallbackQuery.message.chat.title
    videoid, duration, user_id = callback_request.split("|")
    if str(duration) == "None":
        buttons = livestream_markup("720", videoid, duration, user_id)
        return await CallbackQuery.edit_message_text(
            "**Live Stream Terdeteksi**\n\nIngin memainkan Live Streaming? Ini akan menghentikan pemutaran musik saat ini (jika ada) dan akan memulai streaming video langsung.",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Ini bukan untukmu! Cari lagu sendiri.", show_alert=True
        )
    await CallbackQuery.message.delete()
    title, duration_min, duration_sec, thumbnail = get_yt_info_id(videoid)
    if duration_sec > DURATION_LIMIT:
        return await CallbackQuery.message.reply_text(
            f"**Batas durasi terlampaui**\n\n**Durasi yang diperbolehkan: **{DURATION_LIMIT_MIN} menit\n**Durasi yang diterima:** {duration_min} menit"
        )
    await CallbackQuery.answer(f"Processing:- {title[:20]}", show_alert=True)
    mystic = await CallbackQuery.message.reply_text(
        f"**{MUSIC_BOT_NAME} Mendownload**\n\n**Judul:** {title[:50]}\n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
    )
    downloaded_file = await loop.run_in_executor(
        None, download, videoid, mystic, title
    )
    raw_path = await convert(downloaded_file)
    theme = await check_theme(chat_id)
    chat_title = await specialfont_to_normal(chat_title)
    thumb = await gen_thumb(thumbnail, title, user_id, theme, chat_title)
    if chat_id not in db_mem:
        db_mem[chat_id] = {}
    await start_stream(
        CallbackQuery,
        raw_path,
        videoid,
        thumb,
        title,
        duration_min,
        duration_sec,
        mystic,
    )
    
    
@app.on_callback_query(filters.regex(pattern=r"Yukki"))
async def startyuplay(_, CallbackQuery):
    if CallbackQuery.message.chat.id not in db_mem:
        db_mem[CallbackQuery.message.chat.id] = {}
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id = CallbackQuery.message.chat.id
    chat_title = CallbackQuery.message.chat.title
    videoid, duration, user_id = callback_request.split("|")
    if str(duration) == "None":
        return await CallbackQuery.answer(
            f"Sorry! Its a Live Video.", show_alert=True
        )
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "This is not for you! Search You Own Song.", show_alert=True
        )
    await CallbackQuery.message.delete()
    title, duration_min, duration_sec, thumbnail = get_yt_info_id(videoid)
    if duration_sec > DURATION_LIMIT:
        return await CallbackQuery.message.reply_text(
            f"**Duration Limit Exceeded**\n\n**Allowed Duration: **{DURATION_LIMIT_MIN} minute(s)\n**Received Duration:** {duration_min} minute(s)"
        )
    await CallbackQuery.answer()
    mystic = await CallbackQuery.message.reply_text(
        f"**Downloading** {title[:50]}...\n\n ▓▓▓▓▓▓▓▓▓▓▓▓ 0%"
    )
    downloaded_file = await loop.run_in_executor(
        None, download, videoid, mystic, title
    )
    raw_path = await convert(downloaded_file)
    theme = await check_theme(chat_id)
    chat_title = await specialfont_to_normal(chat_title)
    thumb = await gen_thumb(thumbnail, title, user_id, theme, chat_title)
    if chat_id not in db_mem:
        db_mem[chat_id] = {}
    await start_stream(
        CallbackQuery,
        raw_path,
        videoid,
        thumb,
        title,
        duration_min,
        duration_sec,
        mystic,
    )


@app.on_callback_query(filters.regex(pattern=r"Search"))
async def search_query_more(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Cari musik Anda sendiri. Anda tidak diperbolehkan menggunakan tombol ini.",
            show_alert=True,
        )
    await CallbackQuery.answer("Searching More Results")
    results = YoutubeSearch(query, max_results=5).to_dict()
    med = InputMediaPhoto(
        media="https://telegra.ph/file/17c0479350089a08d8ba7.jpg",
        caption=(
            f"1️⃣<b>{results[0]['title']}</b>\n  ┗  🔗 <u>__[Get Additional Information](https://t.me/{BOT_USERNAME}?start=info_{results[0]['id']})__</u>\n\n2️⃣<b>{results[1]['title']}</b>\n  ┗  🔗 <u>__[Get Additional Information](https://t.me/{BOT_USERNAME}?start=info_{results[1]['id']})__</u>\n\n3️⃣<b>{results[2]['title']}</b>\n  ┗  🔗 <u>__[Get Additional Information](https://t.me/{BOT_USERNAME}?start=info_{results[2]['id']})__</u>\n\n4️⃣<b>{results[3]['title']}</b>\n  ┗  🔗 <u>__[Get Additional Information](https://t.me/{BOT_USERNAME}?start=info_{results[3]['id']})__</u>\n\n5️⃣<b>{results[4]['title']}</b>\n  ┗  🔗 <u>__[Get Additional Information](https://t.me/{BOT_USERNAME}?start=info_{results[4]['id']})__</u>"
        ),
    )
    buttons = search_markup(
        results[0]["id"],
        results[1]["id"],
        results[2]["id"],
        results[3]["id"],
        results[4]["id"],
        results[0]["duration"],
        results[1]["duration"],
        results[2]["duration"],
        results[3]["duration"],
        results[4]["duration"],
        user_id,
        query,
    )
    return await CallbackQuery.edit_message_media(
        media=med, reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(pattern=r"popat"))
async def popat(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    id, query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Ini bukan untukmu! Cari streaming mu sendiri", show_alert=True
        )
    i=int(id)
    query = str(query)
    try:
        a = VideosSearch(query, limit=10)
        result = (a.result()).get("result")
        title1 = (result[0]["title"])
        duration1 = (result[0]["duration"])
        title2 = (result[1]["title"])
        duration2 = (result[1]["duration"])      
        title3 = (result[2]["title"])
        duration3 = (result[2]["duration"])
        title4 = (result[3]["title"])
        duration4 = (result[3]["duration"])
        title5 = (result[4]["title"])
        duration5 = (result[4]["duration"])
        title6 = (result[5]["title"])
        duration6 = (result[5]["duration"])
        title7 = (result[6]["title"])
        duration7 = (result[6]["duration"])      
        title8 = (result[7]["title"])
        duration8 = (result[7]["duration"])
        title9 = (result[8]["title"])
        duration9 = (result[8]["duration"])
        title10 = (result[9]["title"])
        duration10 = (result[9]["duration"])
        ID1 = (result[0]["id"])
        ID2 = (result[1]["id"])
        ID3 = (result[2]["id"])
        ID4 = (result[3]["id"])
        ID5 = (result[4]["id"])
        ID6 = (result[5]["id"])
        ID7 = (result[6]["id"])
        ID8 = (result[7]["id"])
        ID9 = (result[8]["id"])
        ID10 = (result[9]["id"])
    except Exception as e:
        n = await mystic.edit(f"😕 Song not found.\n\n» Try searching with a clearer title, or add the artist's name as well..")
        await asyncio.sleep(10)
        await message.delete()
        await n.delete()
        return
    if i == 1:
        buttons = search_markup2(ID6, ID7, ID8, ID9, ID10, duration6, duration7, duration8, duration9, duration10, user_id, query)
        await CallbackQuery.edit_message_text(
            f"🎧 **Silahkan pilih lagu yang ingin anda putar** 🎧:\n\n6️⃣ <b>[{title6[:27]}](https://www.youtube.com/watch?v={ID6})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID6})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n7️⃣ <b>[{title7[:27]}](https://www.youtube.com/watch?v={ID7})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID7})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n8️⃣ <b>[{title8[:27]}](https://www.youtube.com/watch?v={ID8})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID8})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n9️⃣ <b>[{title9[:27]}](https://www.youtube.com/watch?v={ID9})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID9})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n🔟 <b>[{title10[:27]}](https://youtube.com/watch?v={ID10})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID10})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return
    if i == 2:
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        await CallbackQuery.edit_message_text(
            f"🎧 **Silahkan pilih lagu yang ingin anda putar** 🎧:\n\n1️⃣ <b>[{title1[:27]}](https://www.youtube.com/watch?v={ID1})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID1})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n2️⃣ <b>[{title2[:27]}](https://www.youtube.com/watch?v={ID2})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID2})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n3️⃣ <b>[{title3[:27]}](https://www.youtube.com/watch?v={ID3})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID3})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n4️⃣ <b>[{title4[:27]}](https://www.youtube.com/watch?v={ID4})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID4})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__\n\n5️⃣ <b>[{title5[:27]}](https://youtube.com/watch?v={ID5})</b>\n ├ 📚 <b>[More Information](https://t.me/{BOT_USERNAME}?start=info_{ID5})</b>\n └ 💎 __Powered by {MUSIC_BOT_NAME}__",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview = True
        )
        return



@app.on_callback_query(filters.regex(pattern=r"slider"))
async def slider_query_results(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    what, type, query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Cari musik Anda sendiri. Anda tidak diperbolehkan menggunakan tombol ini.",
            show_alert=True,
        )
    what = str(what)
    type = int(type)
    if what == "F":
        if type == 9:
            query_type = 0
        else:
            query_type = int(type + 1)
        await CallbackQuery.answer("Mendapatkan hasil berikutnya", show_alert=True)
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = get_yt_info_query_slider(query, query_type)
        buttons = url_markup(
            videoid, duration_min, user_id, query, query_type
        )
        med = InputMediaPhoto(
            media=thumb,
            caption=f"📎**Judul:**{title}\n\n⏳**Durasi:** {duration_min} Menit\n\n ✨ <b>__Powered By Scarlet__</b>",
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
    if what == "B":
        if type == 0:
            query_type = 9
        else:
            query_type = int(type - 1)
        await CallbackQuery.answer("Mendapatkan hasil sebelumnya", show_alert=True)
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = get_yt_info_query_slider(query, query_type)
        buttons = url_markup(
            videoid, duration_min, user_id, query, query_type
        )
        med = InputMediaPhoto(
            media=thumb,
            caption=f"📎**Judul:**{title}\n\n⏳**Durasi:** {duration_min} Menit\n\n ✨ <b>__Powered By Scarlet</b>__",
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
