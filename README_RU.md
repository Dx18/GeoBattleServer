GeoBattle-Server program | 26.05.2019

Описание:
----------

    Это приложение-сервер для многопользовательской игры планетарного масштаба - GeoBattle. Игроки строят и развивают свои базы на реальной карте мира, используя возможности геолокации. Игра заставит не сидеть на месте, а сражаться за право быть самым успешным.
    Если вы это читаете - значит вы скачали необходимые файлы для запуска собственного сервера этой игры. Разработчики не против внесения изменений в код, но после этого не несут ответственность за нестабильную работу. Внимательно прочтите инструкцию. Удачи в захвате мира!

-----------------------------------------------------------------------------

Основные модули с описанием:
--------------------------------

    socket_server.py - главный модуль сервера. Слушает запросы игроков и вызывает их обработчики. Хранит данные о совершаемых атаках и об изменениях игрового состояния за последние 10 секунд. Начисляет ресурсы игрокам. Структура вызова: python3.6 socket_server.py -i <ip_addr> -p <port> -c <если нужно создать НОВУЮ базу данных> -s <использовать шифрование tls> . 
    SslServer.py - вспомогательный сервер для обновления сертификатов на устройствах игроков.
    startServer.py - запуск сервера и контроль его работы. Структура вызова: python3.6 startServer.py -i <ip_addr> -p <port> -c <если нужно создать НОВУЮ базу данных>
    stopServer.py - простая остановка сервера.
    newdb.py - создание базы данных. Таблицы: Players, Sectors, Buildings, Units, Attacks.
    registration.py - отвечает за регистрацию/авторизацию игроков. Осуществляет проверку почты.
    state.py - формирует ПОЛНОЕ игровое состояние, которое запрашивается при запуске игры.
    build.py - постройка/разрушение зданий.
    sectorBuild.py - строительство нового сектора.
    ResearchEvent.py - улучшение характеристик самолётов, турелей и генераторов.
    addUnits.py - добавление юнитов в ангар
    getRating.py - информация о капитале игроков в денежном эквиваленте для составления игрового рейтинга.
    Fighting.py - создание сценария битвы.
    attack.py - модуль для нападения на чужие сектора.
    functions.py - вспомогательные функции для сервера.
    param_parser.py - модуль для учёта параметров командной строки
    serverFunctions.py - фунции запуска и отключение отдельных частей сервера. 
    cert.pem и key.pem - сертификат и ключ для шифрования.

------------------------------------------------------------------------------------------------------------

Системные требования:
----------------------

    Операционная система linux с 512mb RAM. Пакетно уставленный Python версии не ниже Python3.6.7 . Дополнительно установленные модули: ssl, psutil. Стабильное подключение к интернету. Выделенный ip адрес. 

------------------------------------------------------------------------------------------------------------

Описание запуска:
------------------

0) Проверьте соответствие системным требованиям
1) Скопируйте каталог со всеми файлами в пустую директорию на компьютере-сервере с выделенным ip адресом.
2) Установите инструмент screen.
3) Если у вас уже есть готовая база данных с прошлых запусков, то скопируйте её к остальным файлам под именем main.db
4) Откройте терминал и перейдите в каталог к файлам сервера.
5) Запустите screen
6) Введите: python3.6 startServer.py -i <ip_addr> -p <port>
7) Нажмите Ctrl+a и затем d
8) Сервер запущен! Вы можете закрыть ssh, если такое соединение имело место быть, сервер продолжит работу.

9) При запуске игры введите во вкладке Settings данные вашего сервера.

-----------------------------------------------------------------------------------------------------------------------

Об авторах:
    Проект создан в рамках программы It School Samsung выпускниками: Подковыровым Демьяном, Карандашовым Владиславом и Темненковым Максимом. Вы можете отправить свои отчёты об ошибках и предложения на geobattleit@gmail.com . Новейшая версия сервера по ссылке https://github.com/Dx18/ServerGeobattle . Новейшая версия клиента по ссылке https://github.com/Dx18/GeoBattle .



