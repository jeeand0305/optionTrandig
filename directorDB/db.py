"""
Подключение к PostgreSQL и создание схемы.
"""
import psycopg2
from directorDB.config import DBConfig
from logger import logger



def get_connection(config: DBConfig):
    """
    Открывает соединение с PostgreSQL.
    Один вызов = одно соединение. Закрывать — на стороне вызывающего.
    """
    logger.info(f"Подключение к PostgreSQL {config.host}:"
                f"{config.port}/{config.dbname}")
    return psycopg2.connect(
        dbname=config.dbname,
        user=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
    )


# def to_row(t):
#     raw_deliv = t.get("deliveryFee")
#     return {
#         "order_id":        None,
#         "symbol":          t["symbol"],
#         "ccxt_symbol":     None,
#         "futures_symbol":  None,
#         "expiry_date":     t.get("expiry"),
#         "strike_price":    t.get("strike"),
#         "option_type":     t.get("type"),
#         "side":            t.get("side"),
#         "qty":             t.get("qty"),
#         "avg_entry_price": t.get("entry"),
#         "avg_exit_price":  t.get("exit"),
#         "total_pnl":       t.get("pnl_usdt"),
#         "fees_usdt":       t.get("fees_usdt"),
#         "total_open_fee":  None,
#         "total_close_fee": None,
#         "delivery_fee":    delivery_fee_db(raw_deliv),
#         "delivery_price":  t.get("exit") if str(raw_deliv or "").strip() else None,
#         "open_time":       t.get("open_time"),
#         "close_time":      t.get("close_time"),
#     }

def create_schema(conn) -> None:
    """
    Создаёт таблицы futures_positions и options_positions.
    futures_positions — идемпотентно (IF NOT EXISTS).
    options_positions — пересоздаётся (DROP + CREATE), схема новая.
    """
    with conn.cursor() as cur:

        # -------------------- ФЬЮЧЕРСЫ --------------------
        cur.execute("""
            CREATE TABLE IF NOT EXISTS futures_positions (
                id                BIGSERIAL PRIMARY KEY,
                order_id          VARCHAR(50),
                symbol            VARCHAR(50) NOT NULL,
                side              VARCHAR(10),
                qty               NUMERIC(20, 8),
                avg_entry_price   NUMERIC(20, 8),
                avg_exit_price    NUMERIC(20, 8),
                closed_pnl        NUMERIC(20, 8),
                open_fee          NUMERIC(20, 8),
                close_fee         NUMERIC(20, 8),
                funding_fee       NUMERIC(20, 8) DEFAULT 0,
                open_time         TIMESTAMPTZ,
                close_time        TIMESTAMPTZ,
                loaded_at         TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE (order_id, close_time)
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_futures_symbol_time
                ON futures_positions (symbol, close_time DESC)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_futures_close_time
                ON futures_positions (close_time DESC)
        """)

        # -------------------- ОПЦИОНЫ --------------------
        cur.execute("DROP TABLE IF EXISTS options_positions CASCADE;")
        cur.execute("""
            CREATE TABLE options_positions (
                id                BIGSERIAL PRIMARY KEY,
                symbol            VARCHAR(100) NOT NULL,
                expiry_date       DATE,
                strike_price      NUMERIC(20, 8),
                option_type       VARCHAR(4),
                side              VARCHAR(10),
                qty               NUMERIC(20, 8),
                avg_entry_price   NUMERIC(20, 8),
                avg_exit_price    NUMERIC(20, 8),
                total_pnl         NUMERIC(20, 8),
                fees_usdt         NUMERIC(20, 8),
                delivery_fee      NUMERIC(20, 8),
                delivery_price    NUMERIC(20, 8),
                open_time         TIMESTAMPTZ,
                close_time        TIMESTAMPTZ,
                loaded_at         TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE UNIQUE INDEX uq_options_trade
                ON options_positions (symbol, side, close_time)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_options_expiry
                ON options_positions (expiry_date)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_options_strike
                ON options_positions (strike_price, option_type)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_options_close_time
                ON options_positions (close_time DESC)
        """)

    conn.commit()
    logger.info('Схема БД создана/проверена')

    # conn.commit()
    # logger.info('Схема БД создана/проверена')