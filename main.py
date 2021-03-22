# імпортування компонентів з файлу view.py
from view import start_home, home, location, info, subnets, hosts, sum_menu, user_dict
# імпортування компонентів з файлу config.py
from config import tb, bot, all_menus
# імпортування класу з файлу user_class.py
from user_class import User

# імпортування вмонтованих модулів Python
from threading import Thread
import time
from shutil import rmtree
import os
import pickle

# Функція яка відповідає за очищення файлів згенерованих користувачами в результаті роботи
def user_cleanup(users):
    global stop_cleanup_thread
    while not stop_cleanup_thread:
        for user in users.values():
            if user.expire_time:
                if user.expire_time < time.time():
                    # print(f'Cleaning...\nTime: {time.time()}\nTime expieres: {user.expire_time}')
                    dirname = os.path.dirname(__file__)
                    path = os.path.join(dirname, 'user_data', str(user.id))
                    if os.path.exists(path):
                        try:
                            rmtree(path)
                            user.expire_time = None
                            print("File deleted")
                            break
                        except PermissionError:
                            print('Exception')
                            continue
        time.sleep(3)

# обробник команди /start
@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = message.chat.id
    # Creating user instance
    user = User(chat_id)
    user_dict[chat_id] = user
    # Set menu
    user.set_menu('home')
    start_home(message)
    
# обробник всього надісланого тексту
@bot.message_handler(content_types=['text'])
def main(message):

    # Якщо повідомлення надіслано приватно боту
    if message.chat.type == 'private':
        # Встановлення змінної меню в залежності від надісланого тексту
        if message.text in all_menus.values():
            # Перевірка чи користувач вже існує в словнику
            if message.chat.id in user_dict:
                # Визначення з яким користувачем взаємодіє бот
                user = user_dict[message.chat.id]
                # Пошуку ключа у словнику та встановлення меню для окремого користувача
                user.set_menu(list(all_menus.keys())[list(all_menus.values()).index(message.text)])
                print(message.from_user.first_name ,'menu:', user.menu)
                

                # Запуск відповідної функції в залежності від вибраного меню

                # Домівка
                if user.menu == 'home':
                    home(message)

                # Місцезнаходження IP
                if user.menu == 'location':
                    location(message)

                # Інфо про IP
                if user.menu == 'info':
                    info(message)

                # Рахувати підмережі
                if user.menu == 'subnets':
                    subnets(message)

                # Рахувати хости
                if user.menu == 'hosts':
                    hosts(message)

                # Cумування підмереж
                if user.menu == 'summation':
                    sum_menu(message)
            
            # Якщо користувач ще не користувався ботом
            else:
                # Створення об'єкту користувача та запис його у словник 
                user = User(message.chat.id)
                user_dict[message.chat.id] = user
                user.set_menu('home')
                # bot.send_message(message.chat.id, f'User with id {message.chat.id} - does not exist!')
                main(message)
        else:
            bot.send_message(message.chat.id, 'Невірна кнопка')

# Обробник отриманих аудіо повідомлень
@bot.message_handler(content_types=['audio','voice'])
def handle_audio(message):
	bot.send_message(message.chat.id, 'Нічого не зрозумів, повторіть будь ласка 😂')

# Обробник отриманих файлів
@bot.message_handler(content_types=['document'])
def handle_docs(message):
	bot.send_message(message.chat.id, 'Вибачте, але я не відкриваю файли з неперевірених джерел')

# Обробник отриманих фотографій
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, 'Дуже гарно')

# Якщо файл запускається напряму
if __name__ == '__main__':
    try:
        # Запуск потоку очистки
        print("Pshhhhhssss... cleaning")
        stop_cleanup_thread = False
        cleanup_thread = Thread(target = user_cleanup, args=(user_dict,))
        cleanup_thread.start()

        # Ввімкнення збереження обробника наступного кроку у файл "./.handlers-saves/step.save".
        # Збереження відбувається з затримкою в 2 секунди.
        bot.enable_save_next_step_handlers(delay=2)
        # Завантаження обробника наступного кроку з файлу "./.handlers-saves/step.save".
        bot.load_next_step_handlers()
        # Запуск пулінгу бота
        bot.polling(none_stop=True)
        
    # Вимкнення бота
    except KeyboardInterrupt:
        print('Im leaving!')
        # Зупинка потоку очистки
        stop_cleanup_thread = True
        
        # Збереження стану користувача
        with open('users.pickle', 'wb') as handle:
            pickle.dump(user_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print('Saved: ', user_dict)

        # Зупинка пулінгу бота
        bot.stop_polling()