import telebot
import pymysql
import time
import sys
import os
import multiprocessing as multi_proc
import schedule
import hashlib

from datetime import date
from datetime import datetime
from telebot import types

from modules import settings as conf
from templates import greetings as greet, errors as err
from templates import msg


bot = telebot.TeleBot(conf.TLG.Token)  # Инициируем бота


def check_python_version():
    required_version = conf.COM.RequiredPythonVersion
    major, minor, micro, realise_level, serial = sys.version_info
    py_version = f"{major}.{minor}.{micro}"
    if int(major) == int(required_version[0]) and int(minor) >= int(required_version[2:]):
        return py_version
    else:
        bot.send_message(
            conf.TLG.LogChatID,
            err.TITLE_ERROR
            + "\n"
            + get_timestamp()
            + err.ERROR_MSG_VERSION_1
            + py_version
            + "\n"
            + err.ERROR_MSG_VERSION_2
            + required_version,
        )
        bot.send_message(conf.TLG.LogChatID, err.INFO_TITLE + "\n" + get_timestamp() + err.ERROR_MSG_STOP)
        exit()


def get_full_name(fname="", lname="", road_name=""):  # Формируем полное имя
    full_name = f"{fname} {road_name} {lname}"
    return full_name


def calculate_age(born):  # Вычисляем возраст именинника
    today = date.today()
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    if str(age)[1] == "1":
        return f"{str(age)} год"
    elif "1" < str(age)[1] < "5":
        return f"{str(age)} года"
    elif str(age) == "11":
        return f"{str(age)} лет"
    else:
        return f"{str(age)} лет"


def get_message(fullname, bd_date, member_role=""):  # Формируем поздравление
    if fullname[5:11] != "OST MC":
        return (
            f"{greet.GREETING_TITLE}\n{greet.BD_MSG_1} {member_role} "
            f"{greet.BD_MSG_2},\n {fullname}!\n"
            f"{greet.BD_MSG_3} {calculate_age(bd_date)}!\n"
            f"\U0001F382\U0001F943"
            f"\U0001F943\U0001F943\U0001F382\n{greet.BD_MSG_4}"
        )
    else:
        return (
            f"{greet.GREETING_TITLE}\n{greet.OST_BD_MSG_1}"
            f" {calculate_age(bd_date)} {greet.OST_BD_MSG_2} "
            f"{fullname[5:11]}!\n{greet.OST_BD_TOAST}\n\U0001F943"
            f"\U0001F943\U0001F943"
        )


def get_timestamp():  # Получаем текущее значение даты/времени в формате dd.mm.yy hh:mm
    today = datetime.now()
    return today.strftime("%d.%m.%y - %H:%M:%S - ")


def get_year():  # Получаем значение года в формате YYYY
    today = datetime.now()
    return today.strftime(" %Y ")


def send_error_message(err_obj):
    bot.send_message(conf.TLG.LogChatID, err.TITLE_ERROR + "\n" + get_timestamp() + str(err_obj))
    bot.send_message(conf.TLG.LogChatID, err.INFO_TITLE + "\n" + get_timestamp() + err.ERROR_MSG_STOP)
    exit()


def get_path_docs(file_name):  # Формируем путь к документу
    pdf_path = conf.COM.PdfPath + file_name + ".pdf"
    try:
        return open(pdf_path, "rb")
    except Exception as error:
        send_error_message(error)


def get_path_photo(file_name):  # Формируем путь к изображению именника
    return conf.COM.ImagePath + file_name + ".jpg"
    # if os.path.isfile(img_path):
    #    try:
    #        return open(img_path, "rb")
    #    except Exception as error:
    #        send_error_message(error)
    # else:
    #    return None


def post_from_db():  # Получаем данные из БД и постим сообщение
    try:
        connection = pymysql.connect(host=conf.DB.Host, user=conf.DB.User, passwd=conf.DB.Passwd, database=conf.DB.Name)

        with connection:
            cursor = connection.cursor()
            retrive = (
                "SELECT * FROM `bot_bday_registry` WHERE DAYOFYEAR(curdate()) <= "
                "DAYOFYEAR(DATE_ADD(`bday`, INTERVAL (YEAR(NOW()) - YEAR(`bday`)) YEAR))"
                "AND DAYOFYEAR(curdate()) >= DAYOFYEAR(DATE_ADD(`bday`, INTERVAL (YEAR(NOW()) - YEAR("
                "`bday`)) YEAR));"
            )

            cursor.execute(retrive)
            rows = cursor.fetchall()

        flag_pause = 1
        for row in rows:
            name = "{1}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6])  # noqa: F523
            family = "{2}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6])  # noqa: F523
            roadname = "{3}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6])  # noqa: F523
            bday = "{4}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6])  # noqa: F523
            role = "{5}".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6])  # noqa: F523
            s = bday.replace("-", " ")

            date_of_birth = datetime.strptime(s, "%Y %m %d")

            bot.send_photo(
                conf.TLG.ChatID,
                get_path_photo(roadname),
                get_message(get_full_name(name, family, roadname), date_of_birth, role),
            )
            if len(rows) > 1 and len(rows) != flag_pause:
                time.sleep(conf.GREET.SendInterval)
            flag_pause += 1

    except Exception as error:
        send_error_message(error)


def is_admin(user_id):
    if user_id == int(conf.TLG.AdminID):
        return True


def get_date_month():  # Получаем дату в формате dd.mm
    today = datetime.now()
    return today.strftime("%d.%m")


def happy_new_year():  # Поздравляем с Новогодними праздниками и Рождеством
    # TODO: Нужно переписать эту функцию на работу с БД!!!
    try:
        if get_date_month() == conf.NEW_YEAR:
            if os.path.isfile(get_path_photo(conf.NEW_YEAR_FILE)):
                bot.send_photo(
                    conf.TLG.ChatID,
                    open(get_path_photo(conf.NEW_YEAR_FILE), "rb"),
                    greet.GREETING_TITLE + "\n" + greet.NEW_YEAR_MSG_PART_1 + get_year() + greet.NEW_YEAR_MSG_PART_2,
                )
                return True
            else:
                bot.send_message(
                    conf.TLG.ChatID,
                    greet.GREETING_TITLE + "\n" + greet.NEW_YEAR_MSG_PART_1 + get_year() + greet.NEW_YEAR_MSG_PART_2,
                )
                return True
        elif get_date_month == conf.OLD_NEW_YEAR:
            if os.path.isfile(get_path_photo(conf.OLD_NEW_YEAR_FILE)):
                bot.send_photo(
                    conf.TLG.ChatID,
                    open(get_path_photo(conf.OLD_NEW_YEAR_FILE), "rb"),
                    greet.GREETING_TITLE + "\n" + greet.OLD_NEW_YEAR_MSG,
                )
                return True
            else:
                bot.send_message(conf.TLG.ChatID, greet.GREETING_TITLE + "\n" + greet.OLD_NEW_YEAR_MSG)
                return True
        elif get_date_month() == conf.CHRISTMAS:
            if os.path.isfile(get_path_photo(conf.CHRISTMAS_FILE)):
                bot.send_photo(
                    conf.TLG.ChatID,
                    open(get_path_photo(conf.CHRISTMAS_FILE), "rb"),
                    greet.GREETING_TITLE + "\n" + greet.CHRISTMAS,
                )
                return True
            else:
                bot.send_message(conf.TLG.ChatID, greet.GREETING_TITLE + "\n" + greet.CHRISTMAS)
                return True
        else:
            return False
    except Exception as error:
        send_error_message(error)


def greeting():  # Поздравляем с праздниками и именинников
    if not bool(conf.COM.SilentMode):
        bot.send_message(conf.TLG.LogChatID, err.INFO_TITLE + "\n" + get_timestamp() + err.INFO_MSG_START)
    if happy_new_year():
        time.sleep(conf.GREET.SendInterval)
        post_from_db()
    else:
        post_from_db()
    if not bool(conf.COM.SilentMode):
        bot.send_message(conf.TLG.LogChatID, err.INFO_TITLE + "\n" + get_timestamp() + err.INFO_MSG_STOP)


def ai_version_build(version_file):
    if os.path.isfile(conf.DEV.DevFlagPath):
        file = open(version_file)
        ver = str(file.read())
        file.close()
        if ver[: ver.rfind("+")] == conf.COM.Version:
            build = int(ver[(ver.rfind(".") + 1) :]) + 1  # noqa E203
            ver = ver[: ver.rfind(".") + 1] + str(build)  # noqa E203
            file = open(version_file, "w")
            file.write(ver)
            file.close


def check_integrity():
    connection = pymysql.connect(host=conf.DB.Host, user=conf.DB.User, passwd=conf.DB.Passwd, database=conf.DB.Name)

    with connection:
        cursor = connection.cursor()
        retrive = "SELECT * FROM `hashes`"

        cursor.execute(retrive)
        rows = cursor.fetchall()
        err_flag = False
    if len(rows) != 0:
        for row in rows:
            id = "{0}".format(row[0], row[1], row[2])  # noqa: F523
            module_name = "{1}".format(row[0], row[1], row[2])  # noqa: F523
            hash = "{2}".format(row[0], row[1], row[2])  # noqa: F523
            if hash != get_hash(module_name):
                if os.path.isfile(conf.DEV.DevFlagPath):
                    conn = pymysql.connect(
                        host=conf.DB.Host, user=conf.DB.User, passwd=conf.DB.Passwd, database=conf.DB.Name
                    )
                    with conn.cursor() as cur_upd:
                        sql = "UPDATE hashes SET hash=(%s) WHERE id=(%s)"
                        value = (get_hash(module_name), id)
                        cur_upd.execute(sql, value)
                        conn.commit()
                        conn.close()
                    print(module_name + " - " + hash + " - " + get_hash(module_name))
                else:
                    err_flag = True
                    # TODO: Переписать в отдельную функцию!
                    log = open("./log/error.log", "a")
                    error_msg = "***ERROR***: " + get_timestamp() + "Нарушена целостность модуля " + module_name
                    log.write(error_msg + "\n")
                    log.close()

        if err_flag:
            os._exit(os.EX_OK)

    else:
        conn = pymysql.connect(host=conf.DB.Host, user=conf.DB.User, passwd=conf.DB.Passwd, database=conf.DB.Name)
        with conn.cursor() as cur:
            sql = "INSERT INTO hashes (file, hash) VALUES (%s, %s)"
            value = ("main.py", get_hash("main.py"))
            cur.execute(sql, value)
            conn.commit()

            sql = "INSERT INTO hashes (file, hash) VALUES (%s, %s)"
            value = ("settings.py", get_hash("settings.py"))
            cur.execute(sql, value)
            conn.commit()

            sql = "INSERT INTO hashes (file, hash) VALUES (%s, %s)"
            value = ("functions.py", get_hash("functions.py"))
            cur.execute(sql, value)
            conn.commit()


def get_hash(file):
    md5_hash = hashlib.new("md5")
    if file == "main.py":
        file_path = "./" + file
    elif file == "settings.py" or file == "functions.py":
        file_path = "./modules/" + file

    with open(file_path, "rb") as read_file:
        data = read_file.read(65535)
        md5_hash.update(data)
        read_file.close()
        return md5_hash.hexdigest()
