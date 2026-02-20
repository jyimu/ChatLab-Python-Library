
"""
CSV 格式解析器
支持将 CSV 聊天记录转换为 ChatLab 标准格式
"""

import csv
from pathlib import Path
from typing import Union, List, Dict, Any
from datetime import datetime
from ..models import ChatSession, ChatMessage, ChatMeta, ChatLabVersion, ChatMember


class CSVParser:
    """
    CSV 聊天记录解析器

    支持常见 CSV 格式：
    - WeChat 导出格式（时间, 发送者, 内容）
    - QQ 导出格式
    - 通用格式（timestamp, sender, content）
    """

    # 常见列名映射
    COLUMN_MAPPINGS = {
        'time': ['time', 'timestamp', '日期', '时间', 'Time', 'Timestamp'],
        'sender': ['sender', 'sender_id', '发送者', '用户', 'Sender', 'From'],
        'content': ['content', 'message', '内容', '消息', 'Content', 'Message'],
        'name': ['name', 'account_name', '昵称', 'Name', 'SenderName'],
        'type': ['type', 'msg_type', '类型', 'Type']
    }

    def __init__(self):
        self.column_map = {}

    def parse(self, source: Union[str, Path], 
              platform: str = "unknown",
              chat_name: str = "Unknown",
              encoding: str = "utf-8",
              delimiter: str = ",",
              **kwargs) -> ChatSession:
        """
        解析 CSV 文件

        Args:
            source: CSV 文件路径或内容
            platform: 平台标识（wechat, qq, etc.）
            chat_name: 聊天名称
            encoding: 文件编码
            delimiter: 分隔符
            **kwargs: 额外的元数据
        """
        if isinstance(source, (str, Path)) and Path(source).exists():
            filepath = Path(source)
            with open(filepath, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = list(reader)
        else:
            import io
            f = io.StringIO(source)
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)

        if not rows:
            raise ValueError("CSV 文件为空")

        # 自动检测列映射
        self._detect_columns(rows[0].keys())

        # 解析消息
        messages = []
        members_map = {}

        for idx, row in enumerate(rows):
            msg = self._parse_row(row, idx)
            if msg:
                messages.append(msg)
                # 收集成员信息
                if msg.sender not in members_map:
                    members_map[msg.sender] = msg.account_name

        # 构建成员列表
        members = [
            ChatMember(platform_id=sender, account_name=name)
            for sender, name in members_map.items()
        ]

        # 构建会话
        chatlab = ChatLabVersion(
            version="0.0.1",
            exported_at=int(datetime.now().timestamp()),
            generator="chatlab-csv-parser"
        )

        meta = ChatMeta(
            name=chat_name,
            platform=platform,
            type=kwargs.get("chat_type", "private"),
            owner_id=kwargs.get("owner_id", "")
        )

        return ChatSession(
            chatlab=chatlab,
            meta=meta,
            members=members,
            messages=messages
        )

    def _detect_columns(self, headers: List[str]):
        """自动检测列名映射"""
        headers_lower = [h.lower().strip() for h in headers]

        for standard_name, variants in self.COLUMN_MAPPINGS.items():
            for variant in variants:
                if variant.lower() in headers_lower:
                    idx = headers_lower.index(variant.lower())
                    self.column_map[standard_name] = headers[idx]
                    break

    def _parse_row(self, row: Dict[str, str], idx: int) -> ChatMessage:
        """解析单行数据"""
        # 获取时间戳
        time_col = self.column_map.get('time', 'time')
        timestamp_str = row.get(time_col, '')

        try:
            # 尝试多种时间格式
            timestamp = self._parse_timestamp(timestamp_str)
        except:
            timestamp = idx  # 使用行号作为备用

        # 获取发送者
        sender_col = self.column_map.get('sender', 'sender')
        sender = row.get(sender_col, 'unknown')

        # 获取显示名称
        name_col = self.column_map.get('name', sender_col)
        account_name = row.get(name_col, sender)

        # 获取内容
        content_col = self.column_map.get('content', 'content')
        content = row.get(content_col, '')

        # 获取类型
        type_col = self.column_map.get('type', 'type')
        type_val = int(row.get(type_col, 0)) if row.get(type_col) else 0

        return ChatMessage(
            sender=sender,
            account_name=account_name,
            timestamp=timestamp,
            type=type_val,
            content=content,
            platform_message_id=f"csv_{idx}"
        )

    def _parse_timestamp(self, ts_str: str) -> int:
        """解析各种时间格式"""
        ts_str = str(ts_str).strip()

        # 尝试 Unix 时间戳
        try:
            return int(float(ts_str))
        except:
            pass

        # 尝试常见日期格式
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d",
            "%H:%M:%S",
            "%Y年%m月%d日 %H:%M"
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(ts_str, fmt)
                return int(dt.timestamp())
            except:
                continue

        raise ValueError(f"无法解析时间格式: {ts_str}")
