import telebot
import sqlite3
from crypto_pay_api_sdk import cryptopay

bot = telebot.TeleBot(token = '6572219230:AAH83Vz3Tows4TahB2ZXwaNFpYvTMMIJKXE')
conn = sqlite3.connect('users.db', check_same_thread=False)
Crypto = cryptopay.Crypto(token='8722:AAnXwnxAfOYxMkfXSkrixl3nMrtdbXZyS1F', testnet=True)
cur = conn.cursor()


cur.execute("""SELECT * FROM users""")
invoice_id = cur.fetchone()[-1]
invoice_info = Crypto.getInvoices(params = {"invoice_ids" : int(invoice_id)})
print(invoice_info)
