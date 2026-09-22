# SherloCAN — руководство по функционалу

> Живой документ. Обновлять вместе с функциональными изменениями. Версия документа: 0.2-alpha / 2026-09-22.

## 1. Назначение
SherloCAN — evidence-first инструмент исследования автомобильных CAN-сетей. Текущая версия ориентирована на пассивный сбор и сравнение данных. Программа не должна приписывать CAN ID конкретному ECU, угадывать bitrate или объявлять причину неисправности без подтверждающих данных.

## 2. Текущий функционал

### Capture & Investigate
- File Replay для воспроизводимых тестовых CAN-данных.
- NORMAL baseline и детерминированный поиск LONG GAP.
- Flight Recorder с маркерами событий.
- Ограниченная FrameQueue с явным учётом dropped frames.
- RAW CSV writer с SHA-256 контрольной суммой.
- CAPTURE DATA LOSS при потере кадров.

### OpenPort / J2534
Аппаратный путь разбит на независимые ворота:
1. **J2534 Provider** — поиск зарегистрированного PassThru-провайдера.
2. **Driver / DLL** — проверка существования DLL и архитектуры.
3. **Device Open** — явный PassThruOpen с последующим PassThruClose.
4. **CAN Channel** — явный raw CAN PassThruConnect/Disconnect. Bitrate обязателен и не угадывается.
5. **CAN Traffic** — bounded reader и normalizer подготовлены; физический OpenPort-захват должен быть подтверждён на реальном компьютере.

### Evidence pipeline
Текущий тракт:
`J2534 reader → CANFrame → CaptureSession → FrameQueue → RAW CSV → SHA-256`.

Возвращаемые измерения: observed frames, accepted frames, dropped frames, unique IDs, CAPTURE DATA LOSS, RAW path и SHA-256.

## 3. Безопасность
Режим v0.2 является application-read-only: SherloCAN не добавляет произвольную передачу CAN сообщений. В capture reader не используется write-message API. Это не следует трактовать как обещание электрической пассивности самого J2534-адаптера.

## 4. Интерфейс
### OpenPort Card
**DEVICE TEST** выполняет неинвазивный preflight. **VERIFY DEVICE OPEN** отдельно проверяет открытие J2534-устройства. CAN Channel и CAN Traffic не становятся зелёными только потому, что найден драйвер.

### UNKNOWN
Напряжение, CAN latency, bitrate, fps, ECU ownership и другие параметры отображаются как UNKNOWN, пока реально не измерены или явно не заданы.

## 5. Первый запуск на автомобиле
1. Установить официальный драйвер OpenPort/J2534.
2. Подключить OpenPort 2.0 к Windows-ноутбуку.
3. Запустить SherloCAN.
4. Выполнить DEVICE TEST.
5. Выполнить VERIFY DEVICE OPEN.
6. Указать подтверждённый bitrate вручную.
7. Проверить открытие raw CAN channel.
8. Только после успешных предыдущих ворот запускать bounded capture.
9. После захвата проверить Frames Dropped и CAPTURE DATA LOSS.
10. Сохранить RAW-файл и SHA-256 вместе с описанием условий эксперимента.

## 6. Эксперимент J11 P0603
Для первого сравнительного исследования предусмотрены две сессии:
- **NORMAL/A:** P0603 очищен, зажигание остаётся ON, затем START без OFF.
- **FAULT/B:** двигатель/зажигание OFF → затем ON → START, после чего фиксируется появление P0603/предупреждений.

SherloCAN должен сравнивать наблюдаемые изменения между сессиями, но не назначать root cause автоматически.

## 7. Что ещё не считается готовым
- физически подтверждённый live capture с конкретным OpenPort 2.0;
- автоматическое определение bitrate;
- подтверждённая ECU↔CAN-ID карта J11;
- активный DTC polling;
- UDS/ISO-TP диагностика;
- автоматический вывод о первопричине;
- завершённый x86 bridge для несовместимой архитектуры DLL;
- подтверждённая сборка для Windows 8.

## 8. Правило актуализации
При каждом функциональном цикле обновлять этот файл: **что добавлено → как пользоваться → какие данные являются измеренными → ограничения → новые тесты**. Не превращать будущий roadmap в описание уже работающих функций.

## 9. Capture Evidence Card
В основном экране добавлена карточка **Capture Evidence**. До реального захвата она прямо сообщает, что измерения отсутствуют, и не подставляет демонстрационные числа.

После подключения результата capture pipeline карточка предназначена для отображения только данных backend: **Observed**, **Accepted**, **Dropped**, **Unique IDs**, состояние **CAPTURE DATA LOSS**, путь RAW-файла и его **SHA-256**.

Если `Dropped > 0`, результат должен маркироваться как **CAPTURE DATA LOSS**. Это означает, что сохранённый набор неполон относительно кадров, наблюдавшихся входным трактом, и такой сеанс нельзя представлять как захват без потерь.

### Изменения цикла 009
- добавлен UI-компонент Capture Evidence;
- добавлены состояния «измерений ещё нет», «без зарегистрированных потерь» и «CAPTURE DATA LOSS»;
- карточка пока подключена в безопасном состоянии `result=null`: реальные числа появятся только после session API, а не из mock/demo данных.

## 10. Bounded Capture Session API
Добавлен контроллер одного ограниченного сеанса захвата и endpoint **POST /api/capture/j2534/capture**. Он принимает только явные параметры: provider index, уже открытый channel ID, bitrate, timeout и максимальное число кадров.

Каждый запуск получает уникальный **session_id**, UTC-время начала/окончания и отдельный RAW CSV в `data/captures`. Ответ содержит блок `evidence`, предназначенный для прямой передачи в Capture Evidence Card.

Важно: endpoint не выбирает bitrate автоматически и не открывает канал скрытно. На текущем этапе он рассчитан на уже открытый raw CAN channel; жизненный цикл Open→Connect→Capture→Disconnect будет объединён следующим контроллером, чтобы исключить ручную передачу устаревшего channel ID.

### Изменения цикла 010
- создан CaptureRequest и bounded session controller;
- добавлен API одного ограниченного capture-сеанса;
- добавлены session_id и UTC timestamps;
- добавлен тест метаданных с mock hardware boundary;
- UI-карточка уже совместима с возвращаемым блоком evidence.

## 11. Атомарный аппаратный захват
После командного design review добавлен endpoint **POST /api/capture/j2534/atomic-capture**. Это предпочтительный аппаратный путь: оператор больше не должен передавать или повторно использовать `channel_id`.

Один запрос владеет полным жизненным циклом:
`Provider select → PassThruOpen → raw CAN PassThruConnect → bounded Capture → PassThruDisconnect → PassThruClose → Evidence`.

Очистка выполняется в `finally`: даже при ошибке чтения SherloCAN отдельно пытается закрыть CAN channel и J2534 device. Ответ содержит `disconnected_cleanly`, `device_closed_cleanly`, `error` и `transmit_performed=false`.

### Как использовать
Перед START CAPTURE оператор обязан выбрать зарегистрированный provider и явно указать подтверждённый bitrate. `max_frames` и `timeout_ms` ограничивают сеанс. Успешный Connect сам по себе не означает наличие трафика: это подтверждается только `frames_observed > 0`.

### Изменения цикла 011
- проведён design review до реализации;
- создан атомарный hardware lifecycle;
- channel_id исключается из пользовательского сценария;
- cleanup-состояния стали частью evidence metadata;
- добавлен mock-тест, подтверждающий Disconnect и Close;
- активная передача сообщений не добавлялась.
