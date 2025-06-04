import socket

def send_key(key):
    """Отправляет команду на сервер."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    socket_path = "/tmp/keypress_socket.sock"

    try:
        sock.connect(socket_path)
        sock.sendall(key.encode())
    except Exception as e:
        print(f"Ошибка отправки: {e}")
    finally:
        sock.close()

# Пример использования
if __name__ == "__main__":
    send_key("press XF86AudioPlay")
    send_key("release XF86AudioPlay")  # Отправляем нажатие Tab
