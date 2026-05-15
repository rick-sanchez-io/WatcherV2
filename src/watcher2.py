import sqlite3
import subprocess
import time
from typing import Iterable, List, Optional, Sequence, Set, Tuple

DB_PATH = "/etc/x-ui/x-ui.db"
CHECK_INTERVAL = 1
RECHECK_INTERVAL = 60


expired_users: Set[str] = set()
_last_expired_recheck = 0.0
_bootstrapped = False


def _placeholders(items: Sequence[str]) -> str:
    return ",".join(["?"] * len(items))


def read_clients(
    include_emails: Optional[Iterable[str]] = None,
    exclude_emails: Optional[Iterable[str]] = None,
) -> List[Tuple[str, float, float]]:
    include_list = list(include_emails or [])
    exclude_list = list(exclude_emails or [])

    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        query = "SELECT email, total, up + down AS used FROM client_traffics"
        params: List[str] = []

        if include_list:
            query += f" WHERE email IN ({_placeholders(include_list)})"
            params = include_list
        elif exclude_list:
            query += f" WHERE email NOT IN ({_placeholders(exclude_list)})"
            params = exclude_list

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def kill_xray() -> None:
    subprocess.run(["pkill", "-f", "xray"], check=True)


def _is_unlimited(total: float) -> bool:
    return total <= 0


_RESET = "[0m"
_DIM = "[2m"
_CYAN = "[36m"
_GREEN = "[32m"
_YELLOW = "[33m"
_RED = "[31m"
_MAGENTA = "[35m"
_BLUE = "[34m"


def _colorize(message: str) -> str:
    if message.startswith("[ERROR]"):
        return f"{_RED}{message}{_RESET}"
    if message.startswith("[WARN]"):
        return f"{_YELLOW}{message}{_RESET}"
    if message.startswith("[BOOTSTRAP]"):
        return f"{_MAGENTA}{message}{_RESET}"
    if message.startswith("[RECHECK]"):
        return f"{_BLUE}{message}{_RESET}"
    if message.startswith("[INFO]"):
        return f"{_GREEN}{message}{_RESET}"
    return f"{_CYAN}{message}{_RESET}"


def log(message: str) -> None:
    print(_colorize(message))


def process_once(
    reader=read_clients,
    killer=kill_xray,
    now_fn=time.monotonic,
) -> None:
    global _last_expired_recheck, _bootstrapped

    now = now_fn()

    rows = reader(exclude_emails=expired_users)

    newly_expired_users = []

    for email, total, used in rows:
        log(f"{email} | total: {total} | used: {used}")

        if _is_unlimited(total):
            if email in expired_users:
                expired_users.discard(email)
                log(f"[INFO] {email} is unlimited (total={total}) and removed from expired list.")
            else:
                log(f"[INFO] {email} is unlimited (total={total}); skipping limit check.")
            continue

        if used > total and email not in expired_users:
            newly_expired_users.append((email, total, used))
            expired_users.add(email)

    if not _bootstrapped:
        _bootstrapped = True
        _last_expired_recheck = now
        if newly_expired_users:
            for email, total, used in newly_expired_users:
                log(f"[BOOTSTRAP] {email} exceeded limit before watcher start: used={used}, total={total}")
            log("[BOOTSTRAP] Initial state loaded; xray will not be killed for pre-existing expired users.")
    elif newly_expired_users:
        for email, total, used in newly_expired_users:
            log(f"[WARN] {email} exceeded limit: used={used}, total={total}")

        log("[WARN] Killing xray...")
        killer()
        log("[WARN] xray killed.")

    if expired_users and now - _last_expired_recheck >= RECHECK_INTERVAL:
        rows = reader(include_emails=expired_users)
        restored_users = []

        for email, total, used in rows:
            log(f"[RECHECK] {email} | total: {total} | used: {used}")

            if _is_unlimited(total) or used <= total:
                restored_users.append(email)

        for email in restored_users:
            expired_users.discard(email)
            log(f"[INFO] {email} is active again and will be read normally.")

        _last_expired_recheck = now


def main() -> None:
    while True:
        try:
            process_once()
        except Exception as e:
            log(f"[ERROR] {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
