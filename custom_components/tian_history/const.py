"""常量 - 天聚数行API版本."""
import os
import logging

DOMAIN = "tian_history"
API_URL = "https://apis.tianapi.com/lishi/index"

DEFAULT_SCROLL_INTERVAL = 30

ATTR_TODAY_ITEM = "today_item"
ATTR_HISTORY_LIST = "history_list"
ATTR_TOTAL_COUNT = "total_count"
ATTR_SCROLL_INDEX = "scroll_index"
ATTR_CURRENT_DATE = "current_date"
ATTR_UPDATE_TIME = "update_time"
ATTR_SCROLL_INTERVAL = "scroll_interval"

SENSITIVE_WORDS_FILE = "sensitive_words.txt"

def load_sensitive_words(hass_config_dir: str) -> list:
    """从文件中加载敏感词列表，若文件不存在则返回默认列表。"""
    default_words = ["去世", "逝世", "诞辰", "病故", "病逝", "死亡", "出生", "身亡", "自杀", "长逝", "长辞", "葬"]
    file_path = os.path.join(hass_config_dir, "custom_components", DOMAIN, SENSITIVE_WORDS_FILE)
    if not os.path.exists(file_path):
        return default_words
    words = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                words.append(line)
        return words if words else default_words
    except Exception:
        return default_words

FORBIDDEN_KEYWORDS = ["去世", "逝世", "诞辰", "病故", "病逝", "死亡", "身亡", "自杀", "长逝", "长辞", "葬"]        