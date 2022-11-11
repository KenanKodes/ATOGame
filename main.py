# -*- coding: utf-8 -*-
import logging

import telegram
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ParseMode, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ParseMode

from game import Game
import settings

rating_dict = {}

logger = None

games = {}


def get_or_create_game(chat_id: int) -> Game:
    global games
    game = games.get(chat_id, None)
    if game is None:
        game = Game()
        games[chat_id] = game

    return game


def setup_logger():
    global logger
    file_handler = logging.FileHandler('crocodile.log', 'w', 'utf-8')
    stream_handler = logging.StreamHandler()
    logger = logging.getLogger("main_log")
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def help(update, context):
    update.message.reply_text('Mövcud əmrlər:\n' +
                              '/start - Botu Başlad\n' +
                              '/game - Yeni oyun başladmaq\n' +
                              '/help - Əmirlərə Bax\n' +
                              '/sudo - Sahibləri Görmək\n' +
                              '/master - Aparıcı Olmaq\n' +
                              '/word - Aparıcı Sözü Göstərər\n' +
                              '/sword - Aparıcı Sözü Dəyişər Və Göstərər\n' +
                              '/rating - Qrup Üzrə Reytinq', reply_to_message_id=True)

def sudo(update, context):
    update.message.reply_text('⭐️Sahiblər:\n\n' +
                              '1➤ @KenandiBrat_01\n' +
                              '2➤ @ll_Lonely_ll', reply_to_message_id=True)

def button(update, context):
    user_id = update.callback_query.from_user.id
    chat_id = update.callback_query.message.chat_id
    bot = telegram.Bot(token=settings.TOKEN)

    game = get_or_create_game(chat_id)

    query = update.callback_query

    if query.data == 'word':
        word = game.get_word(user_id)
        if game.is_master(query.from_user.id):
            bot.answer_callback_query(callback_query_id=query.id, text=word, show_alert=True)

    if query.data == 'sword':
        word = game.change_word(user_id)
        if game.is_master(query.from_user.id):
            bot.answer_callback_query(callback_query_id=query.id, text=word, show_alert=True)
    

def command_start(update, context: CallbackContext):
    if update.effective_chat.type == "private":
        
        addme = InlineKeyboardButton(text="➕ 𝑸𝑼𝑹𝑼𝑷𝑨 𝑬𝑳𝑨𝑽𝑬 𝑬𝑻 ➕", url="http://t.me/ATO_GAME_Bot?startgroup=a") 
        sohbet = InlineKeyboardButton(text="⛑ 𝑫𝑬𝑺𝑻𝑬𝑲 𝑸𝑼𝑹𝑼𝑷𝑼𝑴𝑼𝒁", url="https://t.me/ATOSupport") 
        oyun = InlineKeyboardButton(text="📲 𝒀𝑬𝑵𝒊𝑳𝒊𝑲𝑳𝑬𝑹 𝑲𝑨𝑵𝑨𝑳𝑰", url="https://t.me/ATO_RESMl") 
        admin = InlineKeyboardButton(text="ℹ️ 𝑨𝑻𝑶 𝑩𝑶𝑻𝑳𝑨𝑹𝑰", url="https://t.me/ATOBots") 

        keyboard = [[addme],[sohbet],[oyun],[admin]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Salam!👋 Mən sizin qurupunuzda insan adları tapmağ üçün yaradılmış Oyun botuyam. Məni qurupa əlavə edərək oynaya bilərsiz.', reply_to_message_id=True, reply_markup=reply_markup)
    else:
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        username = update.message.from_user.full_name

        logger.info('Got command /game,'
                    'chat_id={},'
                    'user_id'.format(chat_id,
                                     user_id))

        game = get_or_create_game(chat_id)
        game.start()

        update.message.reply_text('Ad Oyunu Başladı ⚡'.format(username), reply_to_message_id=True) 

        set_master(update, context)


def set_master(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.full_name
    logger.info('chat_id={}, New master is "{}"({})'.format(chat_id,
                                                            username,
                                                            update.message.from_user.id))

    game = get_or_create_game(chat_id)

    game.set_master(update.message.from_user.id)

    show_word_btn = InlineKeyboardButton("✅ Ada bax", callback_data='word') 
    change_word_btn = InlineKeyboardButton("🔄 Adı dəyiş", callback_data='sword') 
    
    keyboard = [[show_word_btn], [change_word_btn]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('{} adı başa salır'.format(username,user_id), reply_to_message_id=True, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


def command_master(update: Update, context):
    chat_id = update.message.chat.id
    game = get_or_create_game(chat_id)
    username = update.message.from_user.full_name
    user_id = update.message.from_user.id

    if not game.is_game_started():
        return

    if not game.is_master_time_left():
        update.message.reply_text('Aparıcı olmaq üçün {} saniyə qalıb ⏳'.format(game.get_master_time_left()),
                                  reply_to_message_id=True)
        return

    logger.info('Got command /master,'
                'chat_id={},'
                'user="{}"({}),'
                'timedelta={}'.format(chat_id,
                                      username,
                                      user_id,
                                      game.get_master_time_left()))

    update.message.reply_text(word, reply_to_message_id=True)


def command_word(update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    game = get_or_create_game(chat_id)
    word = game.get_word(user_id)

    logger.info('Got command /word, ' 
                'chat_id={}, '
                'user="{}"({}),'
                'is_user_master={},'
                'word={}'.format(chat_id,
                                 update.message.from_user.full_name,
                                 update.message.from_user.id,
                                 game.is_master(user_id),
                                 word))

    update.message.reply_text(word, reply_to_message_id=True)


def command_sword(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id

    game = get_or_create_game(chat_id)

    word = game.change_word(user_id)

    logger.info('Got command /sword,'
                'chat_id={},'
                'user="{}"({}),'
                'is_user_master={},'
                'word={}'.format(chat_id,
                                 update.message.from_user.full_name,
                                 user_id,
                                 game.is_master(user_id),
                                 word))

    update.message.reply_text(word, reply_to_message_id=True)


def command_rating(update, context):
    chat_id = update.message.chat.id

    game = get_or_create_game(chat_id)

    rating_str = game.get_str_rating()

    logger.info('Got command /rating,'
                'chat_id={},'
                'rating={}'.format(update.message.chat.id,
                                   rating_str))

    update.message.reply_text(rating_str, reply_to_message_id=True)


def is_word_answered(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.full_name
    text = update.message.text

    game = get_or_create_game(chat_id)

    word = game.get_current_word()

    if game.is_word_answered(user_id, text):
        update.message.reply_text('*{}* adını {} tapdı 🔥'.format(word, username,user_id), reply_to_message_id=True, parse_mode=ParseMode.MARKDOWN)

        game.update_rating(user_id, username)

        set_master(update, context)

    logger.info('Guessing word,'
                'chad_id={},'
                'user="{}"({}),'
                'is_master={},'
                'text="{}",'
                'word="{}"'.format(update.message.chat.id,
                                   update.message.from_user.full_name,
                                   update.message.from_user.id,
                                   game.is_master(user_id),
                                   text,
                                   word))


def main():
    setup_logger()

    updater = Updater(settings.TOKEN, use_context=True)

    bot = updater.bot

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("game", command_start))
    dp.add_handler(CommandHandler("master", command_master))
    dp.add_handler(CommandHandler("sword", command_sword))
    dp.add_handler(CommandHandler("word", command_word))
    dp.add_handler(CommandHandler("rating", command_rating))
    dp.add_handler(CommandHandler("sudo", sudo))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", command_start))

    dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(MessageHandler(Filters.text, is_word_answered))

    updater.start_polling()

    updater.idle()


@client.on(events.NewMessage(pattern="^/reload ?(.*)"))
async def reload(event):
    await client.send_message(event.chat_id, "♻️ **Bot yenidən başladıldı**\n✅ **Admin siyahısı yeniləndi** ")

@client.on(events.NewMessage(pattern="^/elaqe ?(.*)"))
async def elaqe(event):
    await client.send_message(event.chat_id, "🌍**Əlaqə Üçün yaz:** @KenandiBrat_01")


if __name__ == '__main__':
    main()
