import unittest
import asyncio
import os
import sys
import json
import shutil
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import discord
from discord.ext import commands
from cogs.event_recorder import EventRecorder

# 模拟Discord事件对象
class MockEvent:
    def __init__(self, name, start_time, end_time=None, channel=None, description=""):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.channel = channel
        self.description = description
        self.status = discord.EventStatus.scheduled

# 模拟Discord语音频道对象
class MockVoiceChannel:
    def __init__(self, name, category=None):
        self.name = name
        self.category = category

    async def connect(self):
        # 返回模拟的语音客户端
        return MockVoiceClient()

# 模拟Discord语音客户端对象
class MockVoiceClient:
    async def disconnect(self):
        pass

# 模拟Discord频道分类对象
class MockCategory:
    def __init__(self, name, text_channels=None):
        self.name = name
        self.text_channels = text_channels or []

# 模拟Discord文本频道对象
class MockTextChannel:
    def __init__(self, name):
        self.name = name

    async def send(self, content):
        print(f"发送到频道 {self.name}: {content}")

# 模拟Discord Guild对象
class MockGuild:
    def __init__(self, id, name, voice_channels=None, text_channels=None, categories=None):
        self.id = id
        self.name = name
        self.voice_channels = voice_channels or []
        self.text_channels = text_channels or []
        self.categories = categories or []

    async def fetch_scheduled_events(self):
        # 返回模拟的计划事件列表
        now = datetime.now()

        # 创建一个即将开始的事件
        upcoming_event = MockEvent(
            name="测试会议",
            start_time=now + timedelta(seconds=30),
            end_time=now + timedelta(minutes=30),
            channel=self.voice_channels[0] if self.voice_channels else None,
            description="测试会议描述\nportfolio_id: TEST-123"
        )

        # 创建一个正在进行的事件
        active_event = MockEvent(
            name="进行中的会议",
            start_time=now - timedelta(minutes=10),
            end_time=now + timedelta(seconds=30),
            channel=self.voice_channels[1] if len(self.voice_channels) > 1 else None
        )
        active_event.status = discord.EventStatus.active

        return [upcoming_event, active_event]

    async def fetch_scheduled_event(self, event_id):
        # 返回模拟的单个事件
        now = datetime.now()
        return MockEvent(
            name=f"事件 {event_id}",
            start_time=now,
            end_time=now + timedelta(minutes=30),
            channel=self.voice_channels[0] if self.voice_channels else None
        )

# 模拟Discord Bot对象
class MockBot:
    def __init__(self, guilds=None):
        self.guilds = guilds or []

    async def wait_until_ready(self):
        pass

    def get_guild(self, guild_id):
        for guild in self.guilds:
            if guild.id == guild_id:
                return guild
        return None

class TestEventRecorder(unittest.TestCase):
    def setUp(self):
        # 创建模拟的Discord环境
        text_channel = MockTextChannel("general")
        category = MockCategory("测试分类", [text_channel])
        voice_channel1 = MockVoiceChannel("会议室1", category)
        voice_channel2 = MockVoiceChannel("会议室2", category)

        self.guild = MockGuild(
            id=123456789,
            name="测试服务器",
            voice_channels=[voice_channel1, voice_channel2],
            text_channels=[text_channel],
            categories=[category]
        )

        self.bot = MockBot([self.guild])
        self.event_recorder = EventRecorder(self.bot)

    def test_event_recorder_initialization(self):
        self.assertIsNotNone(self.event_recorder)
        self.assertEqual(self.event_recorder.bot, self.bot)

    async def test_check_scheduled_events(self):
        # 测试检查计划事件的功能
        await self.event_recorder.check_scheduled_events()
        # 由于这是一个异步任务，我们只能验证它不会抛出异常

    async def test_start_and_stop_recording(self):
        # 创建模拟事件
        now = datetime.now()
        event = MockEvent(
            name="测试录音",
            start_time=now,
            end_time=now + timedelta(minutes=1),
            channel=self.guild.voice_channels[0]
        )

        # 测试开始录音
        await self.event_recorder.start_recording(self.guild.id, event)

        # 等待一小段时间
        await asyncio.sleep(2)

        # 测试停止录音
        await self.event_recorder.stop_recording(self.guild.id)

def run_tests():
    unittest.main()

if __name__ == "__main__":
    # 创建事件循环并运行测试
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.gather(
            TestEventRecorder().test_check_scheduled_events(),
            TestEventRecorder().test_start_and_stop_recording()
        ))
    finally:
        loop.close()

    print("所有测试完成")
