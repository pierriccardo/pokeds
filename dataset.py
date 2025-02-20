import os
import consts
import logger
import logging
import pandas as pd

from db import DB

logger.setup()
logger = logging.getLogger(__name__)


db = DB()

format = '[Gen 9] Random Battle'
N = 1000
query = f"SELECT id, format, rating, log FROM logs WHERE format == '{format}' ORDER BY RANDOM() LIMIT {N}"

conn = db.connect()

df = pd.read_sql_query(query, conn)
df.to_csv(f"{consts.to_compact_notation(format)}-{N}.csv", index=False)

conn.close()





