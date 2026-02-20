"""
ChatLab - 聊天记录分析库

符合 ChatLab Standard Format Specification v0.0.1
支持解析、导出、分析多种聊天记录格式

基本用法:
    >>> import chatlab
    >>> session = chatlab.load("chat.json")
    >>> print(f"共 {len(session.messages)} 条消息")
    >>> session.save("output.json")

版本: 0.1.0
作者: ChatLab Community
"""

__version__ = "0.1.0"
__author__ = "ChatLab Community"

# 核心模型
from .models import (
    ChatSession,
    ChatMessage,
    ChatMember,
    ChatMeta,
    ChatLabVersion,
    MessageType
)

# 解析器
from .parsers import (
    JSONParser,
    AutoParser,
    CSVParser
)

# 导出器
from .exporters import (
    JSONExporter,
    JSONLExporter,
    CSVExporter
)

# 工具函数
from .utils import (
    parse_timestamp,
    format_timestamp,
    extract_mentions,
    extract_urls,
    mask_sensitive_info
)


def load(source, format: str = "auto", **kwargs) -> ChatSession:
    """
    加载聊天记录文件

    Args:
        source: 文件路径或字符串内容
        format: 格式类型 ("auto", "json", "jsonl", "csv")
        **kwargs: 额外的解析参数

    Returns:
        ChatSession 对象

    Examples:
        >>> session = chatlab.load("chat.json")
        >>> session = chatlab.load("chat.csv", platform="wechat")
    """
    if format == "auto":
        parser = AutoParser()
    elif format == "json" or format == "jsonl":
        from .parsers.json_parser import JSONParser
        parser = JSONParser()
        if format == "jsonl":
            return parser.parse_jsonl(source, **kwargs)
    elif format == "csv":
        from .parsers.csv_parser import CSVParser
        parser = CSVParser()
    else:
        raise ValueError(f"不支持的格式: {format}")

    return parser.parse(source, **kwargs)


def loads(text: str, format: str = "auto", **kwargs) -> ChatSession:
    """
    从字符串加载聊天记录

    Args:
        text: JSON/CSV 字符串
        format: 格式类型
        **kwargs: 额外的解析参数
    """
    return load(text, format=format, **kwargs)


def save(session: ChatSession, filepath: str, format: str = "json", **kwargs):
    """
    保存聊天记录到文件

    Args:
        session: ChatSession 对象
        filepath: 输出文件路径
        format: 输出格式 ("json", "jsonl", "csv")
        **kwargs: 额外的导出参数
    """
    if format == "json":
        exporter = JSONExporter()
        exporter.export(session, filepath, **kwargs)
    elif format == "jsonl":
        exporter = JSONLExporter()
        exporter.export(session, filepath, **kwargs)
    elif format == "csv":
        exporter = CSVExporter()
        exporter.export(session, filepath, **kwargs)
    else:
        raise ValueError(f"不支持的格式: {format}")


def saves(session: ChatSession, format: str = "json", **kwargs) -> str:
    """
    导出为字符串

    Args:
        session: ChatSession 对象
        format: 输出格式 ("json", "jsonl")
        **kwargs: 额外的导出参数

    Returns:
        格式化的字符串
    """
    if format == "json":
        return session.to_json(**kwargs)
    elif format == "jsonl":
        exporter = JSONLExporter()
        return "\n".join(exporter.export_stream(session))
    else:
        raise ValueError(f"不支持的字符串格式: {format}")


# 便捷函数
parse = load
parse_string = loads
dump = save
dumps = saves
