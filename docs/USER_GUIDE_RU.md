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

## 12. START CAPTURE в интерфейсе
Добавлена операторская панель **Live Capture**. Она вызывает атомарный hardware endpoint и после завершения передаёт только фактически возвращённый backend блок `evidence` в Capture Evidence Card.

### Порядок работы
1. Выполнить OpenPort **DEVICE TEST** и при необходимости **VERIFY DEVICE OPEN**.
2. В **J2534 PROVIDER INDEX** оставить/указать индекс реально обнаруженного провайдера.
3. В **CONFIRMED BITRATE** вручную ввести только заранее подтверждённую скорость CAN. Пустое значение означает UNKNOWN; SherloCAN не подставляет значение автоматически.
4. В **MAX FRAMES** задать верхнюю границу кадров сеанса.
5. Нажать **START CAPTURE**. На время запроса кнопка блокируется, статус меняется на RUNNING/CAPTURING.
6. После завершения проверить Capture Evidence: Observed, Accepted, Dropped, Unique IDs, DATA LOSS, RAW и SHA-256.
7. Проверить нижнюю полосу жизненного цикла: **DEVICE OPEN**, **CAN CHANNEL**, **DISCONNECT**, **DEVICE CLOSE**. Значения REVIEW требуют разбирательства и не должны трактоваться как полностью успешный сеанс.

### Что важно
Успешный DEVICE OPEN или CAN CHANNEL не доказывает наличие CAN-трафика. Наличие трафика подтверждается только фактически наблюдёнными кадрами. UI не использует synthetic replay как аппаратное измерение.

### Изменения цикла 012
- реализована кнопка START CAPTURE;
- bitrate стал обязательным явным операторским вводом;
- добавлено состояние RUNNING;
- atomic API связан с Capture Evidence Card;
- добавлено отображение cleanup gate status;
- mock/placeholder значения аппаратных измерений не добавлялись.

## 13. Command Center — экран первого аппаратного теста
Интерфейс Capture переразложен по схеме **Устройство и параметры → Состояние захвата → Evidence**. Это не отдельный демонстрационный макет: компоненты связаны с фактическим состоянием atomic capture API.

### Состояние захвата
Панель показывает пять этапов: **Открытие устройства → Подключение к CAN → Чтение данных → Отключение от CAN → Закрытие устройства**. Во время запроса отображается RUNNING. После завершения Open/Connect/Disconnect/Close берутся из backend-результата.

Этап **Чтение данных** считается подтверждённым только при `frames_observed > 0`. Сам факт успешного PassThruConnect не окрашивает трафик как подтверждённый.

### Перед первым тестом
Не ориентироваться на ранее созданный концепт UI как на измерение: показанные там bitrate, fps, версия драйвера, CAN IDs и другие числа были иллюстративными. Реальный экран SherloCAN должен заполнять аппаратные поля только backend-данными.

### Изменения цикла 013
- добавлен CaptureRunStatus;
- LiveCaptureControl публикует состояние RUNNING;
- основной экран перестроен в двухколоночный command-center;
- аппаратный lifecycle отображается отдельно от Evidence;
- подтверждение CAN Traffic привязано к фактически наблюдаемым кадрам;
- адаптивная раскладка возвращается к одной колонке на узком экране.

## 14. Сохранённые сессии NORMAL A / FAULT B
Добавлен рабочий контур сравнительного эксперимента P0603. После завершения atomic capture его metadata сохраняется рядом с RAW как `<session_id>.session.json`. Оператор может зарегистрировать завершённый захват как **NORMAL A** или **FAULT B**.

### Проведение эксперимента
1. Выполнить сценарий **NORMAL A**: P0603 очищен, зажигание не выключать, затем START. Выполнить capture и нажать **Текущий → NORMAL A**.
2. Выполнить сценарий **FAULT B**: OFF → ON → START до появления P0603/предупреждений. Выполнить новый capture и нажать **Текущий → FAULT B**.
3. Когда обе сессии зарегистрированы, нажать **СРАВНИТЬ A/B**.
4. Таблица показывает только описательные различия RAW: CAN ID, количество кадров в A и B, разницу количества и присутствие `BOTH / NORMAL_ONLY / FAULT_ONLY`.
5. Если любая сессия имеет `CAPTURE DATA LOSS`, сравнение сохраняет этот флаг и должно трактоваться с ограничением.

### Ограничения сравнения
Текущая версия **не** присваивает CAN ID блокам ECM/ABS/4WD, не декодирует payload и не объявляет root cause. Разница количества кадров — наблюдение, а не доказательство причинной связи. Следующая версия сравнения должна добавить временные характеристики и детерминированные LONG_GAP/NEW_ID/LOST_ID без изменения этого принципа.

### Изменения цикла 014
- добавлено сохранение session metadata;
- создан persistent experiment registry;
- добавлены роли NORMAL_A и FAULT_B;
- реализовано RAW A/B сравнение по CAN ID/count/presence;
- добавлен backend test сравнения;
- создан UI Experiment P0603 A/B;
- DATA LOSS переносится в результат сравнения.

## 15. First Divergence Engine v1
A/B-анализ расширен от простого count-сравнения к поиску **первого наблюдаемого изменения**. Для каждого CAN ID из RAW рассчитываются count, first/last timestamp, median period, оценочная частота и typical DLC.

Детерминированные события v1: **NEW_ID**, **LOST_ID**, **PERIOD_SHIFT**, **FREQUENCY_SHIFT**, **DLC_CHANGE**. События, попавшие в окно 50 ms, группируются как **MULTI_ID_EVENT**. Пороговые отношения period/frequency в текущей реализации равны 1.5 и должны в дальнейшем стать параметрами профиля анализа.

UI выводит **FIRST OBSERVED CHANGE**, но одновременно фиксирует **ECU UNKNOWN** и **CAUSALITY NOT_ESTABLISHED**. Цвет/оформление события не означает неисправность блока или доказанную причинность.

### Важное ограничение v1
Сессии пока сравниваются по их собственным RAW timestamps без привязки к общему операторскому маркеру START/IGN ON. Поэтому First Divergence v1 является первым детерминированным сравнением, но **ещё не полноценной фазово-синхронизированной причинно-временной реконструкцией**. Следующий шаг — маркеры событий и выравнивание A/B относительно START.

### Изменения цикла 015
- создан First Divergence Engine v1;
- добавлены timing/frequency/DLC признаки;
- добавлены NEW_ID/LOST_ID/PERIOD_SHIFT/FREQUENCY_SHIFT/DLC_CHANGE;
- добавлена 50 ms MULTI_ID группировка;
- создан API divergence для зарегистрированных A/B;
- UI показывает первое наблюдаемое изменение отдельно от причинности;
- добавлен backend test NEW_ID + MULTI_ID_EVENT.

## 16. Маркеры событий и фазовое выравнивание по START
Добавлено persistent-хранилище операторских маркеров. Поддерживаемые типы: **IGN_ON, START, ENGINE_RUNNING, FAULT, DTC, WIGGLE, ROAD_BUMP, CONNECTOR, OTHER**. В UI цикла 016 первым рабочим anchor является **START**.

### Как выполнить синхронизированный тест P0603
1. Записать и сохранить **NORMAL A**.
2. В поле **START timestamp** указать timestamp фактического события START внутри RAW A и нажать **START → A**.
3. Записать и сохранить **FAULT B**.
4. Аналогично зарегистрировать START для B кнопкой **START → B**.
5. Нажать **СРАВНИТЬ A/B**. SherloCAN требует START в обеих сессиях и выравнивает каждую шкалу так, что собственный START становится `t=0`.
6. Текущий рабочий интервал сравнения: **−5 s … +15 s относительно START**.
7. FIRST OBSERVED CHANGE теперь выводится в относительном времени, например `+420 ms`; это значение допустимо как измерение только для реально зарегистрированных RAW/marker данных.
8. Отсутствие START хотя бы в одной сессии должно блокировать START-aligned анализ, а не незаметно возвращать несинхронизированное сравнение.

### Что является evidence
Marker timestamp является **операторским наблюдением**. SherloCAN v0.2 не пытается угадывать START по неизвестному CAN ID. Результат divergence является детерминированным сравнением вокруг указанного anchor, но **FIRST OBSERVED CHANGE ≠ root cause**. ECU ownership остаётся UNKNOWN, пока не появится подтверждённое сопоставление.

### Командное моделирование тестов
Команда провела software simulation happy path и failure paths; протокол сохранён в `docs/TEAM_SIMULATION_016.md`. Автоматический тест моделирует разные абсолютные времена START (A=10 s, B=20 s), после выравнивания ожидает synthetic NEW_ID в `+420 ms` и MULTI_ID_EVENT из двух изменений. Эти ID/времена являются **только тестовыми фикстурами**, не данными Nissan.

Проверены сценарии: отсутствующий START, отрицательный timestamp, неподдерживаемый marker, разные абсолютные временные базы, окно анализа, MULTI_ID grouping, DATA LOSS как ограничение и запрет причинного вывода.

### Изменения цикла 016
- persistent event markers;
- START anchor в UI;
- фазовое выравнивание A/B;
- окно −5…+15 s;
- относительное время FIRST OBSERVED CHANGE;
- API блокирует aligned-анализ без обоих START;
- добавлен моделирующий backend test;
- оформлен командный test walkthrough.

## 17. Повторяемость A1/A2/A3 ↔ B1/B2/B3
Добавлен Repeatability Engine. При сохранении NORMAL_A/FAULT_B оператор задаёт **номер повтора**. Рекомендуемый первый набор: A1, A2, A3 и B1, B2, B3. Каждая сессия должна иметь собственный START marker.

### Порядок теста
1. Трижды выполнить NORMAL-сценарий и сохранить captures как A1, A2, A3.
2. Для каждой A-сессии зарегистрировать фактический START timestamp.
3. Трижды выполнить FAULT-сценарий OFF → ON → START и сохранить B1, B2, B3.
4. Для каждой B-сессии зарегистрировать START.
5. Нажать **АНАЛИЗ ПОВТОРЯЕМОСТИ**. Минимум для запуска движка — две нумерованные A и две B; для рабочего P0603-протокола рекомендуются 3+3.
6. SherloCAN выполняет попарные START-aligned сравнения и агрегирует наблюдения по CAN ID + event type.
7. В таблице выводятся NORMAL n/N, FAULT n/N, median relative time и статус **REPEATED IN ALL B / PARTIAL**.

**REPEATED IN ALL B** означает только то, что наблюдение воспроизвелось во всех зарегистрированных FAULT trials. Это не означает, что CAN ID принадлежит ECM/ABS, и не доказывает root cause.

### Командная симуляция
Протокол `docs/TEAM_SIMULATION_017.md` моделирует шесть файлов с разными абсолютными START. Synthetic 0x200/+420 ms и 0x300/+440 ms присутствуют во всех B и отсутствуют в A. Автотест ожидает 3/3 воспроизводимость после индивидуального START alignment. Эти значения — тестовые фикстуры, не данные автомобиля.

### Изменения цикла 017
- numbered trial для NORMAL_A/FAULT_B;
- Repeatability Engine;
- START-aligned pairwise aggregation;
- REPEATED IN ALL B / PARTIAL;
- median relative event time;
- endpoint repeatability;
- UI Repeatability Panel;
- automated six-trial simulation test;
- командный test walkthrough.

## 18. Hypothesis Manager
Добавлен evidence-bound менеджер диагностических гипотез. Стартовый набор для текущего расследования: **H1 ECM power/shutdown sequence**, **H2 CAN joint/network intermittent**, **H3 ECM KAM/internal retention**, **H4 common power/ground event**.

Каждая карточка содержит статус, конкретные evidence и **NEXT TEST**. Допустимые рабочие состояния интерфейса: **SUPPORTED, CONTRADICTED, INCONCLUSIVE, NOT_TESTED**. В текущей реализации автоматическое CONFIRMED отсутствует намеренно.

### Правило трактовки
SUPPORTED означает только, что имеющиеся наблюдения поддерживают дальнейшую проверку гипотезы. Это **не подтверждение root cause**. Например, повторяемое CAN-изменение во всех FAULT trials может перевести H2 в SUPPORTED, но не доказывает неисправность CAN joint. H1/H3/H4 при отсутствии прямых измерений питания/KAM/ground остаются INCONCLUSIVE.

### Следующие тесты
H1: измерить питание ECM при ON→OFF и проверить delayed shutdown. H2: выполнить контролируемый connector/wiggle capture с marker и проверить воспроизводимое multi-ID нарушение. H3: при стабильной сети проверить backup/keep-alive и retention path ECM. H4: сопоставить групповые CAN-события с прямыми измерениями питания/массы.

Командная software simulation сохранена в `docs/TEAM_SIMULATION_018.md`; автотест проверяет переход H2 в SUPPORTED на synthetic 3/3 CAN observation и сохранение H1 как INCONCLUSIVE. Никаких данных автомобиля этот тест не содержит.

### Изменения цикла 018
- Hypothesis Manager backend;
- четыре исходные проверяемые гипотезы;
- evidence-bound статусы без процентов вероятности;
- NEXT TEST для каждой гипотезы;
- API hypotheses;
- UI карточки hypothesis/evidence/next test;
- automated evidence-bound test;
- командная simulation 018.

## 19. OpenPort SD — подготовка автономной записи
Добавлена отдельная вкладка **OpenPort SD**. Она предназначена для подготовки и проверки `logcfg.txt` для автономного логирования OpenPort 2.0 на microSD.

### Что подтверждено исследованием
OpenPort 2.0 standalone logging использует файл `logcfg.txt` в корне microSD; существуют внешние генераторы, например OPCONFIG, которые формируют этот файл из выбранных PID. В распространённых CAN-примерах `type=obd` + `protocolid=6` означает ISO15765 OBD parameter logging и **отправляет диагностические запросы**. Поэтому SherloCAN не называет такой режим passive/raw CAN capture.

### Текущая вкладка
- редактор/вставка существующего `logcfg.txt`;
- validator имени файла, channel type и protocolid;
- явное предупреждение ACTIVE_DIAGNOSTIC_REQUESTS для `type=obd`;
- безопасный генератор базового Mode 01 шаблона RPM / Vehicle Speed / Coolant;
- сохранение готового файла с именем `logcfg.txt`;
- RAW standalone CAN профиль намеренно не генерируется, пока его синтаксис и поведение OpenPort 2.0 не будут подтверждены документацией или стендовым испытанием.

### Рабочий процесс
1. Подготовить microSD и открыть вкладку OpenPort SD.
2. Вставить проверенный config либо создать OBD-шаблон.
3. Нажать **ПРОВЕРИТЬ** и изучить warnings/features.
4. Сохранить `logcfg.txt` и поместить его в корень microSD.
5. Выполнить короткий контрольный автономный сеанс перед длительной поездкой.
6. Импорт полученных SD-логов в Evidence/Session будет добавлен следующим циклом.

### Ограничение для нашего P0603 расследования
Цель SherloCAN — пассивная forensic-запись CAN. Наличие автономного OBD logging в OpenPort не доказывает наличие подходящего passive raw-CAN standalone режима. До подтверждения этого режима ноутбук + J2534 остаётся основным путём RAW capture.

### Изменения цикла 019
- исследован подход OpenPort standalone/logcfg и существующий OPCONFIG;
- добавлен backend validator;
- добавлен Mode 01 template builder;
- добавлена вкладка OpenPort SD;
- добавлена загрузка/редактирование/валидация/сохранение logcfg.txt;
- активный OBD режим отделён от passive RAW CAN;
- добавлены safety tests.

## 20. OpenPort SD Import → Evidence
Вкладка OpenPort SD расширена вторым этапом **ИМПОРТ ЛОГОВ**. Оператор указывает путь к подключённой microSD/папке, SherloCAN сканирует поддерживаемые файлы `.csv`, `.log`, `.txt` (исключая `logcfg.txt`) и показывает имя, размер, формат и SHA-256.

При **IMPORT → EVIDENCE** исходный файл не изменяется. Создаётся отдельная evidence-copy в `data/captures/sd_imports/<session_id>/`, рассчитывается SHA-256 и сохраняется `import.json` с provenance: original path/name, evidence path, size, hash, import time и source kind `OPENPORT_SD_IMPORT`.

### Важное ограничение
Импорт файла ещё не означает, что SherloCAN знает его структуру. В цикле 020 metadata устанавливает `parsed=false`; программа не выдумывает CAN ID/timestamp/семантику неизвестного формата. Следующий этап — format detection/parsers только для реально подтверждённых OpenPort output formats, после чего импорт можно будет конвертировать в стандартный RAW Evidence и назначать A1/A2/A3/B1/B2/B3.

### Изменения цикла 020
- SD folder scan;
- список автономных логов;
- SHA-256 до импорта;
- immutable evidence-copy;
- provenance metadata import.json;
- UI PREPARE / IMPORT;
- тест сохранности исходника и SHA-256.

## 21. Автообнаружение SD и безопасное определение формата
Перед реализацией проведён reuse-first research; выводы сохранены в `docs/RESEARCH_OPENPORT_SD_021.md`. SherloCAN не пишет собственные парсеры для уже поддерживаемых отраслевых CAN-форматов: для подтверждённых frame-level форматов выбран `python-can`; `cantools` остаётся последующим DBC/decode слоем. OPCONFIG рассматривается как готовый подход к генерации `logcfg.txt`, поэтому общий PID-конфигуратор заново не изобретается.

### Автообнаружение
Кнопка **НАЙТИ SD** на Windows перечисляет removable drives. Наличие `logcfg.txt` или лог-файлов повышает полезность кандидата, но UI всегда показывает **OpenPort: NOT CONFIRMED** — один только тип диска не доказывает, что это карта OpenPort. Ручной путь сохранён как fallback.

### Определение формата
Парсер не выбирается только по расширению. Выполняется content sniffing. Подтверждённая строковая сигнатура can-utils/candump получает `RAW_CAN_SUPPORTED / python-can`; канонический SherloCAN CSV — `RAW_CAN_SUPPORTED / sherlocan-csv`; табличный CSV с именованными параметрами, но без CAN ID/frame data — `PARAMETER_LOG`; всё прочее — `UNKNOWN`.

`PARAMETER_LOG` не допускается к CAN-ID First Divergence как будто это RAW CAN. Неизвестный формат не конвертируется автоматически. Import по-прежнему сначала сохраняет оригинальные bytes + SHA-256 и записывает detection metadata.

### Почему выбран этот вариант
Это минимизирует риск ложной интерпретации Tactrix standalone CSV и одновременно повторно использует зрелые CAN readers. Точное распознавание Tactrix standalone dialect будет добавлено после получения реального файла с microSD пользователя и превращения его в regression fixture.

### Изменения цикла 021
- research/reuse review;
- Windows removable-drive discovery без новой зависимости;
- manual path fallback;
- content-based format detector;
- RAW_CAN_SUPPORTED / PARAMETER_LOG / UNKNOWN;
- python-can назначается только для распознанного candump;
- detection metadata включена в SD scan/import;
- UI показывает classification/confidence;
- regression tests не дают parameter CSV превратиться в RAW CAN.
