# SherloCAN v0.2 Alpha — установка на Windows

## Назначение релиза
Это первый практический alpha-релиз для обкатки интерфейса, Evidence/SD workflow и подготовки к испытанию OpenPort 2.0. Физический J2534 RAW capture ещё не считается подтверждённым на реальном автомобиле.

## Поддерживаемая ОС
Первичная целевая система: Windows 10/11 x64. Windows 8.1 рассматривается как экспериментальная: Python 3.12 официально поддерживает Windows 8.1, но современный frontend toolchain не должен устанавливаться на тестовый ноутбук — frontend собирается заранее в CI. Windows 8.0 не заявляется как поддерживаемая.

## Вариант A — запуск из исходников (для первого теста)
1. Установите Python 3.12 x64.
2. Для J2534 установите официальный драйвер Tactrix OpenPort 2.0 подходящей разрядности.
3. Скачайте ZIP ветки/main релиза и распакуйте, например в C:\SherloCAN.
4. Откройте cmd в каталоге SherloCAN.
5. Выполните scripts\setup_windows.bat.
6. Запустите scripts\run_release.bat.
7. Откройте http://127.0.0.1:8000.

Node.js на тестовом ноутбуке не требуется: release workflow заранее собирает frontend и backend раздаёт статические файлы.

## Проверка перед автомобилем
- приложение открывается;
- /health отвечает;
- OpenPort Card обнаруживает J2534 provider/DLL;
- DEVICE OPEN/CAN CHANNEL остаются NOT TESTED, пока тест не выполнен;
- не вводите bitrate наугад;
- standalone OBD logging и passive RAW CAN — разные режимы.

## Ограничения alpha
Live J2534 reader пока mock-tested и требует проверки точного поведения j2534-api/OpenPort на реальном устройстве. Windows 8.0 не подтверждён. Первый автомобильный тест начинайте с device/open/channel gates, затем короткий capture.
