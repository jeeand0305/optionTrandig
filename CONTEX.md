# КОНТЕКСТ: проект OptionTrandig (Bybit-бот)

## Что случилось
Торговый бот принёс убытки ~89 USDT за период 14.09–13.10.2026.
Остановлен 13.10.2026. Сейчас выключен (screen -ls → пусто).
Сервер остановлен, бот не работает — срочности по деньгам нет.

## Среда
- Сервер: root@46.8.124.233, путь /root/optionTrandig
- Репозиторий: github.com/jeeand0305/optionTrandig, ветка develop
- Локально: C:\Users\X270\Documents\github1leesonSshGit\ProjectOption
- venv: C:\Users\X270\Documents\github1leesonSshGit\ProjectOption\.venv
- PostgreSQL локально: база demo (632 фьючерса + 9 опционов)
- PostgreSQL на сервере: база directorDB (не пулили)
- pgAdmin 4 — смотрим данные

## Найденные причины убытков (из bot.log.2)
1. close_hedge_position() missing argument 'target_symbol' — 08–10.10
2. ab not enough for new order (retCode 110007) на XRP — с 27.09
3. retCode 10002 (timestamp drift > 5 сек recv_window) — постоянно с 27.09
4. is_futures_data_valid не чистил монеты с пустым списком фьючерсов
   → open_futures = [] (не None) → хедж не открывался → накопление позиций

## Коммиты (develop)
- 35652a39  1.0.5  is_futures_data_valid — фикс пустого списка (запушен)
- fcf51037  1.0.4  СЛОМАННЫЙ (убрана крипта из хеджа, clear_futures падает с TypeError)
- 1e385abe  1.0.3  закомментирован close_hedge_position в analizCallStrike/analizPutStrike
- 6ea7c25f  1.0.2
- e4ac8835  1.0.0  positionIdx в close_hedge_position
- [?]      1.0.6 [TEST] fix/no_rehedge — закомментирован open_hedge_order
           (проверить: запушен ли, влит ли в develop)
- [?]      1.0.7 [PLAN→?] NTP на сервере для фикса retCode 10002
           (что именно сделано: установка NTP / код / конфиг — заполнить)

## refactoring.txt — история (обновить после переписывания под 1.0.7)
- 1.0.0: positionIdx + pos_idx для close_hedge_position
- 1.0.1: фиксы analiz_inverted_corridor
- 1.0.2: фикс времени в __init__
- 1.0.3: улучшение analizCallStrike/analizPutStrike + увеличено время итерации
         ЗАКОММЕНТИРОВАН close_hedge_position (причина ошибки missing arg)
- 1.0.4: убрана крипта (SOL, DOGE) из хеджа, сломан clear_futures
- 1.0.5 [PROD/merged]: is_futures_data_valid — обработка пустого списка + set()
         Тесты: 8/8 в testCod2.py (файл перенесён в bybitOptionStratge/)
- 1.0.6 [TEST]: fix/no_rehedge — закомментирован open_hedge_order в
         analizCallStrike/analizPutStrike (отключить улучшение позиции полностью,
         т.к. в 1.0.3 отключили только закрытие, а открытие осталось → накопление)
- 1.0.7 [?]: NTP + фикс retCode 10002 — ЧТО ИМЕННО СДЕЛАНО: ...
         (заполнить: установка chrony/ntp на сервере, правки recv_window, тесты)

## Файлы проекта
ETL (загрузка истории Bybit в PostgreSQL):
- directorDB/config.py    — DBConfig, load_db_config() из .env
- directorDB/db.py        — get_connection, create_schema (таблицы futures_positions, options_positions)
- directorDB/extract.py   — fetch_futures_positions, fetch_options_positions (Bybit Closed P&L)
- directorDB/repository.py — FuturesRepository, OptionsRepository (save_many)
- directorDB/load_history.py — точка входа: python directorDB/load_history.py --days 30

Торговый бот:
- bybitOptionStratge/bybit_client.py — основной файл, класс BybitOptionBot
  * analizCallStrike — защита CALL-ноги
  * analizPutStrike — защита PUT-ноги
  * close_hedge_position(target_symbol, target_side, qty, pos_idx)
  * open_hedge_order(target_symbol, side, qty)
  * is_futures_data_valid — валидация фьючерсов
  * aggregate_coin_data — агрегатор данных монеты
- bybitOptionStratge/main.py — точка входа бота
- bybitOptionStratge/method_symbols.py — OptionAsset (парсер опционных символов)
- bybitOptionStratge/configBybit.py

## Запуск ETL (из корня проекта, локально)
.\.venv\Scripts\python.exe directorDB\load_history.py --days 30
Пишет в PostgreSQL: localhost:5432/demo, user=postgres
В логе: Фьючерсы: 632, Опционы: 9

## Запуск тестов
.\.venv\Scripts\python.exe testCod2.py   (из папки bybitOptionStratge)

## Что НЕ сделано
- [?] 1.0.6 [TEST]: протестировать закомментированный open_hedge_order
      (статус: запушен? влит? тест пройден?)
- [?] 1.0.7: NTP — что осталось (проверить на сервере, что drift < 5 сек)
- 1.0.8 [PLAN]: обработка ab not enough for new order (retCode 110007)
- Слить всё в develop и запулить на сервер
- На сервере бот всё ещё на [?] (было 1.0.4 — проверить актуальную версию)
- Анализ: почему −89 USDT — баги / комиссии / стратегия (дашборд Pandas+Streamlit)
- Внешняя память: раздел "Логика стратегии своими словами" в CONTEXT.md

## Как продолжить
Открой новый чат, скинь этот CONTEXT.md + файлы:
- bybitOptionStratge/refactoring.txt
- bybitOptionStratge/bybit_client.py (или кусок с analizCallStrike/analizPutStrike)
Скажи: "Продолжаем 1.0.7/1.0.8. Смотри CONTEXT.md."