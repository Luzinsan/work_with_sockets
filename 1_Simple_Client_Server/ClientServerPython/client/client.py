import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.4', 50330))  # Подключаемся к нашему серверу.
name_host = 'vk.ru'
print(f'name of host: {name_host}')
s.send(name_host.encode('utf-8'))  # Отправляем имя хоста.
data = s.recv(16)  # Получаем данные из сокета.
print(f'ip: {data.decode("utf-8")}')
s.close()
