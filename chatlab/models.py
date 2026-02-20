"""
ChatLab Standard Format - 核心数据模型
符合 ChatLab Standard Format Specification v0.0.1
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import IntEnum
from pathlib import Path
import json


class MessageType(IntEnum):
    """消息类型枚举"""
    TEXT = 0
    IMAGE = 1
    VOICE = 2
    VIDEO = 3
    FILE = 4
    LOCATION = 5
    LINK = 6
    STICKER = 7
    SYSTEM = 8
    REVOKED = 9

    @classmethod
    def from_int(cls, value: int) -> "MessageType":
        try:
            return cls(value)
        except ValueError:
            return cls.TEXT

    def to_string(self) -> str:
        names = {
            0: "text", 1: "image", 2: "voice", 3: "video",
            4: "file", 5: "location", 6: "link", 7: "sticker",
            8: "system", 9: "revoked"
        }
        return names.get(self.value, "unknown")


@dataclass
class ChatLabVersion:
    """ChatLab 版本信息"""
    version: str
    exported_at: int
    generator: str

    @property
    def exported_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.exported_at)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "exportedAt": self.exported_at,
            "generator": self.generator
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatLabVersion":
        return cls(
            version=data.get("version", "0.0.1"),
            exported_at=data.get("exportedAt", 0),
            generator=data.get("generator", "unknown")
        )


@dataclass
class ChatMeta:
    """聊天元信息"""
    name: str
    platform: str
    type: str
    owner_id: str
    avatar: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "platform": self.platform,
            "type": self.type,
            "ownerId": self.owner_id
        }
        if self.avatar:
            result["avatar"] = self.avatar
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMeta":
        return cls(
            name=data.get("name", "Unknown"),
            platform=data.get("platform", "unknown"),
            type=data.get("type", "private"),
            owner_id=data.get("ownerId", ""),
            avatar=data.get("avatar"),
            description=data.get("description")
        )


@dataclass
class ChatMember:
    """聊天成员"""
    platform_id: str
    account_name: str
    role: Optional[str] = None
    avatar: Optional[str] = None
    remark: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "platformId": self.platform_id,
            "accountName": self.account_name
        }
        if self.role:
            result["role"] = self.role
        if self.avatar:
            result["avatar"] = self.avatar
        if self.remark:
            result["remark"] = self.remark
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMember":
        return cls(
            platform_id=data.get("platformId", ""),
            account_name=data.get("accountName", ""),
            role=data.get("role"),
            avatar=data.get("avatar"),
            remark=data.get("remark")
        )


@dataclass
class ChatMessage:
    """单条聊天消息"""
    sender: str
    account_name: str
    timestamp: int
    type: int
    content: str
    platform_message_id: str
    reply_to: Optional[str] = None

    # 内部字段
    _datetime: Optional[datetime] = field(default=None, repr=False)

    def __post_init__(self):
        if self._datetime is None:
            self._datetime = datetime.fromtimestamp(self.timestamp)

    @property
    def datetime(self) -> datetime:
        return self._datetime

    @property
    def datetime_str(self, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        return self._datetime.strftime(fmt)

    @property
    def message_type(self) -> MessageType:
        return MessageType.from_int(self.type)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "sender": self.sender,
            "accountName": self.account_name,
            "timestamp": self.timestamp,
            "type": self.type,
            "content": self.content,
            "platformMessageId": self.platform_message_id
        }
        if self.reply_to:
            result["replyTo"] = self.reply_to
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        return cls(
            sender=data.get("sender", ""),
            account_name=data.get("accountName", ""),
            timestamp=data.get("timestamp", 0),
            type=data.get("type", 0),
            content=data.get("content", ""),
            platform_message_id=data.get("platformMessageId", ""),
            reply_to=data.get("replyTo")
        )

    def __repr__(self) -> str:
        content = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"ChatMessage({self.account_name} @ {self.datetime_str}: {content})"


@dataclass
class ChatSession:
    """完整聊天会话"""
    chatlab: ChatLabVersion
    meta: ChatMeta
    members: List[ChatMember]
    messages: List[ChatMessage]

    def __post_init__(self):
        # 确保消息按时间排序
        self.messages.sort(key=lambda x: x.timestamp)

    def __repr__(self) -> str:
        return f"ChatSession('{self.meta.name}', {len(self.messages)} messages, {len(self.members)} members)"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chatlab": self.chatlab.to_dict(),
            "meta": self.meta.to_dict(),
            "members": [m.to_dict() for m in self.members],
            "messages": [m.to_dict() for m in self.messages]
        }

    def to_json(self, indent: Optional[int] = 2, ensure_ascii: bool = False) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)

    def save(self, filepath: Union[str, Path], indent: int = 2, encoding: str = "utf-8"):
        """保存为 ChatLab 标准格式 JSON 文件"""
        Path(filepath).write_text(self.to_json(indent=indent), encoding=encoding)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        return cls(
            chatlab=ChatLabVersion.from_dict(data.get("chatlab", {})),
            meta=ChatMeta.from_dict(data.get("meta", {})),
            members=[ChatMember.from_dict(m) for m in data.get("members", [])],
            messages=[ChatMessage.from_dict(m) for m in data.get("messages", [])]
        )

    # ========== 查询方法 ==========

    def get_messages_by_sender(self, sender_id: str) -> List[ChatMessage]:
        """按发送者ID筛选"""
        return [m for m in self.messages if m.sender == sender_id]

    def get_messages_by_name(self, name: str) -> List[ChatMessage]:
        """按显示名称筛选"""
        return [m for m in self.messages if m.account_name == name]

    def get_messages_by_date(self, date_str: str) -> List[ChatMessage]:
        """按日期筛选 (YYYY-MM-DD)"""
        return [m for m in self.messages if m.datetime_str.startswith(date_str)]

    def get_messages_by_type(self, msg_type: Union[int, MessageType]) -> List[ChatMessage]:
        """按消息类型筛选"""
        type_val = msg_type.value if isinstance(msg_type, MessageType) else msg_type
        return [m for m in self.messages if m.type == type_val]

    def get_messages_by_keyword(self, keyword: str, case_sensitive: bool = False) -> List[ChatMessage]:
        """按关键词搜索内容"""
        if not case_sensitive:
            keyword = keyword.lower()
            return [m for m in self.messages if keyword in m.content.lower()]
        return [m for m in self.messages if keyword in m.content]

    def get_message_by_id(self, msg_id: str) -> Optional[ChatMessage]:
        """通过平台消息ID查找"""
        for m in self.messages:
            if m.platform_message_id == msg_id:
                return m
        return None

    def get_timeline(self) -> Dict[str, int]:
        """获取每日消息数量时间线"""
        timeline = {}
        for m in self.messages:
            date = m.datetime_str[:10]  # YYYY-MM-DD
            timeline[date] = timeline.get(date, 0) + 1
        return dict(sorted(timeline.items()))

    def get_sender_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取发送者统计"""
        stats = {}
        for m in self.messages:
            key = m.sender
            if key not in stats:
                stats[key] = {
                    "account_name": m.account_name,
                    "count": 0,
                    "first_message": m.datetime_str,
                    "last_message": m.datetime_str
                }
            stats[key]["count"] += 1
            stats[key]["last_message"] = m.datetime_str
        return stats

    def get_statistics(self) -> Dict[str, Any]:
        """获取完整统计信息"""
        if not self.messages:
            return {
                "total_messages": 0,
                "unique_senders": 0,
                "date_range": None,
                "message_types": {},
                "timeline": {}
            }

        type_counts = {}
        for m in self.messages:
            type_name = m.message_type.to_string()
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            "total_messages": len(self.messages),
            "unique_senders": len(set(m.sender for m in self.messages)),
            "date_range": {
                "start": self.messages[0].datetime_str,
                "end": self.messages[-1].datetime_str
            },
            "message_types": type_counts,
            "timeline": self.get_timeline(),
            "sender_stats": self.get_sender_stats()
        }

    def get_conversation_threads(self, max_gap_minutes: int = 30) -> List[List[ChatMessage]]:
        """
        将消息分割为对话线程（按时间间隔）

        Args:
            max_gap_minutes: 最大间隔时间（分钟），超过则视为新对话
        """
        if not self.messages:
            return []

        threads = []
        current_thread = [self.messages[0]]

        for i in range(1, len(self.messages)):
            prev_msg = self.messages[i-1]
            curr_msg = self.messages[i]

            gap = (curr_msg.timestamp - prev_msg.timestamp) / 60

            if gap > max_gap_minutes:
                threads.append(current_thread)
                current_thread = [curr_msg]
            else:
                current_thread.append(curr_msg)

        if current_thread:
            threads.append(current_thread)

        return threads
