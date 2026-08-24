import os
import time
from datetime import datetime

import psycopg2
from flask import Flask, render_template

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "tpa-postgresql"),
    "port": os.environ.get("DB_PORT", "5432"),
    "dbname": os.environ.get("DB_NAME", "tpadb"),
    "user": os.environ.get("DB_ADMIN", "postgres"),
    "password": os.environ.get("DB_ADMIN_PASSWORD", ""),
}

STATS_QUERY = """
SELECT
  pg_size_pretty(pg_database_size(current_database())) AS db_size,
  (SELECT count(*) FROM pg_stat_activity
   WHERE state = 'active' AND pid != pg_backend_pid()) AS active,
  (SELECT count(*) FROM pg_stat_activity
   WHERE state = 'idle in transaction') AS idle_txn,
  (SELECT count(*) FROM pg_stat_activity
   WHERE pid != pg_backend_pid()) AS total_conns,
  (SELECT coalesce(extract(epoch from max(now() - xact_start))::int, 0)
   FROM pg_stat_activity
   WHERE state != 'idle' AND pid != pg_backend_pid()) AS txn_secs,
  (SELECT pg_size_pretty(sum(size)) FROM pg_ls_waldir()) AS wal_size
"""

TABLE_SIZES_QUERY = """
SELECT
  schemaname || '.' || relname AS table_name,
  pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
  n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 15
"""

ACTIVITY_QUERY = """
SELECT
  state,
  count(*) AS count,
  coalesce(max(extract(epoch from now() - xact_start))::int, 0) AS max_duration_secs
FROM pg_stat_activity
WHERE pid != pg_backend_pid()
GROUP BY state
ORDER BY count DESC
"""


def get_db_stats():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_session(autocommit=True)
        cur = conn.cursor()

        cur.execute(STATS_QUERY)
        row = cur.fetchone()
        stats = {
            "db_size": row[0],
            "active": row[1],
            "idle_txn": row[2],
            "total_conns": row[3],
            "txn_secs": row[4],
            "wal_size": row[5],
        }

        txn = stats["txn_secs"]
        if txn and txn > 0:
            stats["txn_display"] = f"{txn // 60}m{txn % 60}s"
        else:
            stats["txn_display"] = "-"

        stats["is_busy"] = stats["active"] > 0 or stats["idle_txn"] > 0
        stats["status"] = "INGESTING" if stats["is_busy"] else "IDLE"

        cur.execute(TABLE_SIZES_QUERY)
        stats["tables"] = [
            {"name": r[0], "size": r[1], "rows": r[2]} for r in cur.fetchall()
        ]

        cur.execute(ACTIVITY_QUERY)
        stats["activity"] = [
            {
                "state": r[0] if r[0] else 'pg_sql background workers (<code>pg_stat_activity.state == NULL</code>)',
                "is_null_state": r[0] is None,
                "count": r[1],
                "max_duration": r[2],
            }
            for r in cur.fetchall()
        ]

        stats["error"] = None
        cur.close()
        conn.close()
    except Exception as e:
        stats = {"error": str(e), "status": "ERROR", "is_busy": False}

    stats["timestamp"] = datetime.now().strftime("%H:%M:%S")
    return stats


@app.route("/")
def index():
    stats = get_db_stats()
    return render_template("index.html", stats=stats, refresh_interval=10)


@app.route("/healthz")
def healthz():
    return "ok"
