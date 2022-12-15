import socket

serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
serv_sock.bind(('127.0.0.4', 50330))  # Привязываем серверный сокет к localhost и 50330 порту.
serv_sock.listen(1)  # Начинаем прослушивать входящие соединения.
while True:
    conn, addr = serv_sock.accept()  # Метод который принимает входящее соединение.
    data = conn.recv(1024)  # Получаем данные из сокета.
    name_host = data.decode('utf-8')
    print(f'name of host: {name_host}')
    ip_host = socket.gethostbyname(name_host)
    print(f'ip: {ip_host}')
    conn.send(ip_host.encode('utf-8'))
    conn.close()