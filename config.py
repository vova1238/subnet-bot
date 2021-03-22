# імпортування модулю telebot
import telebot as tb

# Токен бота
TOKEN = "some token"

# Створення екземпляру бота
bot = tb.TeleBot(TOKEN)

# Список всіх пунктів меню
all_menus = {
    'home':'Домівка',
    'location':'Місцезнаходження IP',
    'info':'Інфо про IP',
    'subnets':'Рахувати підмережі',
    'hosts':'Рахувати хости',
    'summation':'Cумування підмереж',
}

