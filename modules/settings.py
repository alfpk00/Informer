# from modules import functions as func
from dataclasses import dataclass
import pymysql
from datetime import datetime

# TODO: Не забыть убрать!!!!
# Настройки поздравлений ########################################################################
NEW_YEAR = "10.01"  # Дата НГ
NEW_YEAR_FILE = "new_year"  # Имя файла открытки с НГ

OLD_NEW_YEAR = "14.01"  # Дата старого НГ
OLD_NEW_YEAR_FILE = "old_new_year"  # Имя файла открытки со старым НГ

CHRISTMAS = "07.01"  # Дата Рождества
CHRISTMAS_FILE = "christmas"  # Имя файла открытки с Рождеством

SEND_INTERVAL = 30  # Интервал отправки множественных поздравлений

# Настройки документов ##########################################################################
USTAV_FILE = "Устав OST MC"  # Имя файла с Уставом
KODEKS_FILE = "Кодекс OST MC"  # Имя файла с Кодексом


def get_timestamp():  # Получаем текущее значение даты/времени в формате dd.mm.yy hh:mm
    today = datetime.now()
    return today.strftime("%d.%m.%y - %H:%M:%S - ")


@dataclass
class DB:
    with open("conf/db.conf") as conf_db:
        for row in conf_db:
            row = row.rstrip("\n")
            name = row[: row.find(":")]
            if name == "Host":
                Host: str = row[row.find(":") + 1 :]
            elif name == "User":
                User: str = row[row.find(":") + 1 :]
            elif name == "Passwd":
                Passwd: str = row[row.find(":") + 1 :]
            elif name == "DBName":
                Name: str = row[row.find(":") + 1 :]


class TLG:
    connection = pymysql.connect(host=DB.Host, user=DB.User, passwd=DB.Passwd, database=DB.Name)
    with connection:
        cursor = connection.cursor()
        retrive = "SELECT * FROM `settings` WHERE node ='tlg'"

        cursor.execute(retrive)
        rows = cursor.fetchall()
        for row in rows:
            name = row[2]  # noqa: F523
            value = row[3]  # noqa: F523
            if name == "Token":
                Token: str = value
            elif name == "ChatID":
                ChatID: str = value
            elif name == "AdminID":
                AdminID: str = value
            elif name == "LogChatID":
                LogChatID: str = value
            else:
                log = open("./log/error.log", "a")
                error_msg = "***ERROR***: " + get_timestamp() + "Неизвестный параметр: " + name
                log.write(error_msg + "\n")
                log.close()
                exit()


class GREET:
    connection = pymysql.connect(host=DB.Host, user=DB.User, passwd=DB.Passwd, database=DB.Name)
    with connection:
        cursor = connection.cursor()
        retrive = "SELECT * FROM `settings` WHERE node ='grit'"

        cursor.execute(retrive)
        rows = cursor.fetchall()
        for row in rows:
            name = row[2]  # noqa: F523
            value = row[3]  # noqa: F523
            if name == "SendInterval":
                SendInterval: str = value
            else:
                log = open("./log/error.log", "a")
                error_msg = "***ERROR***: " + get_timestamp() + "Неизвестный параметр: " + name
                log.write(error_msg + "\n")
                log.close()
                exit()


class COM:
    connection = pymysql.connect(host=DB.Host, user=DB.User, passwd=DB.Passwd, database=DB.Name)
    with connection:
        cursor = connection.cursor()
        retrive = "SELECT * FROM `settings` WHERE node ='common'"

        cursor.execute(retrive)
        rows = cursor.fetchall()
        for row in rows:
            name = row[2]  # noqa: F523
            value = row[3]  # noqa: F523
            if name == "ImagePath":
                ImagePath: str = value
            elif name == "PdfPath":
                PdfPath: str = value
            elif name == "RequiredPythonVersion":
                RequiredPythonVersion: str = value
            elif name == "SilentMode":
                SilentMode: str = value
            elif name == "Version":
                Version: str = value
            else:
                log = open("./log/error.log", "a")
                error_msg = "***ERROR***: " + get_timestamp() + "Неизвестный параметр: " + name
                log.write(error_msg + "\n")
                log.close()
                exit()


class DEV:
    connection = pymysql.connect(host=DB.Host, user=DB.User, passwd=DB.Passwd, database=DB.Name)
    with connection:
        cursor = connection.cursor()
        retrive = "SELECT * FROM `settings` WHERE node ='dev'"

        cursor.execute(retrive)
        rows = cursor.fetchall()
        for row in rows:
            name = row[2]  # noqa: F523
            value = row[3]  # noqa: F523
            if name == "DevFlagPath":
                DevFlagPath: str = value
            elif name == "VersionPath":
                VersionPath: str = value
            else:
                log = open("./log/error.log", "a")
                error_msg = "***ERROR***: " + get_timestamp() + "Неизвестный параметр: " + name
                log.write(error_msg + "\n")
                log.close()
                exit()
