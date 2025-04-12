import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import time
import tempfile
import asyncio
import json
from datetime import datetime, timedelta
import subprocess

# 存储活跃的录音进程
active_recordings = {}

class EventRecorder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_scheduled_events.start()

    def cog_unload(self):
        self.check_scheduled_events.cancel()
        # 停止所有活跃的录音
        for guild_id in list(active_recordings.keys()):
            asyncio.create_task(self.stop_recording(guild_id))

    @tasks.loop(minutes=1)
    async def check_scheduled_events(self):
        """每分钟检查一次是否有即将开始的Discord事件"""
        now = datetime.now()

        for guild in self.bot.guilds:
            # 获取所有计划中的事件
            scheduled_events = await guild.fetch_scheduled_events()

            for event in scheduled_events:
                # 检查事件是否即将开始（1分钟内）
                if event.status == discord.EventStatus.scheduled:
                    time_until_start = event.start_time - now

                    # 如果事件将在1分钟内开始
                    if timedelta(0) <= time_until_start <= timedelta(minutes=1):
                        # 检查事件是否有关联的语音频道
                        if event.channel and isinstance(event.channel, discord.VoiceChannel):
                            # 启动录音进程
                            await self.start_recording(guild.id, event)

                # 检查事件是否即将结束（1分钟内）
                elif event.status == discord.EventStatus.active:
                    # 如果事件有结束时间
                    if event.end_time:
                        time_until_end = event.end_time - now

                        # 如果事件将在1分钟内结束且正在录音
                        if timedelta(0) <= time_until_end <= timedelta(minutes=1) and guild.id in active_recordings:
                            # 停止录音进程
                            await self.stop_recording(guild.id)

    @check_scheduled_events.before_loop
    async def before_check_scheduled_events(self):
        await self.bot.wait_until_ready()

    async def start_recording(self, guild_id, event):
        """开始录音"""
        if guild_id in active_recordings:
            # 已经在录音中
            return

        guild = self.bot.get_guild(guild_id)
        if not guild:
            return

        voice_channel = event.channel
        if not voice_channel or not isinstance(voice_channel, discord.VoiceChannel):
            return

        try:
            # 连接到语音频道
            voice_client = await voice_channel.connect()

            # 创建临时文件
            temp_wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name

            # 启动ffmpeg进程
            ffmpeg_process = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-f", "s16le",
                "-ar", "48000",
                "-ac", "2",
                "-i", "-",
                temp_wav_file,
                stdin=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            # 存储录音信息
            active_recordings[guild_id] = {
                "voice_client": voice_client,
                "ffmpeg_process": ffmpeg_process,
                "temp_file": temp_wav_file,
                "event": event,
                "start_time": datetime.now()
            }

            # 如果有文本频道与事件关联，发送通知
            if event.channel and hasattr(event.channel, 'category') and event.channel.category:
                for channel in event.channel.category.text_channels:
                    try:
                        await channel.send(f"📢 自动录音已开始: **{event.name}**")
                        break
                    except:
                        continue

        except Exception as e:
            print(f"开始录音时出错: {e}")

    async def stop_recording(self, guild_id):
        """停止录音并保存文件"""
        if guild_id not in active_recordings:
            return

        recording_info = active_recordings[guild_id]
        voice_client = recording_info["voice_client"]
        ffmpeg_process = recording_info["ffmpeg_process"]
        temp_file = recording_info["temp_file"]
        event = recording_info["event"]

        try:
            # 关闭ffmpeg进程
            ffmpeg_process.stdin.close()
            await ffmpeg_process.wait()

            # 断开语音连接
            await voice_client.disconnect()

            # 保存会议记录
            json_file_path = await self.save_meeting_record(guild_id, temp_file, event)

            # 如果保存成功，不需要删除临时文件，因为它已经被移动到recordings目录
            if json_file_path:
                temp_file = None

            # 如果临时文件仍然存在，删除它
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

            # 从活跃录音中移除
            del active_recordings[guild_id]

            # 发送通知
            if event.channel and hasattr(event.channel, 'category') and event.channel.category:
                for channel in event.channel.category.text_channels:
                    try:
                        await channel.send(f"✅ 自动录音已完成: **{event.name}**")
                        break
                    except:
                        continue

        except Exception as e:
            print(f"停止录音时出错: {e}")

    async def save_meeting_record(self, guild_id, file_path, event):
        """保存会议记录为JSON文件"""
        try:
            # 获取事件信息
            event_name = event.name
            event_date = event.start_time.strftime("%Y-%m-%d")

            # 尝试从事件描述中获取portfolio_id
            portfolio_id = ""
            if event.description:
                try:
                    # 尝试查找格式为"portfolio_id: XXX"的文本
                    desc_lines = event.description.split('\n')
                    for line in desc_lines:
                        if line.lower().startswith("portfolio_id:"):
                            portfolio_id = line.split(":", 1)[1].strip()
                            break
                except:
                    pass

            # 如果没有找到portfolio_id，使用事件所在的频道类别名称
            if not portfolio_id and event.channel and hasattr(event.channel, 'category') and event.channel.category:
                portfolio_id = event.channel.category.name

            # 如果仍然没有portfolio_id，使用默认值
            if not portfolio_id:
                portfolio_id = "未指定"

            # 生成唯一的会议名称（包含日期）
            meeting_name = f"{event_name}_{event_date}"

            # 创建会议记录JSON对象
            meeting_record = {
                "meeting_date": event_date,
                "meeting_name": meeting_name,
                "portfolio_id": portfolio_id,
                "recording_file_link": file_path  # 本地文件路径
            }

            # 创建recordings目录（如果不存在）
            recordings_dir = os.path.join(os.getcwd(), "recordings")
            os.makedirs(recordings_dir, exist_ok=True)

            # 将会议记录保存为JSON文件
            json_file_path = os.path.join(recordings_dir, f"{meeting_name}.json")
            with open(json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(meeting_record, json_file, ensure_ascii=False, indent=4)

            print(f"会议记录已保存: {json_file_path}")

            # 将录音文件移动到recordings目录
            new_audio_path = os.path.join(recordings_dir, f"{meeting_name}.wav")
            os.rename(file_path, new_audio_path)

            # 更新JSON文件中的录音文件路径
            meeting_record["recording_file_link"] = new_audio_path
            with open(json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(meeting_record, json_file, ensure_ascii=False, indent=4)

            return json_file_path

        except Exception as e:
            print(f"保存会议记录时出错: {e}")
            return None

    @app_commands.command(name="list_events", description="列出服务器中的所有计划事件")
    async def list_events(self, interaction: discord.Interaction):
        """列出服务器中的所有计划事件"""
        await interaction.response.defer(ephemeral=True)

        try:
            guild = interaction.guild
            scheduled_events = await guild.fetch_scheduled_events()

            if not scheduled_events:
                await interaction.followup.send("当前没有计划中的事件。")
                return

            embed = discord.Embed(
                title="📅 计划事件列表",
                description="以下是服务器中的所有计划事件：",
                color=discord.Color.blue()
            )

            for event in scheduled_events:
                status_str = "计划中" if event.status == discord.EventStatus.scheduled else "进行中" if event.status == discord.EventStatus.active else "已完成"
                channel_str = f"在 {event.channel.mention}" if event.channel else "无频道"

                value = (
                    f"**状态:** {status_str}\n"
                    f"**频道:** {channel_str}\n"
                    f"**开始时间:** {event.start_time.strftime('%Y-%m-%d %H:%M')}\n"
                )

                if event.end_time:
                    value += f"**结束时间:** {event.end_time.strftime('%Y-%m-%d %H:%M')}\n"

                embed.add_field(
                    name=event.name,
                    value=value,
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"获取事件列表时出错: {e}")

    @app_commands.command(name="manual_record_event", description="手动开始录制指定的事件")
    @app_commands.describe(event_id="要录制的事件ID")
    async def manual_record_event(self, interaction: discord.Interaction, event_id: str):
        """手动开始录制指定的事件"""
        await interaction.response.defer(ephemeral=True)

        try:
            guild = interaction.guild

            # 获取事件
            event = await guild.fetch_scheduled_event(int(event_id))
            if not event:
                await interaction.followup.send("找不到指定的事件。")
                return

            # 检查事件是否有关联的语音频道
            if not event.channel or not isinstance(event.channel, discord.VoiceChannel):
                await interaction.followup.send("该事件没有关联的语音频道，无法录制。")
                return

            # 检查是否已经在录制
            if guild.id in active_recordings:
                await interaction.followup.send("已经有一个录音进程在运行。")
                return

            # 开始录制
            await self.start_recording(guild.id, event)

            await interaction.followup.send(f"已开始录制事件: **{event.name}**")

        except ValueError:
            await interaction.followup.send("无效的事件ID。")
        except Exception as e:
            await interaction.followup.send(f"开始录制时出错: {e}")

    @app_commands.command(name="stop_recording_event", description="手动停止当前的事件录制")
    async def stop_recording_event(self, interaction: discord.Interaction):
        """手动停止当前的事件录制"""
        await interaction.response.defer(ephemeral=True)

        try:
            guild = interaction.guild

            # 检查是否有录音进程
            if guild.id not in active_recordings:
                await interaction.followup.send("当前没有录音进程在运行。")
                return

            # 获取事件名称
            event_name = active_recordings[guild.id]["event"].name

            # 停止录制
            await self.stop_recording(guild.id)

            await interaction.followup.send(f"已停止录制事件: **{event_name}**")

        except Exception as e:
            await interaction.followup.send(f"停止录制时出错: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(EventRecorder(bot))
