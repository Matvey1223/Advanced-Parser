import telebot
from telebot import types
from crypto_pay_api_sdk import cryptopay
import sqlite3
from apscheduler.schedulers.base import BaseScheduler



bot = telebot.TeleBot(token = '6682924404:AAEtX6wYskAwc9vc9x4kkI8Wx6oOp1Z-JMc')
invoice_info = []
Crypto = cryptopay.Crypto(token='8722:AAnXwnxAfOYxMkfXSkrixl3nMrtdbXZyS1F', testnet=True)
conn = sqlite3.connect('users.db', check_same_thread=False)
cur = conn.cursor()  # db create
invoice_id = ''
invoice_p = ''
scheduler = BaseScheduler()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global conn, cur
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Парсер', callback_data = 'Парсер')
    btn2 = types.InlineKeyboardButton('🎰 Пополнить баланс', callback_data='🎰 Пополнить баланс')
    btn3 = types.InlineKeyboardButton('Настройки', callback_data='Настройки')
    btn4 = types.InlineKeyboardButton('Тарифы', callback_data='Тарифы')
    markup.row(btn1)
    markup.row(btn2, btn3)
    markup.row(btn4)

    bot.send_message(message.chat.id, f'Добро пожаловать, в парсинг бота, {message.from_user.first_name}\nВаш баланс: 0',reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_inline(callback):
    global invoice_info, Crypto, conn, cur, invoice_id, invoice_p
    if callback.data == '🎰 Пополнить баланс':
        bot.send_message(callback.message.chat.id, text = 'Введите сумму пополнения для подключения подписки на нужный вам период')
    if callback.data == 'Настройки':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Назад', callback_data='Назад')
        markup.row(btn1)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Ваши настройки", reply_markup=markup)
    if callback.data == 'Назад':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Парсер', callback_data='Парсер')
        btn2 = types.InlineKeyboardButton('🎰 Пополнить баланс', callback_data='🎰 Пополнить баланс')
        btn3 = types.InlineKeyboardButton('Настройки', callback_data='Настройки')
        btn4 = types.InlineKeyboardButton('Тарифы', callback_data='Тарифы')
        markup.row(btn1)
        markup.row(btn2, btn3)
        markup.row(btn4)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text=f'Добро пожаловать, в парсинг бота, {callback.from_user.first_name}\nВаш баланс: 0.0', reply_markup=markup)
    if callback.data == 'Тарифы':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('1 день/ 2.5$', callback_data='1 день/ 2.5$')
        btn2 = types.InlineKeyboardButton('3 дня/ 8$', callback_data='3 дня/ 8$')
        btn3 = types.InlineKeyboardButton('Неделя/ 18$', callback_data='Неделя/ 18$')
        btn4 = types.InlineKeyboardButton('Месяц/ 40$', callback_data='Месяц/ 40$')
        btn5 = types.InlineKeyboardButton('Назад', callback_data='Назад')
        markup.row(btn1)
        markup.row(btn2)
        markup.row(btn3)
        markup.row(btn4)
        markup.row(btn5)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Тарифы", reply_markup=markup)

    if callback.data in  ('BTC', 'USDT', 'TON', 'ETH', 'BNB'):
        invoice_info.append(callback.data)
        invoice = Crypto.createInvoice(asset = invoice_info[1], amount = invoice_info[0])
        bot.send_message(chat_id=callback.message.chat.id, text = f'Вы можете оплатить по данной ссылке: {invoice["result"]["pay_url"]}')
        print(invoice)
        invoice_id = str(invoice['result']['invoice_id'])
        user = (str(callback.message.chat.id), 0.0)
        cur.execute(
            """CREATE TABLE IF NOT EXISTS users(userid TEXT UNIQUE,balance REAL);""")  # create columns
        conn.commit()  # saving
        cur.execute("INSERT OR IGNORE INTO users VALUES (?,  ?);", user)  # add user
        conn.commit()  # saving
        invoice_p = invoice
    invoice_info = []


@bot.message_handler(content_types=['text'])
def paying(message):
    global invoice_info, invoice_id, Crypto
    if float(message.text) >= 0.1:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('USDT', callback_data='USDT')
        btn2 = types.InlineKeyboardButton('TON', callback_data='TON')
        btn3 = types.InlineKeyboardButton('BTC', callback_data='BTC')
        btn4 = types.InlineKeyboardButton('ETH', callback_data='ETH')
        btn5 = types.InlineKeyboardButton('BNB', callback_data='BNB')
        markup.row(btn1)
        markup.row(btn2)
        markup.row(btn3)
        markup.row(btn4)
        markup.row(btn5)
        invoice_info.append(message.text)
        bot.send_message(message.chat.id, text = 'Выберите криптовалюту в которой хотите произвести оплату', reply_markup=markup)



scheduler.add_job(callback_inline, "interval", seconds=5)
scheduler.start()


bot.infinity_polling()
