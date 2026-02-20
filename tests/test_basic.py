"""
ChatLab 基础测试
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import chatlab
from chatlab.models import ChatSession, ChatMessage, ChatMember, ChatMeta, ChatLabVersion


def test_basic_parsing():
    """测试基础解析功能"""
    raw_data = """{'chatlab': {'version': '0.0.2', 'exportedAt': 1770985548, 'generator': 'WeFlow'}, 'meta': {'name': 'TestChat', 'platform': 'wechat', 'type': 'private', 'ownerId': 'test_id'}, 'members': [{'platformId': 'user1', 'accountName': 'User1'}], 'messages': [{'sender': 'user1', 'accountName': 'User1', 'timestamp': 1770985500, 'type': 0, 'content': 'Hello', 'platformMessageId': 'msg_1'}]}"""

    session = chatlab.loads(raw_data)

    assert session.meta.name == "TestChat"
    assert len(session.messages) == 1
    assert session.messages[0].content == "Hello"
    print("✅ 基础解析测试通过")


def test_session_methods():
    """测试会话方法"""
    raw_data = """{'chatlab': {'version': '0.0.2', 'exportedAt': 1770985548, 'generator': 'WeFlow'}, 'meta': {'name': 'TestChat', 'platform': 'wechat', 'type': 'private', 'ownerId': 'test_id'}, 'members': [{'platformId': 'user1', 'accountName': 'Alice'}, {'platformId': 'user2', 'accountName': 'Bob'}], 'messages': [{'sender': 'user1', 'accountName': 'Alice', 'timestamp': 1770985500, 'type': 0, 'content': 'Hi Bob', 'platformMessageId': 'msg_1'}, {'sender': 'user2', 'accountName': 'Bob', 'timestamp': 1770985560, 'type': 0, 'content': 'Hi Alice', 'platformMessageId': 'msg_2'}]}"""

    session = chatlab.loads(raw_data)

    # 测试筛选方法
    alice_msgs = session.get_messages_by_sender('user1')
    assert len(alice_msgs) == 1
    assert alice_msgs[0].account_name == 'Alice'

    # 测试关键词搜索
    hi_msgs = session.get_messages_by_keyword('Hi')
    assert len(hi_msgs) == 2

    # 测试统计
    stats = session.get_statistics()
    assert stats['total_messages'] == 2
    assert stats['unique_senders'] == 2

    print("✅ 会话方法测试通过")


def test_export_import():
    """测试导出导入循环"""
    import tempfile
    import os

    raw_data = """{'chatlab': {'version': '0.0.2', 'exportedAt': 1770985548, 'generator': 'WeFlow'}, 'meta': {'name': 'TestChat', 'platform': 'wechat', 'type': 'private', 'ownerId': 'test_id'}, 'members': [{'platformId': 'user1', 'accountName': 'User1'}], 'messages': [{'sender': 'user1', 'accountName': 'User1', 'timestamp': 1770985500, 'type': 0, 'content': 'Test message', 'platformMessageId': 'msg_1'}]}"""

    session = chatlab.loads(raw_data)

    # 测试 JSON 导出导入
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        temp_path = f.name

    try:
        chatlab.save(session, temp_path, format='json')
        loaded = chatlab.load(temp_path, format='json')

        assert loaded.meta.name == session.meta.name
        assert len(loaded.messages) == len(session.messages)
        assert loaded.messages[0].content == session.messages[0].content

        print("✅ 导出导入测试通过")
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    test_basic_parsing()
    test_session_methods()
    test_export_import()
    print("\n🎉 所有测试通过！")
