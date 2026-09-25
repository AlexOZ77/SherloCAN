# SherloCAN v0.2.1 Alpha — первый тест на автомобиле

## Статус этой сборки

Эта сборка предназначена для **контролируемого первого аппаратного теста** SherloCAN с J2534/OpenPort на Windows 10/11 x64.

Что уже проверяется CI:
- frontend typecheck и production build;
- backend compile и полный pytest;
- установка `requirements-hardware.txt`;
- импорт `J2534`, `python-can` и `cantools`;
- сборка готового Windows ZIP.

Что **ещё не подтверждено до вашего теста**:
- фактическое поведение конкретного OpenPort 2.0 и установленного драйвера;
- точная интерпретация J2534 RxStatus/TxFlags/timestamp конкретной библиотеки;
- реальный RAW CAN capture на автомобиле;
- x86 bridge для 32-битного J2534 DLL;
- Windows 8.0.

Поэтому первый выезд — это **hardware acceptance**, а не уже подтверждённая диагностическая эксплуатация.

## 1. До автомобиля

1. Используйте Windows 10/11 x64.
2. Установите Python 3.12 x64.
3. Установите официальный драйвер Tactrix OpenPort 2.0.
4. Распакуйте ZIP полностью, например в `C:\SherloCAN`.
5. Выполните:
   `scripts\setup_windows.bat`
6. Затем:
   `scripts\run_release.bat`
7. Откройте `http://127.0.0.1:8000`.
8. Убедитесь, что интерфейс загружен и synthetic demo отделён от hardware.

## 2. Аппаратные ворота

Идти строго по порядку:

1. J2534 Provider / DLL.
2. Device Open.
3. CAN Channel с **подтверждённым** bitrate.
4. Короткий bounded capture.
5. Проверка Acceptance Gate.

Не переходить к следующему этапу после FAIL.

## 3. Experiment Protocol

Перед START CAPTURE заполнить:
- SCENARIO;
- TRIAL;
- IGNITION STATE;
- ENGINE STATE;
- измеренное напряжение АКБ, если есть;
- J2534 PROVIDER INDEX;
- CONFIRMED BITRATE;
- BITRATE SOURCE;
- MAX FRAMES;
- TIMEOUT;
- примечание оператора.

SherloCAN не угадывает bitrate.

## 4. Успешный первый capture

Capture технически пригоден только если Acceptance Gate показывает PASS:
- Device Open = OK;
- CAN Channel = OK;
- frames_observed > 0;
- frames_dropped = 0;
- RAW path создан;
- SHA-256 создан;
- Disconnect = clean;
- Device Close = clean;
- transmit_performed = false.

PASS означает только пригодность capture как evidence. Это не подтверждение исправности автомобиля и не root cause.

## 5. P0603 A/B

Сначала сохранить полный Quick Test внешним сканером.

NORMAL A:
- P0603 очищен;
- зажигание после очистки не выключать;
- START;
- capture;
- сохранить NORMAL_A trial 1;
- зарегистрировать START marker.

FAULT B:
- OFF;
- затем ON → START;
- зафиксировать возвращение P0603/предупреждений;
- capture с теми же параметрами;
- сохранить FAULT_B trial 1;
- зарегистрировать START marker.

Для repeatability выполнить A1/A2/A3 и B1/B2/B3.

## 6. Если что-то не работает

Сохранить:
- скриншот;
- точный текст ошибки;
- версию Windows;
- версию драйвера OpenPort;
- provider index;
- session ID;
- RAW/manifest, если созданы.

Не менять одновременно несколько условий.

## 7. После теста

Передать разработчику:
- `*.session.json`;
- `*.manifest.json`;
- RAW CSV;
- SHA-256;
- DTC Quick Test;
- скриншоты UI;
- заполненные условия теста.

Подробная процедура: `docs\DIAGNOSTIC_EXPERIMENT_PROCEDURE.md`.
Установка: `docs\INSTALL_WINDOWS_RU.md`.
