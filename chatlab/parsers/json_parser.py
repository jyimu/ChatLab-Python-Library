
"""
ChatLab JSON 格式解析器
支持标准 JSON 和 Python 字典格式（单引号）
"""

import json
import ast
import re
from pathlib import Path
from typing import Union, Iterator, Optional
from ..models import ChatSession, ChatMessage


class JSONParser:
    """
    ChatLab JSON 格式解析器

    支持格式：
    - 标准 JSON（双引号）
    - Python 字典格式（单引号，WeFlow 导出格式）
    - JSON Lines (.jsonl)
    """

    def __init__(self):
        self.errors = []

    def parse(self, source: Union[str, Path], encoding: str = "utf-8") -> ChatSession:
        """
        解析 ChatLab JSON 数据

        Args:
            source: JSON 字符串或文件路径
            encoding: 文件编码

        Returns:
            ChatSession 对象
        """
        if isinstance(source, (str, Path)) and Path(source).exists():
            text = Path(source).read_text(encoding=encoding)
        else:
            text = source

        text = text.strip()

        # 尝试多种解析方法
        data = None

        # 1. 尝试标准 JSON
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. 尝试 Python 字面量（单引号格式）
        if data is None:
            try:
                data = ast.literal_eval(text)
            except (ValueError, SyntaxError):
                pass

        # 3. 尝试修复常见错误后解析
        if data is None:
            data = self._try_fix_and_parse(text)

        if data is None:
            raise ValueError("无法解析输入格式，请确保是有效的 JSON 或 Python 字典格式")

        return ChatSession.from_dict(data)

    def _try_fix_and_parse(self, text: str) -> Optional[dict]:
        """尝试修复常见格式错误"""
        # 处理尾部逗号
        text = re.sub(r',(\s*[}\]])', r'\1', text)

        # 处理单引号包裹的字符串
        try:
            return ast.literal_eval(text)
        except:
            return None

    def parse_stream(self, source: Union[str, Path], encoding: str = "utf-8") -> Iterator[ChatMessage]:
        """
        流式解析（用于大文件）

        注意：流式解析只返回消息对象，不包含会话元信息
        """
        if isinstance(source, (str, Path)) and Path(source).exists():
            text = Path(source).read_text(encoding=encoding)
        else:
            text = source

        # 查找 messages 数组
        pattern = r'["\']messages["\']\s*:\s*(\[.*?\])\s*["\']?\}'
        match = re.search(pattern, text, re.DOTALL)

        if match:
            try:
                messages_data = ast.literal_eval(match.group(1))
                for msg_data in messages_data:
                    yield ChatMessage.from_dict(msg_data)
            except Exception as e:
                self.errors.append(f"流式解析错误: {e}")

    def parse_jsonl(self, source: Union[str, Path], encoding: str = "utf-8") -> ChatSession:
        """
        解析 JSON Lines 格式（.jsonl）

        JSONL 格式：
        {"_type": "header", "chatlab": {...}, "meta": {...}}
        {"_type": "member", ...}
        {"_type": "message", ...}
        """
        if isinstance(source, (str, Path)) and Path(source).exists():
            text = Path(source).read_text(encoding=encoding)
        else:
            text = source

        lines = text.strip().splitlines()

        header = None
        members = []
        messages = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
                type_ = obj.get("_type")

                if type_ == "header":
                    header = obj
                elif type_ == "member":
                    members.append(obj)
                elif type_ == "message":
                    messages.append(obj)
            except json.JSONDecodeError:
                continue

        if not header:
            raise ValueError("JSONL 文件缺少 header 行")

        # 构建标准格式
        data = {
            "chatlab": header.get("chatlab", {}),
            "meta": header.get("meta", {}),
            "members": members,
            "messages": messages
        }

        return ChatSession.from_dict(data)

    def validate(self, source: Union[str, Path], encoding: str = "utf-8") -> bool:
        """验证格式是否正确"""
        try:
            self.parse(source, encoding)
            return True
        except Exception as e:
            self.errors.append(str(e))
            return False


class AutoParser:
    """
    自动检测格式并解析
    支持：JSON, JSONL, Python dict
    """

    def __init__(self):
        self.parser = JSONParser()

    def parse(self, source: Union[str, Path]) -> ChatSession:
        """自动检测格式并解析"""
        if isinstance(source, (str, Path)) and Path(source).exists():
            path = Path(source)
            suffix = path.suffix.lower()

            if suffix == '.jsonl':
                return self.parser.parse_jsonl(path)
            else:
                return self.parser.parse(path)
        else:
            # 尝试作为字符串解析
            text = source.strip()

            # 检测是否是 JSONL（多行，每行一个 JSON）
            if '\n' in text and '"_type"' in text:
                try:
                    return self.parser.parse_jsonl(text)
                except:
                    pass

            return self.parser.parse(text)
