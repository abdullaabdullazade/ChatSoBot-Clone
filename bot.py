import os
import time
from dotenv import dotenv_values,load_dotenv

from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, \
    InputMediaPhoto,InputMediaVideo
import sqlite3 as sql
import random



load_dotenv()

TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID") 
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# variables
app = Client('ChatSoBot', api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH,
             bot_token=TELEGRAM_BOT_TOKEN)

stickers = ['🙋🏻‍♂', '👨🏻', '👨🏻‍💻', '👨🏻‍🏫', '👨🏻‍', '🕺', '🥷', '🤴🏻', '👨🏻‍', '👦🏻', '👮🏻‍♂', '👨🏻‍🔧', '👨🏻‍🚒', '👨🏻',
            '🧑🏻‍🚀']
stickers_woman = ['🙋🏻‍♀', '👩🏻', '👩🏻‍💻', '👩🏻‍🏫', '👩🏻‍', '💃',
                  '🥷', '👸🏻', '👩🏻‍', '👧🏻', '👮🏻‍', '👩🏻‍🔧',
                  '👩🏻‍🚒', '👩🏻‍', '🧑🏻‍🚀', '👩🏻‍🌾', '👩🏻‍🍳',
                  '👩🏻‍🔬', '👩🏻‍🎨', '👩🏻‍🎤']
flags = [
    "🇦🇿",  # Azerbaijan
    "🇹🇷",  # Turkey
    "🇷🇺"  # Russia
]
languages = ['🇦🇿Azərbaycanca ▫', '🇹🇷 Türkçe ▫', '🇷🇺 Русский ▫']

database = sql.connect('database.db', check_same_thread=False)

register_user_list = {}
register_user_info = {}
change_user_info = {}
questions = ['Adınız nədir?', '✍Neçə yaşınız var?',
             '🎎 Cinsiyyətinizi seçin:',
             '🖼 Profil şəklinizin hansı olmasını istərdinizsə onu mənə göndərin ( Max: 5 MB ölçüdə olmalıdır)',
             """Haqqınızda qısa məlumat verin\nNə işlə məşğulsuniz, Oxuyursunuzmu? və.s"""]

searchings = {}
chattings = {}

give_present = {}

hearts = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 10, 6: 20, 7: 25, 8: 40, 9: 50, 10: 75, 11: 100, 12: 200}


# Functions
def check_user(id, check_start='_'):
    if database.execute(f'SELECT ID FROM Users WHERE ID={id}').fetchone() is None:
        if check_start != 'start':
            app.send_message(id, 'Qeydiyyatdan keç. Bunun üçün /start yaz.')
        return False
    return True


def register_user(id):
    user_id = id
    info = register_user_info[user_id]
    database.execute(
        f"INSERT INTO Users VALUES({user_id},{info[1]},'{info[0]}',0,0,0,'{info[2]}','{info[3]}',0,0,0,0,0,0,0)")
    if info[2].lower() == 'kişi':
        man_count = database.execute(f'SELECT Men FROM Common').fetchone()[0]
        database.execute(f"UPDATE Common SET Men = {man_count + 1}")
    else:
        woman_count = database.execute(f'SELECT Women FROM Common').fetchone()[0]
        database.execute(f"UPDATE Common SET Women = {woman_count + 1}")

    app.send_message(user_id, '**Demək olar hər şey hazırdır.**', reply_markup=ReplyKeyboardRemove())

    database.commit()
    send_profile(user_id)
    if register_user_list.get(user_id) != -1:
        register_user_list.pop(user_id)
        register_user_info.pop(user_id)


def check_gender_image(id):
    user_id = id
    if register_user_info.get(user_id) is not None:
        info = register_user_info[user_id][2]
    else:
        info = database.execute(f'SELECT Sex FROM Users WHERE ID={id}').fetchone()[0]
    print(info)
    if info.lower() == 'kişi':
        return "man_photos"
    else:
        return 'woman_photos'


def check_gender(id):
    user_id = id
    if register_user_info.get(user_id) is not None:
        info = register_user_info[user_id][2]
    else:
        info = database.execute(f'SELECT Sex FROM Users WHERE ID={id}').fetchone()[0]
    print(info)
    if info.lower() == 'kişi': return True
    return False


def check_age(age, id):
    if str(age).isdigit():

        age = int(age)
        print(age)
        if 15 <= age <= 60:
            return True
        app.send_message(id, '**Yaş seçimi 15-dən böyük 60-dan kiçik olmalıdır**')
    else:
        app.send_message(id, '**Rəqəm girin**')
    return False


def check_profile_pic(id):
    image_folder = check_gender_image(id)
    images = os.listdir(image_folder)
    random_image = random.choice(images)
    buttons = [
        [InlineKeyboardButton('➡İrəli', callback_data=f'next_image'),
         InlineKeyboardButton('✅Seçin', callback_data=f'select_image')],
    ]
    print(id)
    photo_message = app.send_photo(id, f'{image_folder}/{random_image}', reply_markup=ReplyKeyboardRemove())
    app.send_message(id, '🖼Profil şəkli olmağını istərdinizmi?',
                     reply_markup=InlineKeyboardMarkup(buttons))


def send_profile(id):
    user_info = database.execute(f"SELECT Age,Nick,About,Sex FROM Users WHERE ID={id}").fetchone()
    buttons = [
        [InlineKeyboardButton('🔄Düzəliş Et', callback_data='change_profile'),
         InlineKeyboardButton('🔍Çata Başla', callback_data='start_chat')]
    ]
    app.send_photo(id, f'downloads/{id}.png', f"""
    **🥳 Demək olar hərşey hazırdır**\n\n👤 Adınız: **{user_info[1]}\n\n📆 Yaşınız: **{user_info[0]}\n\n🗒 Haqqınızda:{user_info[2]}\n\n🎎 Cinsiyyət: **{user_info[3]}**
    """, reply_markup=InlineKeyboardMarkup(buttons))


def choose_sticker(id):
    info = database.execute(f'SELECT Sex FROM Users WHERE ID={id}').fetchone()[0]
    if info.lower() == 'kişi':
        return stickers
    return stickers_woman


def profile_user(id, msg_id=0, key="_"):
    print('xe')
    user_info = database.execute(
        F"SELECT ID,Nick,Biriliant,Hearts,Sticker,Anonyms,Media,VIP FROM Users Where ID={id}").fetchone()
    vip = user_info[7]
    if not vip:
        vip = "🙁 Yoxdur"
    anonyms = user_info[5]
    if anonyms == 0:
        anonyms = "❌ Bağlıdır"
    else:
        anonyms = '✅ Açıqdır'
    if user_info[6] == 0:
        media = '❌ Xeyr'
    else:
        media = '✅ Bəli'
    print(media)
    emoji = choose_sticker(id)[user_info[4]]
    buttons = [
        [InlineKeyboardButton(f'Media{media[0]}', callback_data='change_media'),
         InlineKeyboardButton(f"Anonimlik{anonyms[0]}", callback_data='change_anonyms')],
        [InlineKeyboardButton(f'💎 Al', callback_data='buy_biriliant'),
         InlineKeyboardButton('💰 Pul Çıxarışı', callback_data='withdrawal')],
        [InlineKeyboardButton(f'Emojiniz {emoji}', callback_data='change_emoji'),
         InlineKeyboardButton('🖼Profiliniz', callback_data='see_profil')],
        [InlineKeyboardButton('⭐Vip Al', callback_data='buy_vip')],
        [InlineKeyboardButton('🗑 Sil', callback_data='delete')]
    ]
    if key == 'back':
        app.edit_message_media(id, msg_id, InputMediaPhoto(f'downloads/{id}.png'))
    if msg_id == 0:
        app.send_photo(id, f"downloads/{id}.png",
                       F"🆔 ID: {id}\n\nÇatdakı adınız: {user_info[1]}\n\nAlmaz: {user_info[2]}💎\nÜrək Balansınız: {user_info[2]}❤ = {user_info[2]} ₼**\n\n"
                       F"**Emojiniz: {emoji}**\n\n"
                       F"**Vip Istifadəçilik: {vip}**\n\n"
                       F"**Anonimliyiniz (Açıq olarsa siz mesaj yazan zaman başqaları əsil profilinizin adını görəcək) : {anonyms}**\n\n"
                       F"**Başqaları sizə (Səs,Video və.s) göndərə bilərmi ?: {media}**",
                       reply_markup=InlineKeyboardMarkup(buttons))
        return
    app.edit_message_text(id, msg_id,
                          F"🆔 ID: {id}\n\nÇatdakı adınız: {user_info[1]}\n\nAlmaz: {user_info[2]}💎\nÜrək Balansınız: {user_info[2]}❤ = {user_info[2]} ₼**\n\n"
                          F"**Emojiniz: {emoji}**\n\n"
                          F"**Vip Istifadəçilik: {vip}**\n\n"
                          F"**Anonimliyiniz (Açıq olarsa siz mesaj yazan zaman başqaları əsil profilinizin adını görəcək) : {anonyms}**\n\n"
                          F"**Başqaları sizə (Səs,Video və.s) göndərə bilərmi ?: {media}**",
                          reply_markup=InlineKeyboardMarkup(buttons))


def update(tablename, element, id, tabletitle='Users'):
    database.execute(f"UPDATE {tabletitle} SET {tablename} = ? WHERE ID = ?", (element, id))
    database.commit()


def mating_users(id):
    user_id = chattings[id]
    user_info = database.execute(
        F'SELECT Nick,Sticker,Followers,About,Sex,Language,Likes,Dislikes,Age FROM Users WHERE ID={user_id}').fetchone()
    sticker = choose_sticker(user_id)[user_info[1]]
    print(sticker, user_info[1])
    buttons = [[
        InlineKeyboardButton('❤ Hədiyyə et', callback_data='give_present'),
        InlineKeyboardButton('İzlə', callback_data='follow')
    ]
        , [
            InlineKeyboardButton('👍', callback_data='Likes'),
            InlineKeyboardButton('👎', callback_data='Dislikes'),

        ],
        [InlineKeyboardButton('🔄Dəyiş', callback_data='change_search_user'),
         InlineKeyboardButton('📫Şikayət', callback_data='report')]
    ]
    app.send_photo(id, f"downloads/{user_id}.png", f'**🎉 Ləqəbi:{user_info[0]}{sticker}**\n\n'
                                                   f'**👥 İzləyici sayı: {user_info[2]}\n**'
                                                   f'**🏷 Haqqında: {user_info[3]}\n**'
                                                   f'**🗓 Yaş: {user_info[8]}\n**'
                                                   f'**🚻 Cinsiyəti: {user_info[4]}\n**'
                                                   f'**🌐 Language: {flags[user_info[5]]}\n**'
                                                   f'**👍{user_info[6]}👎{user_info[7]}\n\n**'
                                                   f'**Xoş Söhbətlər 🥳**'
                   , reply_markup=InlineKeyboardMarkup(buttons))


def current_chat(id):
    if chattings.get(id) is not None:
        return True
    return False


def search_(id):
    user_id = id
    if chattings.get(user_id) is None and searchings.get(user_id) is None:
        app.send_video(user_id, 'gifs/search.mp4')
        app.send_message(user_id, '📍 İpucu: Ayarlar bölməsindən istədiyiniz nizamlamaları dəyişə bilərsiniz /settings')
        blocked_users = [x[0] for x in database.execute(F"SELECT C_ID FROM Blocks WHERE ID={user_id}").fetchall()]
        while True:
            print(searchings)
            if len(searchings) == 0:
                searchings[user_id] = ""
                break
            else:
                for i in searchings.keys():
                    if not i in blocked_users and i != user_id:
                        chattings[user_id] = i
                        chattings[i] = user_id
                        mating_users(user_id)
                        mating_users(i)
                        searchings.pop(i)
                        if searchings.get(user_id) is not None:
                            searchings.pop(user_id)
                        return
                if chattings.get(user_id) is None:
                    searchings[user_id] = ''
            print(searchings)

            time.sleep(0.5)
    else:
        app.send_message(user_id, "Senin geden chatin var")


def stop(id):
    chat_id = id
    if chattings.get(chat_id) is None:
        searchings.pop(chat_id)
    else:
        user_2 = chattings[chat_id]
        app.send_message(user_2, 'Qarşı tərəf chatı dayandırdı')
        chattings.pop(user_2)
        chattings.pop(chat_id)


def fetch_data(table, tabletitle, id='_'):
    if id == "_":
        return database.execute(f'SELECT {tabletitle} FROM {table}').fetchone()[0]
    else:
        return database.execute(f'SELECT {tabletitle} FROM {table} WHERE ID={id}').fetchone()[0]


# App


# Bot commands
@app.on_message(filters.command('start') & filters.private)
def start(bot, msg):
    global register_user_list, register_user_info
    user_id = msg.from_user.id
    if not check_user(user_id, 'start'):
        register_user_list[user_id] = 0
        register_user_info[user_id] = []
        print(register_user_info[user_id])
        app.send_message(user_id, f"**{questions[0]}**")
    else:
        msg.reply('Çata başlamaq üçün /search yazın.')


@app.on_message(filters.command("settings") & filters.private)
def profile(bot, msg):
    profile_user(msg.from_user.id, 0)
    return


@app.on_message(filters.command('search') & filters.private)
def search(bot, msg):
    user_id = msg.from_user.id
    if check_user(user_id):
        search_(user_id)


@app.on_message(filters.command('stop') & filters.private)
def stop_(bot, msg):
    stop(msg.from_user.id)
    app.send_video(msg.from_user.id, 'gifs/stop.mp4', '**Söhbəti dayandırdınız yeni söhbət üçün /search edin**'
                   )


@app.on_message(filters.command('botstatic') & filters.private)
def botstats(bot, msg):
    user_id = msg.from_user.id
    men = fetch_data('Common', 'Men')
    women = fetch_data('Common', 'Women')
    current_chat_now = len(chattings) // 2
    current_searching_now = len(searchings)
    banned_user = fetch_data('Common', 'BannedUser')
    vip_count = fetch_data('Common', 'VIP')
    app.send_message(user_id, 'ChatSOBot Botu Statistikası\n\n'
                              f'🗣 Hal-hazırda Söhbətləşən: **{current_chat_now}**\n'
                              f'🔎 Axtarış edən: **{current_searching_now}**\n'
                              f'⭐ Vip İstifadəçi: **{vip_count}**\n'
                              f'💣 Ban olunanların sayı: **{banned_user}**\n'
                              f'✅ Ümumi İstifadəçi sayı:\n **👩🏻{women} + 🧔🏻‍{men} = {women + men}**')


@app.on_message(filters.command('help') & filters.private)
def help(bot, msg):
    button = [[
        InlineKeyboardButton('Ətraflı', url='https://t.me/SOBotlar/180')
    ]]
    app.send_message(msg.from_user.id,
                     "**Bot və komandalar haqqında məlumat almaq üçün aşağıdan Ətraflı düyməsinə tıklayın**",
                     reply_markup=InlineKeyboardMarkup(button))


@app.on_message(filters.command('block') & filters.private)
def block(bot, msg):
    if chattings.get(msg.from_user.id) is None:
        msg.reply(
            "**Bu funksiya hər hansısa söhbət zamanı qarşı tərəfi bloklamağınıza kömək olacaqdır.Əgər qarşınızdakı istifadəçinin heçbir zaman birdaha qarşınıza çıxmağını istəməsəniz həmin istifadəçi ilə mesajlaşarkən /block yazmağınız kifayətdir**")
    else:
        database.execute(f"INSERT INTO Blocks VALUES({msg.from_user.id},{chattings[msg.from_user.id]})")
        database.execute(f"INSERT INTO Blocks VALUES({chattings[msg.from_user.id]},{msg.from_user.id})")

        app.send_message(msg.from_user.id, '**User bloklandı. Bir daha qarşınıza çıxmayacaq.**')
        stop(msg.from_user.id)
    database.commit()


# callbackquery, photo,text
@app.on_message(filters.text & filters.private)
def text(bot, msg):
    global register_user_list, register_user_info
    user_id = msg.from_user.id

    if register_user_list.get(user_id) is not None:
        index = register_user_list[user_id]
        info = register_user_info[user_id]
        if index == 4 and str(msg.text).lower() in ['addımı keç', 'addimi kec']:
            info.append('')
            register_user(user_id)
            return

        if index == 3 and not str(msg.text).lower() in ['gondermek istemirem', 'göndərmək istəmirəm']:
            msg.reply('**Şəkil atın, zəhmət olmasa🖼**')
            return
        elif index == 3 and str(msg.text).lower() in ['gondermek istemirem', 'göndərmək istəmirəm']:
            msg.reply('**Aşağıdakı Avatarlardan istədiyinizi profil şəkli seçə bilərsiniz**',
                      reply_markup=ReplyKeyboardRemove())
            check_profile_pic(user_id)
            return

        if index == 0:
            info.append(msg.text)
            register_user_list[user_id] = index + 1
            print('ad')
            msg.reply(f"**{questions[index + 1]}**")
        elif index == 1:
            if check_age(msg.text, user_id):
                info.append(int(msg.text))
                buttons = [[
                    ('🧔🏻‍Mən Kişiyəm'),
                    ('👩🏻Mən Qadınam')
                ]]
                reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
                msg.reply(text=f'**{questions[index + 1]}**', reply_markup=reply_markup)
                register_user_list[user_id] = index + 1


        elif index == 2:
            gender = msg.text.lower().strip()
            if str(gender) in ['🧔🏻‍mən kişiyəm', '👩🏻mən qadınam', '🧔🏻‍men kisiyem', '👩🏻men qadinam']:
                if str(gender) in ['🧔🏻‍mən kişiyəm', '🧔🏻‍men kisiyem']:
                    info.append("Kişi")



                else:
                    info.append('Qadın')
                print(register_user_info[user_id])
                register_user_list[user_id] = index + 1
                buttons = [
                    [
                        ('Göndərmək istəmirəm')
                    ]
                ]
                msg.reply(f"**{questions[index + 1]}**",
                          reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
            else:
                msg.reply("**Cinsi yenidən girin.**")

        if index == 4:
            info.append(msg.text)
            register_user(user_id)
    elif change_user_info.get(user_id):
        if change_user_info[user_id] == 'name':
            update('Nick', msg.text, user_id)
            msg.reply('**Adınız uğurla dəyişdirildi. Çata başlamaq üçün /search bura tıklayın**')
            change_user_info.pop(user_id)
        elif change_user_info[user_id] == 'bio':
            update('About', msg.text, user_id)
            msg.reply('**✅Bio uğurla dəyişdirildi. Çata başlamaq üçün /search bura tıklayın**')
            change_user_info.pop(user_id)

        elif change_user_info[user_id] == 'age':
            update('Age', msg.text, user_id)
            if check_age(msg.text, user_id):
                msg.reply('**📆Yaşınız uğurla dəyişdirildi. Çata başlamaq üçün /search bura tıklayın**')
                change_user_info.pop(user_id)
        elif change_user_info[user_id] == 'pic':
            print(msg.text)
            if str(msg.text).lower() in ['gondermek istemirem', 'göndərmək istəmirəm']:
                check_profile_pic(user_id)
            else:
                msg.reply('**Şəkil atın, zəhmət olmasa🖼**')
    elif chattings.get(user_id):
        stickers_packet = choose_sticker(user_id)
        nickandsticker = database.execute(f"SELECT Nick,Sticker,Anonyms FROM Users WHERE ID={user_id}").fetchone()
        if nickandsticker[2] == 0:
            name = nickandsticker[0]
        else:
            name = app.get_users(user_id).first_name
        app.send_message(chattings[user_id], f'{stickers_packet[nickandsticker[1]]}{name}: **{msg.text}**')
    database.commit()


@app.on_message(filters.photo & filters.private)
async def photo(bot, msg):
    user_id = msg.from_user.id
    if register_user_list.get(user_id) is not None:
        index = register_user_list[user_id]
        if index == 3:
            print('xe')
            await app.download_media(msg.photo.file_id, file_name=str(user_id) + '.png')
            register_user_list[user_id] = index + 1
            await app.send_message(msg.from_user.id, f'**{questions[index + 1]}**', reply_markup=
            ReplyKeyboardMarkup([[
                ('Addımı keç')
            ]], resize_keyboard=True, one_time_keyboard=True))
    elif change_user_info.get(msg.from_user.id) is not None:
        if change_user_info[msg.from_user.id] == 'pic':
            await app.download_media(msg.photo.file_id, file_name=str(user_id) + '.png')
            change_user_info.pop(user_id)
            await app.send_message(user_id, 'Profil uğurla dəyişdirildi. Çata başlamaq üçün /search bura tıklayın',reply_markup=ReplyKeyboardRemove())
    elif chattings.get(user_id):
        user_id_ = chattings[user_id]
        stickers_packet = choose_sticker(user_id_)
        nickandsticker = database.execute(
            f"SELECT Nick,Sticker,Media,Anonyms FROM Users WHERE ID={user_id_}").fetchone()
        print(nickandsticker)
        if nickandsticker[2] == 1:
            if nickandsticker[3] == 0:
                name = nickandsticker[0]
            else:
                name = await app.get_users(user_id)
                name = name.first_name
            await app.send_photo(user_id_, msg.photo.file_id, f'{stickers_packet[nickandsticker[1]]}{name}:')


@app.on_message(filters.voice & filters.private)
async def voice(bot, msg):
    user_id = chattings[msg.from_user.id]
    if chattings.get(user_id):
        stickers_packet = choose_sticker(user_id)
        nickandsticker = database.execute(
            f"SELECT Nick,Sticker,Media,Anonyms FROM Users WHERE ID={user_id}").fetchone()
        if nickandsticker[2] == 1:
            if nickandsticker[3] == 0:
                name = nickandsticker[0]
            else:
                name = await app.get_users(msg.from_user.id)
                name = name.first_name
            await app.send_voice(user_id, msg.voice.file_id, f'{stickers_packet[nickandsticker[1]]}{name}:')



@app.on_callback_query()
def handle_callback_query(bot, callback_query):
    query_data = callback_query.data
    chat_id = callback_query.from_user.id
    message_id = int(callback_query.message.id) - 1
    if query_data == 'next_image':
        images = check_gender_image(callback_query.from_user.id)
        images_list = os.listdir(images)
        random_image = random.choice(images_list)
        print(f"Editing message in chat {chat_id} with message ID {message_id}")
        print(os.path.join(images,random_image))
        app.delete_messages(chat_id,[message_id,message_id+1])
        check_profile_pic(chat_id)

    elif query_data == 'select_image':
        if register_user_list.get(chat_id) is not None:
            index = register_user_list[chat_id]
            app.send_message(callback_query.from_user.id, "Şəkil seçildi✅", reply_markup=ReplyKeyboardRemove())
            message = app.get_messages(chat_id, message_id)
            print(message)
            app.download_media(message.photo.file_id, file_name=str(chat_id) + '.png')
            app.delete_messages(chat_id, message_id)
            app.delete_messages(chat_id, message_id + 1)
            app.delete_messages(chat_id, message_id - 1)
            register_user_list[chat_id] = index + 1
            app.send_message(chat_id, f"**{questions[index + 1]}**", reply_markup=ReplyKeyboardMarkup([[
                ('Addımı keç')
            ]], one_time_keyboard=True, resize_keyboard=True))

        else:
            app.edit_message_text(chat_id, callback_query.message.id,
                                  '✅Avatarınız seçildi. Çata başlamaq üçün /search bura tıklayın',
                                  reply_markup=ReplyKeyboardRemove())
            message = app.get_messages(chat_id, message_id)
            print(message)
            app.download_media(message.photo.file_id, file_name=str(chat_id) + '.png')

    elif query_data == 'select_image':
        if register_user_list.get(chat_id) is not None:
            index = register_user_list[chat_id]
            message = app.get_messages(chat_id, message_id)
            app.download_media(message.photo.file_id, file_name=str(chat_id) + '.png')
            app.send_message(callback_query.from_user.id, "Şəkil seçildi✅", reply_markup=ReplyKeyboardRemove())
            app.delete_messages(chat_id, message_id)
            app.delete_messages(chat_id, message_id + 1)
            app.delete_messages(chat_id, message_id - 1)
            register_user_list[chat_id] = index + 1
            app.send_message(chat_id, f"**{questions[index + 1]}**", reply_markup=ReplyKeyboardMarkup([[
                ('Addımı keç')
            ]], one_time_keyboard=True, resize_keyboard=True))

        else:
            message = app.get_messages(chat_id, callback_query.message.id - 1)
            print(message)
            app.download_media(message.photo.file_id, file_name=str(chat_id) + '.png')
            app.edit_message_text(chat_id, callback_query.message.id,
                                  '✅Avatarınız seçildi. Çata başlamaq üçün /search bura tıklayın',
                                  reply_markup=ReplyKeyboardRemove())

    elif query_data == 'start_chat':
        search_(chat_id)
    elif query_data == 'change_profile':
        buttons = [
            [InlineKeyboardButton('🌐Adı Dəyiş', callback_data='change_name'),
             InlineKeyboardButton('📆Yaşı Dəyiş', callback_data='change_age')],
            [InlineKeyboardButton('🖼Şəkili Dəyiş', callback_data='change_pic'),
             InlineKeyboardButton('🗒Haqqınızdanı Dəyiş', callback_data='change_bio')],
            [InlineKeyboardButton('⚙Ayarlar', callback_data='settings')]
        ]
        app.edit_message_text(chat_id, callback_query.message.id, '✍ Harada düzəliş etmək istəyirsiniz?',
                              reply_markup=InlineKeyboardMarkup(buttons))
    elif query_data == 'change_name':
        print('xe')
        app.edit_message_text(chat_id, callback_query.message.id, f"{questions[0]}")
        change_user_info[callback_query.from_user.id] = 'name'
    elif query_data == 'change_bio':
        print('xe')
        app.edit_message_text(chat_id, callback_query.message.id, f"✍{questions[4]}")
        change_user_info[callback_query.from_user.id] = 'bio'
    elif query_data == 'change_age':
        print('xe')
        app.edit_message_text(chat_id, callback_query.message.id, f"{questions[1]}")
        change_user_info[callback_query.from_user.id] = 'age'
    elif query_data == 'change_pic':
        print('xe')
        buttons = [

            [('Göndərmək istəmirəm')]
        ]
        # Deleting the message associated with the callback query
        app.delete_messages(chat_id, callback_query.message.id)

        # Sending a new message with a custom keyboard
        app.send_message(chat_id, f"**{questions[3]}**",
                         reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))

        # Updating the user's info in the dictionary
        change_user_info[callback_query.from_user.id] = 'pic'
    elif query_data == 'settings':
        profile_user(chat_id, callback_query.message.id)
    elif query_data == 'change_media':
        check_media = database.execute(F'SELECT Media FROM Users WHERE ID={chat_id}').fetchone()[0]
        if check_media:
            update('Media', 0, chat_id)
        else:
            update('Media', 1, chat_id)
        profile_user(chat_id, callback_query.message.id)
    elif query_data == 'change_anonyms':
        check_media = database.execute(F'SELECT Anonyms FROM Users WHERE ID={chat_id}').fetchone()[0]
        if check_media:
            update('Anonyms', 0, chat_id)
        else:
            update('Anonyms', 1, chat_id)
        profile_user(chat_id, callback_query.message.id)
    elif query_data == 'buy_biriliant':
        biriliant_count = database.execute(f"SELECT Biriliant FROM Users WHERE ID={chat_id}").fetchone()[0]
        buttons = [
            # 💎
            [InlineKeyboardButton('10💎 - 1 AZN', url='https://sobotlar.com/api/6687203347/100/ChatSOBot'),
             InlineKeyboardButton('20💎 - 2 AZN', url='https://sobotlar.com/api/6687203347/200/ChatSOBot')],
            [InlineKeyboardButton('50💎 - 5 AZN', url='https://sobotlar.com/api/6687203347/500/ChatSOBot'),
             InlineKeyboardButton('100💎 - 10 AZN', url='https://sobotlar.com/api/6687203347/1000/ChatSOBot')],
            [InlineKeyboardButton('250💎 - 25 AZN', url='https://sobotlar.com/api/6687203347/2500/ChatSOBot'),
             InlineKeyboardButton('500💎 - 50 AZN', url='https://sobotlar.com/api/6687203347/5000/ChatSOBot')],
            [InlineKeyboardButton('1000💎 - 100 AZN', url='https://sobotlar.com/api/6687203347/10000/ChatSOBot'),
             InlineKeyboardButton('2000💎 - 10 AZN', url='https://sobotlar.com/api/6687203347/20000/ChatSOBot')],
            [InlineKeyboardButton('🔙 Geri', callback_data='back')]
        ]
        app.delete_messages(chat_id, callback_query.message.id)
        app.send_video(chat_id, 'gifs/biriliant.mp4', f'💎 Balansınız: {biriliant_count}\n'
                                                      f'Aşağıdan istədyiniz qədər balansınızı artıra bilərsiniz',
                       reply_markup=InlineKeyboardMarkup(buttons))

    elif query_data == 'withdrawal':
        heart = database.execute(F"SELECT Hearts FROM Users WHERE ID={chat_id}").fetchone()[0]

        buttons = [
            [InlineKeyboardButton('💳Karta köçür', callback_data='pay_to_card')],
            [InlineKeyboardButton('🔙 Geri', callback_data='back')]
        ]
        app.delete_messages(chat_id, callback_query.message.id)
        app.send_video(chat_id, 'gifs/withdrawal.mp4',
                       f'Buradan sizə göndərilən ❤-ləri Real pula çevirə bilərsiniz 🥰\n\n'
                       f'💰 Balansınız: {heart}❤ = {heart} ₼',
                       reply_markup=InlineKeyboardMarkup(buttons))
    elif query_data == 'pay_to_card':
        heart = database.execute(F"SELECT Hearts FROM Users WHERE ID={chat_id}").fetchone()[0]
        if heart < 175:
            callback_query.answer(f'Yığdığınız ❤-ləri Nəğdləşdirə bilmək üçün ən azı 175❤ olmalıdır.\n'
                                  f'💰Balansınız:{heart}❤ = {heart}₼', show_alert=True)
    elif query_data == 'change_emoji':
        stickers_ = choose_sticker(chat_id)
        current_sticker = database.execute(f"SELECT Sticker FROM Users WHERE ID={chat_id}").fetchone()[0]
        buttons = []
        row = 0
        for i in stickers_:
            if row % 5 == 0:
                buttons.append([])

            if stickers_[current_sticker] == i:
                buttons[-1].append(InlineKeyboardButton(i + '▪', callback_data=f'emoji#{stickers_.index(i)}'))
            else:
                buttons[-1].append(InlineKeyboardButton(i + '▫', callback_data=f'emoji#{stickers_.index(i)}'))
            row += 1
        buttons.append([InlineKeyboardButton('🔙 Geri', callback_data='back')])
        app.edit_message_text(chat_id, callback_query.message.id, 'Almaq İstədiyiniz emojini aşağıdan seçin',
                              reply_markup=InlineKeyboardMarkup(buttons))

    elif query_data == 'see_profil':
        user_info = database.execute(f"SELECT Age,Nick,About,Sex FROM Users WHERE ID={chat_id}").fetchone()
        buttons = [
            [InlineKeyboardButton('🔄Düzəliş Et', callback_data='change_profile')],
            [InlineKeyboardButton('🔙 Geri', callback_data='back')]
        ]
        app.edit_message_text(chat_id, callback_query.message.id,
                              f"""👤 Adınız: **{user_info[1]}\n\n📆 Yaşınız: **{user_info[0]}\n\n🗒 Haqqınızda:{user_info[2]}\n\n🎎 Cinsiyyət: **{user_info[3]}**
              """, reply_markup=InlineKeyboardMarkup(buttons))
    elif query_data[:5] == 'emoji':
        biriliant = int(database.execute(F"SELECT Biriliant FROM Users WHERE ID={chat_id}").fetchone()[0])
        print(biriliant)
        if biriliant < 1:
            callback_query.answer(
                'Bu Emojini almaq üçün hesabınızda 1💎 olmalıdır. Balansınızı artırmaq üçün Geri düyməsinə tıklayın və 💎 Al bölməsinə daxil olun',
                show_alert=True)
            return
        emoji_id = int(query_data.split('#')[1])
        update('Sticker', emoji_id, chat_id)
        update('Biriliant', biriliant - 1, chat_id)
        app.send_message(chat_id, '💎 Emoji alındı.')
        profile_user(chat_id, callback_query.message.id)


    elif query_data == 'delete':
        app.delete_messages(chat_id, callback_query.message.id)

    elif query_data == 'back':
        profile_user(chat_id, callback_query.message.id, key='back')
    elif query_data in ['Likes', 'Dislikes']:
        if current_chat(chat_id):
            check_user_likes_and_dislikes = database.execute(F"SELECT * FROM LikesAndDislikes WHERE ID={chat_id}")
            likesanddislikes = \
                database.execute(F"SELECT {query_data} FROM Users WHERE ID={chattings[chat_id]}").fetchone()[0]
            if check_user_likes_and_dislikes.fetchone() is None:
                database.execute(f"INSERT INTO LikesAndDislikes VALUES({chat_id},{chattings[chat_id]})")
                update('Likes', 1, chattings[chat_id])
                callback_query.answer(f'Bu istifadəçi {query_data[:-1]} etdiniz!', show_alert=True)
            database.commit()
            check_user_likes_and_dislikes = database.execute(
                F"SELECT * FROM LikesAndDislikes WHERE ID={chat_id}").fetchall()
            c_ids = [x[1] for x in check_user_likes_and_dislikes]

            if chattings[chat_id] in c_ids:
                callback_query.answer('Siz bu istifadəçini dəyərləndirmisiniz', show_alert=True)
            else:
                update(f'{query_data}', likesanddislikes + 1, chattings[chat_id])
                callback_query.answer(f'Bu istifadəçi {query_data[:-1]} etdiniz!', show_alert=True)

        else:
            callback_query.answer('Artıq bu istifadəçi ilə çatlaşmırsınız!', show_alert=True)
        database.commit()
    elif query_data == 'follow':
        if current_chat(chat_id):
            check_user_likes_and_dislikes = database.execute(F"SELECT * FROM LikesAndDislikes WHERE ID={chat_id}")
            check_follow = \
                database.execute(F"SELECT Followers FROM Users WHERE ID={chattings[chat_id]}").fetchone()[0]
            if check_user_likes_and_dislikes.fetchone() is None:
                database.execute(f"INSERT INTO Followers VALUES({chat_id},{chattings[chat_id]})")
                followers_count = \
                    database.execute(f"SELECT Followers FROM Users WHERE ID={chattings[chat_id]}").fetchone()[0]
                update('Followers', followers_count + 1, chat_id)
                callback_query.answer(f'Bu istifadəçi izləyirsiniz!', show_alert=True)
            check_user_likes_and_dislikes = database.execute(
                F"SELECT * FROM Followers WHERE ID={chat_id}").fetchall()
            c_ids = [x[1] for x in check_user_likes_and_dislikes]
            if chattings[chat_id] in c_ids:
                callback_query.answer('Siz bu istifadəçini izləyirsiniz', show_alert=True)
            else:
                update(f'Followers', check_follow + 1, chattings[chat_id])
                callback_query.answer(f'Bu istifadəçi izləyrsiniz!', show_alert=True)

        else:
            callback_query.answer('Artıq bu istifadəçi ilə çatlaşmırsınız!', show_alert=True)
    elif query_data == 'give_present':
        if current_chat(chat_id):
            if give_present.get(chat_id) is None:
                buttons = [[
                    InlineKeyboardButton('➡Növbəti', callback_data='next_heart'),
                    InlineKeyboardButton('🔙Geri', callback_data='back_heart')

                ],
                    [InlineKeyboardButton('❤Göndər', callback_data='send_heart')]
                ]
                give_present[chat_id] = 0
                print('give_present')
                app.send_video(chat_id, f"gifs/{hearts[give_present[chat_id]]}hearts.mp4",
                               f"{hearts[give_present[chat_id]]}❤",
                               reply_markup=InlineKeyboardMarkup(buttons))
        else:
            print('nite2')
            callback_query.answer('Sən bu istifadəçi ilə çatlaşmırsan!', show_alert=True)

    elif query_data == 'next_heart':
        if give_present.get(chat_id) is not None:
            buttons = [[
                InlineKeyboardButton('➡Növbəti', callback_data='next_heart'),
                InlineKeyboardButton('🔙Geri', callback_data='back_heart')

            ],
                [InlineKeyboardButton('❤Göndər', callback_data='send_heart')]
            ]
            give_present[chat_id] += 1
            if give_present[chat_id] < 13:
                app.edit_message_media(chat_id, callback_query.message.id,
                                       InputMediaVideo(f"gifs/{hearts[give_present[chat_id]]}hearts.mp4"))
                app.edit_message_text(chat_id, callback_query.message.id,
                                      f"{hearts[give_present[chat_id]]}❤", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            print('next_heart')
            callback_query.answer('Çat artıq sonlanıb!', show_alert=True)
    elif query_data == 'back_heart':
        if give_present.get(chat_id) is not None:
            buttons = [[
                InlineKeyboardButton('➡Növbəti', callback_data='next_heart'),
                InlineKeyboardButton('🔙Geri', callback_data='back_heart')

            ],
                [InlineKeyboardButton('❤Göndər', callback_data='send_heart')]
            ]
            if give_present[chat_id] > 0:
                give_present[chat_id] -= 1
                app.edit_message_media(chat_id, callback_query.message.id,
                                       InputMediaVideo(f"gifs/{hearts[give_present[chat_id]]}hearts.mp4"))
                app.edit_message_text(chat_id, callback_query.message.id,
                                      f"{hearts[give_present[chat_id]]}❤", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            callback_query.answer('Çat artıq sonlanıb!', show_alert=True)
    elif query_data == 'send_heart':
        if give_present.get(chat_id) is not None:
            biriliant = database.execute(F"SELECT Biriliant FROM Users WHERE ID={chat_id}").fetchone()[0]
            total = hearts[give_present[chat_id]]
            if biriliant < total:
                callback_query.answer(
                    f'Bu hədiyyəni göndərmək üçün balansınızda ən azı {total}💎 olmalıdır\nBalansınızı artırmaq üçün aşağıdan 💎 Al-a daxil olun və hesabı artırın.',
                    show_alert=True)
                app.send_video(
                    chat_id,
                    'gifs/biriliant.mp4',
                    caption=f'Bu hədiyyəni göndərmək üçün balansınızda ən azı {total} 💎 olmalıdır.Balansınızı artırmaq üçün aşağıdan 💎 Al-a daxil olun və hesabı artırın.',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('💎Al', callback_data='buy_biriliant')]
                    ])
                )
        else:
            callback_query.answer('Çat artıq sonlanıb!', show_alert=True)
    elif query_data == 'change_search_user':
        if current_chat(chat_id):
            app.send_message(chattings[chat_id],
                             F'**Söhbət qarşı tərəfdən dayandırıldı yeni söhbət üçün /search edin**')
            stop(chat_id)
            search_(chat_id)
        else:
            callback_query.answer('Çat artıq sonlanıb!', show_alert=True)

    elif query_data == 'report':
        if current_chat(chat_id):
            app.send_message(5420622167, f"{chattings[chat_id]} report gəldi")
            callback_query.answer('Adminstatorlara göndərildi.')
        else:
            callback_query.answer('Çat artıq sonlanıb!', show_alert=True)


app.run()