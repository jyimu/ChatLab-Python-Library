
"""
ChatLab 工具函数
"""

import re
from datetime import datetime
from typing import Optional


def parse_timestamp(ts) -> datetime:
    """
    解析时间戳
    支持秒级和毫秒级时间戳
    """
    ts = int(ts)
    # 检测毫秒级时间戳（长度 > 10）
    if ts > 1e10:
        ts = ts / 1000
    return datetime.fromtimestamp(ts)


def format_timestamp(dt: datetime, milliseconds: bool = False) -> int:
    """格式化时间为时间戳"""
    ts = dt.timestamp()
    if milliseconds:
        return int(ts * 1000)
    return int(ts)


def escape_content(content: str) -> str:
    """转义内容中的特殊字符"""
    return content.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')


def unescape_content(content: str) -> str:
    """反转义内容"""
    return content.encode('utf-8').decode('unicode_escape')


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_mentions(content: str) -> list:
    """提取 @提及的用户"""
    pattern = r'@([^\s@]+)'
    return re.findall(pattern, content)


def extract_urls(content: str) -> list:
    """提取 URL 链接"""
    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, content)


def extract_emails(content: str) -> list:
    """提取邮箱地址"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, content)


def mask_sensitive_info(content: str, mask: str = "***") -> str:
    """
    脱敏处理
    隐藏手机号、身份证号等敏感信息
    """
    # 手机号
    content = re.sub(r'1[3-9]\d{9}', mask, content)
    # 身份证号
    content = re.sub(r'\d{17}[\dXx]', mask, content)
    # 银行卡号
    content = re.sub(r'\d{16,19}', mask, content)
    return content


def calculate_reading_time(content: str, words_per_minute: int = 300) -> int:
    """
    估算阅读时间（秒）

    Args:
        content: 文本内容
        words_per_minute: 每分钟阅读字数
    """
    # 中文字符 + 英文单词
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    english_words = len(re.findall(r'[a-zA-Z]+', content))

    total_words = chinese_chars + english_words
    minutes = total_words / words_per_minute
    return max(1, int(minutes * 60))


def split_messages_by_time(messages, max_gap_minutes: int = 30):
    """
    按时间间隔分割消息列表

    Returns:
        对话片段列表
    """
    if not messages:
        return []

    chunks = []
    current_chunk = [messages[0]]

    for i in range(1, len(messages)):
        prev_msg = messages[i-1]
        curr_msg = messages[i]

        gap = (curr_msg.timestamp - prev_msg.timestamp) / 60

        if gap > max_gap_minutes:
            chunks.append(current_chunk)
            current_chunk = [curr_msg]
        else:
            current_chunk.append(curr_msg)

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
