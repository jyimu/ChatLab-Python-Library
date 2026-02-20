"""
ChatLab 基础使用示例
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import chatlab


def example_1_basic_loading():
    """示例1: 基础加载"""
    print("=" * 50)
    print("示例1: 基础加载")
    print("=" * 50)

    # 从字符串加载（WeFlow 导出的格式）
    raw_data = """{'chatlab': {'version': '0.0.2', 'exportedAt': 1770985548, 'generator': 'WeFlow'}, 'meta': {'name': 'Qelys', 'platform': 'wechat', 'type': 'private', 'ownerId': 'wxid_gckt3mu9s9dr29_5f43'}, 'members': [{'platformId': 'wxid_gckt3mu9s9dr29', 'accountName': 'Qelys'}], 'messages': [{'sender': 'wxid_gckt3mu9s9dr29', 'accountName': '我', 'timestamp': 1770819410, 'type': 0, 'content': 'hi', 'platformMessageId': '211867332358183300'}, {'sender': 'wxid_gckt3mu9s9dr29', 'accountName': '我', 'timestamp': 1770822000, 'type': 0, 'content': 'hello', 'platformMessageId': '856316427780575200'}]}"""

    session = chatlab.loads(raw_data)

    print(f"会话名称: {session.meta.name}")
    print(f"平台: {session.meta.platform}")
    print(f"消息数: {len(session.messages)}")
    print()


def example_2_querying():
    """示例2: 查询消息"""
    print("=" * 50)
    print("示例2: 查询消息")
    print("=" * 50)

    raw_data = """{'chatlab': {'version': '0.0.2', 'exportedAt': 1770985548, 'generator': 'WeFlow'}, 'meta': {'name': 'Test', 'platform': 'wechat', 'type': 'group', 'ownerId': 'owner1'}, 'members': [{'platformId': 'user1', 'accountName': 'Alice'}, {'platformId': 'user2', 'accountName': 'Bob'}], 'messages': [{'sender': 'user1', 'accountName': 'Alice', 'timestamp': 1770985500, 'type': 0, 'content': '大家好', 'platformMessageId': '1'}, {'sender': 'user2', 'accountName': 'Bob', 'timestamp': 1770985560, 'type': 0, 'content': '你好 Alice', 'platformMessageId': '2'}, {'sender': 'user1', 'accountName': 'Alice', 'timestamp': 1770985620, 'type': 0, 'content': '今天天气不错', 'platformMessageId': '3'}]}"""

    session = chatlab.loads(raw_data)

    # 按发送者查询
    alice_msgs = session.get_messages_by_sender('user1')
    print(f"Alice 的消息: {len(alice_msgs)} 条")

    # 关键词搜索
    weather_msgs = session.get_messages_by_keyword('天气')
    print(f"包含'天气'的消息: {len(weather_msgs)} 条")
    if weather_msgs:
        print(f"  内容: {weather_msgs[0].content}")

    # 获取统计
    stats = session.get_statistics()
    print(f"\n统计信息:")
    print(f"  总消息: {stats['total_messages']}")
    print(f"  发送者: {stats['unique_senders']}")
    print()


def example_3_exporting():
    """示例3: 导出数据"""
    print("=" * 50)
    print("示例3: 导出数据")
    print("=" * 50)

    raw_data = """{'chatlab': {'version': '0.0.2', 'exportedAt': 1770985548, 'generator': 'WeFlow'}, 'meta': {'name': 'ExportTest', 'platform': 'wechat', 'type': 'private', 'ownerId': 'user1'}, 'members': [{'platformId': 'user1', 'accountName': 'Me'}], 'messages': [{'sender': 'user1', 'accountName': 'Me', 'timestamp': 1770985500, 'type': 0, 'content': 'Test', 'platformMessageId': '1'}]}"""

    session = chatlab.loads(raw_data)

    # 导出为 JSON 字符串
    json_str = chatlab.saves(session, format='json', indent=2)
    print(f"JSON 长度: {len(json_str)} 字符")
    print(f"前200字符:\n{json_str[:200]}...")
    print()


def example_4_analysis():
    """示例4: 数据分析"""
    print("=" * 50)
    print("示例4: 数据分析")
    print("=" * 50)

    # 创建示例数据
    session = chatlab.loads("""{'chatlab': {'version': '0.0.2', 'exportedAt': 1770985548, 'generator': 'WeFlow'}, 'meta': {'name': 'Analysis', 'platform': 'wechat', 'type': 'group', 'ownerId': 'owner'}, 'members': [{'platformId': 'u1', 'accountName': 'User1'}, {'platformId': 'u2', 'accountName': 'User2'}], 'messages': [{'sender': 'u1', 'accountName': 'User1', 'timestamp': 1770985500, 'type': 0, 'content': 'Message 1', 'platformMessageId': '1'}, {'sender': 'u2', 'accountName': 'User2', 'timestamp': 1770985560, 'type': 0, 'content': 'Message 2', 'platformMessageId': '2'}, {'sender': 'u1', 'accountName': 'User1', 'timestamp': 1770985620, 'type': 0, 'content': 'Message 3', 'platformMessageId': '3'}]}""")

    # 获取发送者统计
    sender_stats = session.get_sender_stats()
    print("发送者统计:")
    for sender_id, info in sender_stats.items():
        print(f"  {info['account_name']}: {info['count']} 条消息")

    # 获取时间线
    timeline = session.get_timeline()
    print(f"\n每日消息数:")
    for date, count in timeline.items():
        print(f"  {date}: {count} 条")
    print()


if __name__ == "__main__":
    example_1_basic_loading()
    example_2_querying()
    example_3_exporting()
    example_4_analysis()

    print("=" * 50)
    print("所有示例运行完成！")
    print("=" * 50)
