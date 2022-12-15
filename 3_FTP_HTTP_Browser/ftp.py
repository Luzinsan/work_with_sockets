import dearpygui.dearpygui as dpg
from socket import *
import re
import time

DEFAULT_SERVER = "ftp.slackware.com"
DEFAULT_LOGIN = "anonymous"
DEFAULT_PASS = "anonymous"
DEFAULT_PORT = 21  # сетевой порт для управляющего соединения
TIMEOUT = 0.0

dpg.create_context()


# region ####################################### Stage #1: INITIALIZATION SERVER  ######################################
def recv_all(socket_manager):
    while True:
        answer = socket_manager.recv(1024).decode('utf-8')
        match = re.search(r'\d{3}\s.*', answer)
        if match:
            print(match[0])
            break
    return match[0]


def init_server(sender, app_data, user_data):
    socket_manager = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)  # управляющее соединение
    try:
        # соединяемся с сервером для передачи управляющих команд
        socket_manager.connect((dpg.get_value('host'), dpg.get_value('port')))
        recv_all(socket_manager)
        dpg.add_text("1: Connected to host successful", tag='connect', before='sep')
        time.sleep(TIMEOUT)
        dpg.delete_item("connect")
        dpg.set_item_user_data("auth", socket_manager)
    except:
        dpg.add_text("Incorrect HOST or PORT", tag='err', before='sep')
        time.sleep(TIMEOUT)
        dpg.delete_item("err")
        socket_manager.close()
        return
    etc_server_data(socket_manager)
    update_dir(socket_manager)


def etc_server_data(socket_manager):
    # аутентификация пользователя
    init_user(socket_manager)
    # текущая кодировка
    update_text(socket_manager, b"TYPE I\r\n", 'type')
    # определяем систему хоста
    update_text(socket_manager, b"SYST\r\n", 'system')


def update_dir(socket_manager):
    # определяем текущую директорию
    update_text(socket_manager, b"PWD\r\n", 'path')
    socket_data = init_pasv(socket_manager)
    output_list(socket_manager, socket_data)
    socket_data.close()


def update_text(socket_manager, cmd: bytes, tag: str):
    socket_manager.send(cmd)
    response = recv_all(socket_manager)
    dpg.set_value(tag, response[3:])
    return response[:3]


def output_list(socket_manager, socket_data):
    print('\n\t\tOUTPUT_LIST')
    socket_manager.send(b"LIST\r\n")
    recv_all(socket_manager)  # Подтверждаем соединение с сервером для передачи списка
    recv_all(socket_manager)  # Подтверждение о выводе списка директорий/файлов
    count = 0
    ftp_list = []
    print("READING...")
    while True:
        curr_list = socket_data.recv(1024).decode('utf-8').splitlines()
        count = count + len(curr_list)
        ftp_list += curr_list
        if len(curr_list) == 0:
            break
    dpg.set_value('numdir', count)
    dpg.configure_item('list', items=ftp_list)
    print("\t\tOutputting list DONE\n")


########################################## Stage #2: AUTHENTICATION USER #############################################
def send_recv_cmd(socket_manager: socket, cmd: bytes, tag: str = 'response', before: str = '') -> str:
    """ Посылает команду на подключенных хост, выводит в GUI ответ (tag='response') и возвращает код ответа

    :param socket_manager: сокет управляющего соединения
    :param cmd: отправляемая команда на подключенный сервер
    :param tag: tag добавляемого в GUI ответа
    :param before: tag элемента, перед которым выводится ответ (если '', то вывод в консоль)
    :return: код ответа
    """
    socket_manager.send(cmd)
    res = recv_all(socket_manager)
    if before != '':
        dpg.add_text(res[3:], tag=tag, before=before)
    return res[:3]


def init_user(socket_manager):
    CMD_USER = f"USER {dpg.get_value('user')}\r\n".encode("utf-8")
    CMD_PASS = f"PASS {dpg.get_value('pass')}\r\n".encode("utf-8")
    # Имя пользователя для входа на сервер.
    send_recv_cmd(socket_manager, CMD_USER, 'user_auth', 'pass')
    # Пароль пользователя для входа на сервер.
    res = send_recv_cmd(socket_manager, CMD_PASS, 'pass_user', 'answers')
    if res == '230':  # если аутентификация прошла успешно, закрываем окно
        dpg.add_text("Authorization successful", tag='success', before="answers")
        time.sleep(TIMEOUT)
        dpg.configure_item('auth', show=False)
        dpg.delete_item('success')
    time.sleep(TIMEOUT)
    dpg.delete_item('pass_user')
    dpg.delete_item('user_auth')


def init_pasv(socket_manager):
    #  Войти в пассивный режим. Сервер вернёт адрес и порт, к которому нужно подключиться, чтобы забрать данные
    socket_manager.send(b"PASV\r\n")
    pasv = recv_all(socket_manager)
    # ищем подстроку соответствующую регулярному выражению
    match = re.search(r'(\d+,\d+,\d+,\d+,\d+,\d+)', pasv)
    # разбиваем через запятую получая список чисел соответствующих ip port
    match = re.split(r",", match[0])
    ip = ".".join(match[:4])
    port = int(match[4]) * 256 + int(match[5])
    dpg.set_value('ip_port', f"ip: {ip}\tport: {port}")
    print(f"ip {ip} port {port}")

    socket_data = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
    try:
        socket_data.connect((ip, port))
        return socket_data
    except:
        dpg.add_text("Discard Connection", tag='discard_socket_data', before='path')
        time.sleep(TIMEOUT)
        dpg.delete_item("discard_socket_data")
        socket_data.close()


# endregion ################################################ END AUTHORIZATION #########################################


def move_to(sender, app_data, user_data):
    socket_manager, directory = dpg.get_item_user_data('auth'),  dpg.get_value('move_to_path')
    # переходим в указанную директорию
    if send_recv_cmd(socket_manager, f"CWD {directory}\r\n".encode('utf-8')) == '250':
        update_dir(socket_manager)
        dpg.set_value('move_to_path', '')
        print(f"Moving to {directory} done")
    else:
        dpg.set_value('move_to_path', 'Invalid directory')


def download(sender, app_data, user_data):
    socket_manager, file_name = dpg.get_item_user_data('auth'),  dpg.get_value('download_file')
    socket_data = init_pasv(socket_manager)
    socket_manager.send(f"RETR {file_name}\r\n".encode('utf-8'))
    response = recv_all(socket_manager)  # подтверждение соединения (и возвращение размера файла)
    if response[:3] != '150':
        dpg.set_value('download_file', "Invalid File")
        socket_data.close()
        return
    match = re.search(r'\d+.\d+', response[4:])
    if match:
        size_file = round(float(match[0])*1024)  # Получаем размер файла в байтах
    else:
        size_file = 1024
    file = open(f"{file_name}", 'w')
    while size_file > 0:
        try:
            file_data = socket_data.recv(1024).decode('utf-8')
            file.write(file_data)
            size_file -= 1024
        except Exception as err:
            dpg.set_value('download_file', "Disable to download")
            print(err)
            file.close()
            recv_all(socket_manager)  # узнаём состояние загрузки
            socket_data.close()
            return
    file.close()
    recv_all(socket_manager)  # узнаём успешность загрузки
    downloaded_files.append(file_name)
    dpg.configure_item('downloaded', items=downloaded_files)
    dpg.set_value('download_file', '')
    socket_data.close()


def on_exit(sender, app_data, user_data):
    socket_manager = dpg.get_item_user_data('auth')
    send_recv_cmd(socket_manager, b"QUIT\r\n")
    socket_manager.close()
    print("socket_manager closed successfully")


############################################# AUTHORIZATION ############################################################
with dpg.window(label="AUTHORIZATION", modal=True, show=False, tag="auth", no_title_bar=True, autosize=True):
    dpg.add_input_text(label=":HOST", tag='host', default_value=DEFAULT_SERVER)
    dpg.add_input_int(label=":PORT", tag='port', default_value=DEFAULT_PORT)
    dpg.add_separator(tag='sep')
    dpg.add_input_text(label=":user", tag='user', default_value=DEFAULT_LOGIN)
    dpg.add_input_text(label=":password", tag='pass', default_value=DEFAULT_PASS, password=True)
    with dpg.group(horizontal=True, tag="answers"):
        dpg.add_button(label="Connect", width=75, callback=init_server)
        dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("auth", show=False))
########################################################################################################################


################################################# MAIN ################################################################
with dpg.window(label="Main", tag="Main", autosize=True):
    with dpg.menu_bar():
        with dpg.menu(label="Connection"):
            dpg.add_menu_item(label="Log in", callback=lambda: dpg.configure_item("auth", show=True))
    dpg.add_input_text(label=":System of Host", tag='system', readonly=True)  # система хоста
    dpg.add_input_text(label=":IP/PORT of Host", tag='ip_port', readonly=True)  # после перехода в пассивный режим определяем IP и PORT хоста
    dpg.add_input_text(label=":TYPE data", tag='type', readonly=True)  # переключаемся в бинарный режим
    dpg.add_input_text(label=":PATH", tag='path', readonly=True)  # текущая директория хоста
    dpg.add_input_text(label=":Number of Lines", tag='numdir', readonly=True)  # количество директорий/файлов в текущем каталоге

    dpg.add_listbox(tag='list', width=1820, num_items=20, tracked=True)  # список файлов текущей директории

    with dpg.group(horizontal=True, tag="move_to", indent=155):
        dpg.add_button(label="MOVE", callback=move_to, width=75)
        dpg.add_input_text(label=":PATH", tag='move_to_path', width=340)

    with dpg.group(horizontal=True, tag="download", indent=155):
        dpg.add_button(label="DOWNLOAD", callback=download, width=75)
        dpg.add_input_text(label=":FILE", tag='download_file', width=340)
    downloaded_files = []
    dpg.add_listbox(tag='downloaded', width=1820, items=downloaded_files)
########################################################################################################################
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (77, 7, 143), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvInputInt):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 77, 70), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvText):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (15, 61, 131), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)
########################################################################################################################
dpg.create_viewport(title='FTP CLIENT', width=960, height=750)
dpg.set_global_font_scale(1.25)
dpg.set_exit_callback(on_exit)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Main", True)
dpg.start_dearpygui()
dpg.destroy_context()

