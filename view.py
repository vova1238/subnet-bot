# імпортування компонентів з файлу calculator.py
from calculator import is_valid_ip, is_valid_mask, mask2cidr, ip2network_address, subnetting, ip_str2list, summation
# імпортування компонентів з файлу config.py
from config import tb, bot, all_menus
# імпортування класу з файлу user_class.py
from user_class import User

# імпортування вмонтованих модулів Python
import csv
import os
import pickle

# Завантаження списку користувачів
if os.path.isfile('users.pickle'):
    with open('users.pickle', 'rb') as handle:
        user_dict = pickle.load(handle)
    print('Loaded dict: ', user_dict)
else:
    user_dict = {}

# Налаштування розмітки клавіатури бота

# Функція створення клавіатури зі списку
def create_keyboard(keys: list, row_width: int = 2):
    keyboard= []
    for key in keys:
        keyboard.append(tb.types.KeyboardButton(key))
    return tb.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width).add(
        *keyboard)

# Розмітка головного меню
menu_markup = create_keyboard(keys = list(all_menus.values())[1:], row_width = 2)

# Розмітка для всіх інших меню
back_mp = create_keyboard(keys = ['Домівка'])

# Функція надсилання результату обчислень у зручній для використання формі
def render(message, mode, content, detail = False):
    """
    Render bot answer
    input:
    message,
    mode: 'info' 'by_subnets' 'by_hosts' 'summation',
    content: content to display,
    detail: True if there are some details
    Sends message to user
    """
    headers_dict = {
             'info':{'avail_hosts':'Доступні хости',
                     'netmask':'Маска мережі',
                     'network_address':'Адреса мережі',
                     'first_avail_ip':'Перша доступна адреса',
                     'last_avail_ip':'Остання доступна адреса',
                     'broadcast_address':'Широкомовна адреса'},

       'by_subnets':{'cidr':'Префікс',
                     'class':'Клас',
                     'type':'Тип',
                     'subnet_amount':'Кількість підмереж',
                     'network_address_list':'Список адрес',
                     'avail_hosts':'Доступних хостів'},

         'by_hosts':{'cidr':'Префікс',
                     'class':'Клас',
                     'type':'Тип',
                     'subnet_amount':'Кількість підмереж',
                     'network_address_list':'Список адрес',
                     'avail_hosts':'Доступних хостів'},
        'summation':{'cidr':'Префікс',
                     'bin_ip':'Двійкова адреса',
                     'avail_hosts':'Доступні хости',
                     'netmask':'Маска мережі',
                     'network_address':'Адреса мережі',
                     'first_avail_ip':'Перша доступна адреса',
                     'last_avail_ip':'Остання доступна адреса',
                     'broadcast_address':'Широкомовна адреса'},
    }

    header = headers_dict[mode]
    network_address_list = [] 
    output = ''
    if mode in headers_dict.keys():
        for param, each in zip(header.values(),content):
            if type(each) is not list:
                output += param + ': ' + str(each) + '\n'
            else:
                network_address_list = each
                cidr = content[0]
                output += param + ': ' + 'Деталі нижче\n'
        bot.send_message(message.chat.id, output)
        if detail:
            if 10 > len(network_address_list) > 0:
                for each_subnet in network_address_list:
                    render(message, 'info', ip2network_address(each_subnet, cidr))
                    detail = False
            else:
                dirname = os.path.dirname(__file__)
                file_path = os.path.join(dirname, 'user_data', str(message.chat.id), 'subnets.csv')
                # Створення папки користувача
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wt', newline='') as csvfile:
                    csvfile.write('"sep=,"\n')
                    filewriter = csv.writer(csvfile, delimiter = ',')
                    filewriter.writerow(list(headers_dict['info'].values()))
                    for each_subnet in network_address_list:
                        filewriter.writerow(list(ip2network_address(each_subnet, cidr)))
                
                user = user_dict[message.chat.id]
                user.set_expire_time()

                if os.stat(file_path).st_size > 52428800:
                    bot.send_message(message.chat.id, "Сталася помилка: Створений файл завеликий для відправки")
                else:
                    with open(file_path, 'rb') as file2send:
                        bot.send_document(message.chat.id, file2send)
                

# Функції для кожного меню

# Відправка вітального повідомлення та встановлення розмітки
def start_home(message):
    # Розмітка для головного меню
    global menu_markup
    dirname = os.path.dirname(__file__)
    file_path = os.path.join(dirname, 'images', 'icon.png')
    with open(file_path, 'rb') as icon:
        bot.send_photo(message.chat.id, icon, f"Ласкаво просимо, {message.from_user.first_name}!\n"+
                                                f"Я - <b>{bot.get_me().first_name}</b> - бот призначений для роботи з IP-адресами.",
                                                parse_mode='html',
                                                reply_markup=menu_markup)

    bot.send_message(message.chat.id,   "Я вмію:\n"+
                                        "-Показувати інформацію про ip\n"+
                                        "-Відображати місцезнаходження ip\n"+
                                        "-Підраховувати підмережі\n"+
                                        "-Агрегувати (сумувати) підмережі")



# Відправка повідомлення головного меню та встановлення розмітки
def home(message):
    # Розмітка для головного меню
    global menu_markup
    global all_menus
    
    bot.send_message(message.chat.id,
                    'Головне меню',
                    reply_markup=menu_markup)

    # Якщо це не команда меню вивести повідомлення
    if not message.text in all_menus.values():
        bot.send_message(message.chat.id, f'Я не знаю що відповісти на "{message.text}"')


# Відправка повідомлення меню Місцезнаходження IP та встановлення розмітки
def location(message):
    """
    Shows location menu caption and changes keyboard markup
    """         
    global back_mp
    msg = bot.send_message(message.chat.id, 'Введіть айпі адресу\n'+
                                            'Наприклад 172.16.254.1',
                                            reply_markup=back_mp)

    bot.register_next_step_handler(msg, process_ip_location)

# Відправка повідомлення підменю Місцезнаходження IP
def process_ip_location(message):
    try:
        # Якщо IP введено правильно 
        if is_valid_ip(message.text):
            # Надіслати відповідь
            info_message = f'Розташування IP адреси доступне за посиланням: https://ipapi.co/{message.text}/'
            bot.send_message(message.chat.id, info_message)
        
        # Якщо натиснуто на кнопку - повернення в головне меню
        elif message.text == 'Домівка':
            home(message)
        else:
            msg = bot.send_message(message.chat.id, 'Невірно введено IP')
            bot.register_next_step_handler(msg, process_ip_location)

    except Exception as e:
        bot.reply_to(message, f'При обробці повідомлення сталася помилка\n{e}')


# Відправка повідомлення меню Інфо про IP та встановлення розмітки
def info(message):      
    global back_mp
    msg = bot.send_message(message.chat.id, 'Введіть айпі адресу\n'+
                                            'Наприклад 172.16.254.1',
                                            reply_markup=back_mp)

    bot.register_next_step_handler(msg, process_ip4info)

# Відправка повідомлення підменю Інфо про IP
def process_ip4info(message):
    try:
        # Отримання користувача за його id
        user = user_dict[message.chat.id]
        # Якщо IP введено правильно перейти до наступного кроку
        if is_valid_ip(message.text):
            # Збереження значення IP
            user.ip = message.text
            msg = bot.send_message(message.chat.id, 'Введіть маску мережі\n'+
                                                    'Наприклад: 255.255.240.0 або 28\n')
            bot.register_next_step_handler(msg, process_mask4info)

        elif message.text == 'Домівка':
            home(message)
        else:
            msg = bot.send_message(message.chat.id, 'Невірно введено IP')
            bot.register_next_step_handler(msg, process_ip4info)

    except Exception as e:
        bot.reply_to(message, f'При обробці повідомлення сталася помилка\n{e}')

# Відправка повідомлення підменю Інфо про IP
def process_mask4info(message):
    try:
        # Отримання користувача за його id
        user = user_dict[message.chat.id]
        # Визначення змінної якщо введено число
        num = int(message.text) if message.text.isdecimal() else -1

        # Якщо маску введено правильно
        if is_valid_mask(message.text):
            mask = mask2cidr(message.text)
            render(message, 'info', ip2network_address(user.ip, mask))

        # Якщо префікс введено правильно
        elif 0 < num < 33:
            render(message, 'info', ip2network_address(user.ip, num))

        elif message.text == 'Домівка':
            home(message)
        else:
            msg = bot.send_message(message.chat.id, 'Невірно введено маску')
            bot.register_next_step_handler(msg, process_mask4info)
            
    except Exception as e:
        bot.reply_to(message, f'При обробці повідомлення сталася помилка\n{e}')


# Відправка повідомлення меню "Рахувати підмережі" та встановлення розмітки
def subnets(message):      
    global back_mp
    msg = bot.send_message(message.chat.id, 'Введіть айпі адресу\n'+
                                            'Наприклад 172.16.254.1',
                                            reply_markup=back_mp)

    bot.register_next_step_handler(msg, process_ip4subnets)

# Відправка повідомлення підменю "Рахувати підмережі"
def process_ip4subnets(message):
    try:
        # Отримання користувача за його id
        user = user_dict[message.chat.id]
        # Якщо IP введено правильно
        if is_valid_ip(message.text):
            user.set_ip(message.text)
            msg = bot.send_message(message.chat.id, 'Введіть кількість хостів\n'+
                                                    'Наприклад: 25\n')
            bot.register_next_step_handler(msg, process_amount4subnets)

        elif message.text == 'Домівка':
            home(message)
        else:
            msg = bot.send_message(message.chat.id, 'Невірно введено IP')
            bot.register_next_step_handler(msg, process_ip4subnets)

    except Exception as e:
        bot.reply_to(message, f'При обробці повідомлення сталася помилка\n{e}')

# Відправка повідомлення підменю "Рахувати підмережі"
def process_amount4subnets(message):
    try:
        # Отримання користувача за його id
        user = user_dict[message.chat.id]

        num = int(message.text) if message.text.isdecimal() else -1

        if 0 < num < 4000000000:
            content = subnetting(user.ip, host_amount = num)
            render(message, 'by_hosts', content, True)

        elif message.text == 'Домівка':
            home(message)
        else:
            msg = bot.send_message(message.chat.id, 'Невірно введено кількість хостів')
            bot.register_next_step_handler(msg, process_amount4subnets)

    except Exception as e:
        bot.reply_to(message, f'При обробці повідомлення сталася помилка\n{e}')


# Відправка повідомлення меню "Рахувати хости" та встановлення розмітки
def hosts(message):
    global back_mp
    msg = bot.send_message(message.chat.id, 'Введіть айпі адресу\n'+
                                            'Наприклад 172.16.254.1',
                                            reply_markup=back_mp)

    bot.register_next_step_handler(msg, process_ip4hosts)

# Відправка повідомлення підменю "Рахувати хости"
def process_ip4hosts(message):
    try:
        # Отримання користувача за його id
        user = user_dict[message.chat.id]
        # Якщо IP введено правильно
        if is_valid_ip(message.text):
            user.set_ip(message.text)
            msg = bot.send_message(message.chat.id, 'Введіть кількість підмереж\n'+
                                                    'Наприклад: 25\n')
            bot.register_next_step_handler(msg, process_amount4hosts)

        elif message.text == 'Домівка':
            home(message)
        else:
            msg = bot.send_message(message.chat.id, 'Невірно введено IP')
            bot.register_next_step_handler(msg, process_ip4hosts)

    except Exception as e:
        bot.reply_to(message, f'При обробці повідомлення сталася помилка\n{e}')

# Відправка повідомлення підменю "Рахувати хости"
def process_amount4hosts(message):
    try:
        # Отримання користувача за його id
        user = user_dict[message.chat.id]

        message_str = message.text
        num = int(message_str) if message_str.isdecimal() else -1

        if 0 < num < 4000000000:
            content = subnetting(user.ip, host_amount = num)
            render(message, 'by_subnets', content, True)
        
        elif message.text == 'Домівка':
            home(message)
        else:
            msg = bot.send_message(message.chat.id, 'Невірно введено кількість підмереж')
            bot.register_next_step_handler(msg, process_amount4hosts)
            
    except Exception as e:
        bot.reply_to(message, f'При обробці повідомлення сталася помилка\n{e}')


# Відправка повідомлення меню "Cумування підмереж" та встановлення розмітки
def sum_menu(message):         
    global back_mp
    msg = bot.send_message(message.chat.id, 
"""
Введіть список IP-адрес із префіксом,
розділених комою (,)
Наприклад:
192.201.240.29/4,
192.170.69.50/4,
192.218.143.51/4,
192.150.23.239/4,
192.215.227.104/4,
192.161.58.59/4,
192.181.131.109/4,
192.226.156.219/4,
192.246.21.104/4,
192.252.152.242/4,
192.178.154.161/4,
""",
    reply_markup=back_mp)

    bot.register_next_step_handler(msg, process_ip4sum)

# Превірка отриманих IP-адрес та відправка повідомлення з результатом обчислень меню "Cумування підмереж"
def process_ip4sum(message):
    try:
        if message.text == 'Домівка':
            home(message)
        else:
            valid_ips, invalid_ips = ip_str2list(message.text)
            if valid_ips:
                render(message, 'summation', summation(valid_ips))
            if invalid_ips:
                invalid_str = ',\n'.join(invalid_ips)
                bot.send_message(message.chat.id, f'Невірно введені IP:\n{invalid_str}')
        
    except Exception as e:
        bot.reply_to(message, f'При обробці повідомлення сталася помилка\n{e}')

