# utils/date_util.py
from datetime import datetime

def parse_date(date_str: str) -> datetime:
    """
    解析日期字符串，支持以下格式：
    - "DD/MM/YYYY HH:MM"
    - "DD/MM/YYYY" （默认时间为 00:00）
    如果解析失败，则返回 None。
    """
    formats = ["%d/%m/%Y %H:%M", "%d/%m/%Y"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # 如果只输入日期，则默认时间为 00:00
            if fmt == "%d/%m/%Y":
                dt = dt.replace(hour=0, minute=0)
            return dt
        except ValueError:
            continue
    return None
