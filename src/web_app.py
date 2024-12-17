"""
ЗАДАЧА:
1) Написать простое веб-приложение, которое можно написать на Python без установки каких-либо дополнительных
библиотек или фреймворков.
2) Приложение представляет собой один адрес для проверки работоспособности сервиса, который отдает на GET-запрос
ответ с HTML-шаблоном страницы <Контакты>.
3) Работоспособность веб-приложения можно проверить через браузер или через Postman. Для работы через Postman
необходимо отправить GET-запрос на адрес http://localhost:8080.
"""


# Импорт библиотеки для работы с SSL-сертификатов
import ssl
# Импорт библиотеки для скачивания файла с удаленного репозитория
import urllib.request
# Импорт встроенной библиотеки для работы веб-сервера и обработки HTTP-запросов
from http.server import BaseHTTPRequestHandler, HTTPServer
# Чтобы распарсить данные в словарь на сервере, используется модуль urllib.parse
from urllib.parse import parse_qs

from config import HTML_URL

# Создаю SSL-контекст, который отключает проверку сертификатов при загрузке файла.
# При работе с SSL на MacOS часто бывает так, что Python не может проверить SSL-сертификат для
# указанного ресурса (в данном случае, для моего GitHub URL), что вызывает ошибку CERTIFICATE_VERIFY_FAILED.
# Для этого, чтоб протестировать работу кода локально, можно отключить проверку SSL-сертификатов при загрузке файла.
ssl._create_default_https_context = ssl._create_unverified_context

# Для начала определяю настройки запуска:
# 1) адрес, где сервер будет доступен (локальный компьютер)
# 2) порт, где сервер будет слушать входящие запросы
hostName = "localhost"
serverPort = 8080


# Класс MyServer наследует BaseHTTPRequestHandler и предназначен для обработки входящих HTTP-запросов
class MyServer(BaseHTTPRequestHandler):
    """Специальный класс, который отвечает за обработку входящих запросов от клиентов"""

    def do_GET(self) -> None:
        """Метод для обработки входящих GET-запросов"""
        # Отправка клиенту кода ответа 200 (OK)
        self.send_response(200)
        # Указываем тип данных, который будет передавать сервер (тело ответа будет в формате HTML-шаблона)
        self.send_header("Content-type", "text/html; charset=utf-8")
        # Завершение формирования заголовков ответа
        self.end_headers()
        # Отключаю проверку сертификата SSL, чтоб при тесте работы избежать ошибку CERTIFICATE_VERIFY_FAILED на MacOS
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(HTML_URL) as response:
            # Читаю и декодирую HTML
            html_content = response.read().decode("utf-8")
            # Кодирую в байты и отправляю клиенту
            self.wfile.write(bytes(html_content, "utf-8"))

    def do_POST(self) -> None:
        """Метод для обработки POST-запроса и печати в консоль данных, которые были введены пользователем"""
        # Получаю длину содержимого контента
        content_length = int(self.headers['Content-Length'])
        # Читаю и декодирую данные
        post_data = self.rfile.read(content_length).decode('utf-8')
        # Преобразовываю в словарь для удобного использования полученных данных в будущем
        post_params = parse_qs(post_data)
        # Печатаю данные в консоль
        print("Параметры POST-запроса:", post_params)
        # Отправляю ответ клиенту
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("POST-запрос успешно обработан!".encode("utf-8"))


if __name__ == "__main__":
    """Инициализация веб-сервера, который будет по заданным параметрам в сети принимать запросы и отправлять
    их на обработку специальному классу, который был описан выше"""

    # Создаю экземпляр сервера с указанными адресом и портом и назначения класса для обработки запросов
    webServer = HTTPServer((hostName, serverPort), MyServer)
    # Вывожу сообщение о старте сервера с указанием адреса и порта
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        # Запуск веб-сервера в бесконечном цикле прослушивания входящих запросов
        webServer.serve_forever()
    except KeyboardInterrupt:
        # Корректный способ остановить сервер в консоли через сочетание клавиш Ctrl + C
        pass

    # Корректная остановка веб-сервера, чтобы он освободил адрес и порт в сети, которые занимал
    webServer.server_close()
    print("Server stopped.")
