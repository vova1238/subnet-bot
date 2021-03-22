# імпортування модулів регулярного виразу та часу
import re
import time

class User:
    def __init__(self, id):
        self.id = id
        self.menu = ''
        self.ip = None
        self.expire_time = None        

    # Метод встановлення меню користувача
    def set_menu(self, menu):
        self.menu = menu

    # Метод встановлення ip-адреси з якою працює користувач
    def set_ip(self, ip):
        # Якщо ip-адреса не дійсна виводится повідомлення про помилку
        if re.match(r'^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$', ip):
            self.ip = ip
        else:
            raise ValueError(f'{ip} is invalid IP!')

    # Метод встановлення терміну зберігання інформації
    def set_expire_time(self):
        self.expire_time = time.time() + 60
