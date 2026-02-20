
"""
ChatLab 格式导出器
支持导出为标准 JSON 和 JSON Lines 格式
"""

import json
from pathlib import Path
from typing import Union, Optional, Iterator
from ..models import ChatSession, ChatMessage


class JSONExporter:
    """JSON 格式导出器"""

    def export(self, session: ChatSession, 
               filepath: Union[str, Path],
               indent: Optional[int] = 2,
               encoding: str = "utf-8",
               ensure_ascii: bool = False):
        """
        导出为 JSON 文件

        Args:
            session: ChatSession 对象
            filepath: 输出文件路径
            indent: 缩进空格数（None 表示紧凑格式）
            encoding: 文件编码
            ensure_ascii: 是否转义非 ASCII 字符
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = session.to_dict()
        json_str = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
        filepath.write_text(json_str, encoding=encoding)

    def export_string(self, session: ChatSession, 
                     indent: Optional[int] = 2,
                     ensure_ascii: bool = False) -> str:
        """导出为 JSON 字符串"""
        return session.to_json(indent=indent, ensure_ascii=ensure_ascii)


class JSONLExporter:
    """
    JSON Lines 格式导出器
    适用于大文件，流式处理
    """

    def export(self, session: ChatSession,
               filepath: Union[str, Path],
               encoding: str = "utf-8"):
        """
        导出为 JSONL 格式

        格式：
        {"_type": "header", "chatlab": {...}, "meta": {...}}
        {"_type": "member", ...}
        {"_type": "message", ...}
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding=encoding) as f:
            # 写入 header
            header = {
                "_type": "header",
                "chatlab": session.chatlab.to_dict(),
                "meta": session.meta.to_dict()
            }
            f.write(json.dumps(header, ensure_ascii=False) + '\n')

            # 写入成员
            for member in session.members:
                member_line = {"_type": "member", **member.to_dict()}
                f.write(json.dumps(member_line, ensure_ascii=False) + '\n')

            # 写入消息
            for msg in session.messages:
                msg_line = {"_type": "message", **msg.to_dict()}
                f.write(json.dumps(msg_line, ensure_ascii=False) + '\n')

    def export_stream(self, session: ChatSession) -> Iterator[str]:
        """流式导出，生成器方式"""
        # Header
        header = {
            "_type": "header",
            "chatlab": session.chatlab.to_dict(),
            "meta": session.meta.to_dict()
        }
        yield json.dumps(header, ensure_ascii=False)

        # Members
        for member in session.members:
            member_line = {"_type": "member", **member.to_dict()}
            yield json.dumps(member_line, ensure_ascii=False)

        # Messages
        for msg in session.messages:
            msg_line = {"_type": "message", **msg.to_dict()}
            yield json.dumps(msg_line, ensure_ascii=False)


class CSVExporter:
    """CSV 格式导出器"""

    def export(self, session: ChatSession,
               filepath: Union[str, Path],
               encoding: str = "utf-8",
               delimiter: str = ","):
        """导出为 CSV 文件"""
        import csv

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', newline='', encoding=encoding) as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(['timestamp', 'datetime', 'sender', 'account_name', 'type', 'content'])

            for msg in session.messages:
                writer.writerow([
                    msg.timestamp,
                    msg.datetime_str,
                    msg.sender,
                    msg.account_name,
                    msg.type,
                    msg.content
                ])
