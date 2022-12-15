import dearpygui.dearpygui as dpg
import re
from socket import *
from ssl import *
from http_parser.http import HttpStream
from http_parser.reader import SocketReader
from html.parser import HTMLParser

hostname = "docs.readthedocs.io"
path = "/en/"
DEFAULT_PORT = 443
TIMEOUT = 0.0

dpg.create_context()
sslcontext = create_default_context()


class tHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            dpg.add_text(f"{tag}: ", parent='content')
            for attr in attrs:
                dpg.add_text(f"     attr: {attr}", parent='content')
        for attr in attrs:
            if attr[0] == 'href':
                dpg.add_button(label=attr[1], parent='content', callback=follow_link, user_data=attr[1])


def follow_link(sender, app_data, user_data):
    parse_path(user_data)
    dpg.set_value('path', user_data)
    open_link(None, None, user_data)


def parse_path(full_path: str):
    print("PARSE_PATH: ", full_path)
    global hostname, path
    if full_path[0] != '/':
        if re.search(r'(//[\w.]*)', full_path):
            hostname = re.search(r'(//[\w.]*)', full_path)[0][2:]
        print("parsed hostname: ", hostname)
        if re.search(r'(\w/.*)', full_path) or re.search(r'(\w/.*\.html)', full_path):
            path = re.search(r'(\w/.*)', full_path)[0][1:]
        else:
            path = '/'
    else:
        path = full_path
    dpg.set_value('correct_host', f"{hostname}{path}")


def open_link(sender, app_data, full_path):
    dpg.delete_item('content', children_only=True)
    if full_path == 'init':
        full_path = dpg.get_value('path')
        parse_path(full_path)
    if not re.search(r'(http)', full_path):
        full_path = 'https://' + hostname + path
    print("open_link: ", full_path)
    with create_connection((hostname, DEFAULT_PORT)) as sock:
        with sslcontext.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(ssock.version())
            receive_page = f"GET {path} HTTP/1.1\r\n" \
                           f"Host:{hostname}\r\n" \
                           f"User-Agent: Linux\r\n" \
                           "\r\n"
            ssock.send(receive_page.encode())
            r = SocketReader(ssock)
            p = HttpStream(r)
            # print(p.headers())
            body = p.body_file().read()
            parser = tHTMLParser()
            parser.feed(body.decode('utf8'))
            if re.search(r'([^/]/.*\.html)', full_path):
                filename = re.search(r'([^/]*\.html)', full_path)[0]
                with open(filename, 'wb') as source:
                    source.write(body)


with dpg.window(label="BROWSER", tag="main", autosize=True):
    with dpg.menu_bar():
        dpg.add_button(label=':SEARCH', tag='search', callback=open_link, user_data='init')
        dpg.add_input_text(label=":PATH", tag='path', default_value='https://docs.readthedocs.io/en/')
        dpg.add_input_text(label="Host", tag='correct_host', default_value='docs.readthedocs.io/en/', readonly=True)
    dpg.add_child_window(tag='content')

# region other
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
dpg.create_viewport(title='BROWSER', width=960, height=750)
dpg.set_global_font_scale(1.25)
# dpg.set_exit_callback(on_exit)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main", True)
dpg.start_dearpygui()
dpg.destroy_context()

# endregion
