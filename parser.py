# parser.py
"""
Log parsing functions. Provides `extract_errors_from_log_text(log_text)` that returns a pandas DataFrame
with columns:
  timestamp (datetime), timestamp_raw, module, level, message, exception, exc_message, category_key, raw_traceback
"""

import re
from dateutil import parser as dateparser
import pandas as pd
from typing import Optional

from errors_mapping import SUB_TO_CAT

# Regex patterns (robust heuristics)
LOG_LINE_RE = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s*-\s*(?P<module>[^-]+?)\s*-\s*(?P<level>[A-Z]+)\s*-\s*(?P<message>.*)$'
)
EXC_LINE_RE = re.compile(
    r'^\s*(?P<exc>[A-Za-z_][\w\.\:\-<>]*?(?:Error|Exception|Warning|Exit|Interrupt)?)\s*[:]\s*(?P<msg>.*)$'
)
SINGLELINE_EXC_RE = re.compile(
    r'(?P<exc>[A-Za-z_][\w\.\:\-<>]*?(?:Error|Exception|Warning|Exit|Interrupt)?)\s*[:\-]\s*(?P<msg>.+)$'
)


def parse_timestamp(ts_str: str) -> Optional[pd.Timestamp]:
    try:
        return dateparser.parse(ts_str.replace(',', '.'))
    except Exception:
        return None


def extract_errors_from_log_text(log_text: str) -> pd.DataFrame:
    lines = log_text.splitlines()
    entries = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].rstrip("\n")
        m = LOG_LINE_RE.match(line)
        if m:
            ts_raw = m.group("ts")
            ts = parse_timestamp(ts_raw)
            module = m.group("module").strip()
            level = m.group("level").strip()
            message = m.group("message").strip()

            exc_name = None
            exc_msg = ""
            single_m = SINGLELINE_EXC_RE.search(message)
            if single_m:
                exc_name = single_m.group("exc")
                exc_msg = single_m.group("msg").strip()

            raw_tb = ""
            # capture traceback block if next line begins with Traceback...
            if (i + 1) < n and lines[i + 1].lstrip().startswith("Traceback (most recent call last):"):
                tb_lines = []
                j = i + 1
                while j < n:
                    tb_lines.append(lines[j])
                    ex_m = EXC_LINE_RE.match(lines[j].strip())
                    if ex_m:
                        exc_name = ex_m.group("exc")
                        exc_msg = ex_m.group("msg").strip()
                        j += 1
                        break
                    j += 1
                raw_tb = "\n".join(tb_lines)
                i = j - 1

            if not exc_name:
                ex_m2 = EXC_LINE_RE.search(message)
                if ex_m2:
                    exc_name = ex_m2.group("exc")
                    exc_msg = ex_m2.group("msg").strip()

            cat_key = SUB_TO_CAT.get(exc_name)

            entries.append({
                "timestamp": ts,
                "timestamp_raw": ts_raw if ts else None,
                "module": module or None,
                "level": level or None,
                "message": message,
                "exception": exc_name,
                "exc_message": exc_msg or "",
                "category_key": cat_key,
                "raw_traceback": raw_tb
            })
        else:
            # traceback-only segment
            if line.lstrip().startswith("Traceback (most recent call last):"):
                tb_lines = [line]
                j = i + 1
                exc_name = None
                exc_msg = ""
                while j < n:
                    tb_lines.append(lines[j])
                    ex_m = EXC_LINE_RE.match(lines[j].strip())
                    if ex_m:
                        exc_name = ex_m.group("exc")
                        exc_msg = ex_m.group("msg").strip()
                        break
                    j += 1
                cat_key = SUB_TO_CAT.get(exc_name)
                entries.append({
                    "timestamp": None,
                    "timestamp_raw": None,
                    "module": None,
                    "level": "ERROR",
                    "message": "(traceback-only entry)",
                    "exception": exc_name,
                    "exc_message": exc_msg or "",
                    "category_key": cat_key,
                    "raw_traceback": "\n".join(tb_lines)
                })
                i = j
        i += 1

    df = pd.DataFrame(entries)
    if df.empty:
        return df
    # Add derived columns
    from errors_mapping import CATEGORY_MAPPING  # avoid circular at top
    df["category"] = df["category_key"].map(lambda k: CATEGORY_MAPPING[k]["category"] if k in CATEGORY_MAPPING else ("Unknown" if pd.notnull(k) else None))
    df["date"] = df["timestamp"].dt.date
    df["time"] = df["timestamp"].dt.time
    return df
