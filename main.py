import json
import os
from typing import List, Dict, Any

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import logger


class GotoStudy(Star):
    """去学习插件 - 当指定用户发送消息时自动提醒去学习"""

    def __init__(self, context: Context, config: Dict[str, Any] = None):
        super().__init__(context)
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")

        # 优先使用 AstrBot 传入的配置，否则使用本地配置
        if config:
            self.config = dict(config)  # AstrBotConfig 继承自 Dict
        else:
            self.config = self._load_local_config()

    def _get_config(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)

    def _set_config(self, key: str, value):
        """设置配置值，同时更新内存配置和本地配置"""
        # 更新内存配置
        self.config[key] = value

        # 保存到本地配置文件（作为备份）
        self._save_local_config()

        # 尝试保存到 AstrBot 配置系统
        try:
            if hasattr(self, 'config') and hasattr(self.config, 'save_config'):
                self.config.save_config()
        except Exception as e:
            logger.debug(f"[GotoStudy] 保存 AstrBot 配置失败: {e}")

    def _load_local_config(self) -> dict:
        """从本地配置文件加载"""
        default_config = {
            "target_qqs": [],
            "group_whitelist": [],
            "reply_message": "去学习！",
            "enabled": True
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"[GotoStudy] 加载本地配置失败: {e}")
                return default_config
        else:
            self._save_local_config(default_config)
            return default_config

    def _save_local_config(self, config: dict = None):
        """保存到本地配置文件"""
        if config is None:
            config = self.config
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[GotoStudy] 保存本地配置失败: {e}")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AstrMessageEvent):
        """监听所有消息事件"""
        if not self._get_config("enabled", True):
            return

        # 获取发送者QQ号
        sender_id = event.get_sender_id()
        if not sender_id:
            return

        # 检查发送者是否在目标列表中
        target_qqs = self._get_config("target_qqs", [])
        if sender_id not in target_qqs:
            return

        # 获取群号（如果有）
        message_obj = event.message_obj
        group_id = getattr(message_obj, "group_id", "")

        # 检查群白名单
        group_whitelist = self._get_config("group_whitelist", [])
        if group_whitelist:
            # 白名单不为空，只在指定群中生效
            if not group_id or group_id not in group_whitelist:
                return

        # 发送回复
        reply_msg = self._get_config("reply_message", "去学习！")
        yield event.plain_result(reply_msg)

    @filter.command_group("gotostudy")
    def gotostudy(self):
        """去学习插件管理命令"""
        pass

    @gotostudy.command("add")
    async def add_target(self, event: AstrMessageEvent, qq: str):
        """添加目标QQ号
        用法: /gotostudy add 114514
        """
        try:
            qq_number = str(qq).strip()
            if not qq_number.isdigit():
                yield event.plain_result("❌ QQ号必须是数字！")
                return

            target_qqs = self._get_config("target_qqs", [])
            if qq_number in target_qqs:
                yield event.plain_result(f"⚠️ QQ {qq_number} 已经在列表中了！")
                return

            target_qqs.append(qq_number)
            self._set_config("target_qqs", target_qqs)

            yield event.plain_result(f"✅ 已添加 QQ {qq_number} 到目标列表！")
        except Exception as e:
            logger.error(f"[GotoStudy] 添加目标失败: {e}")
            yield event.plain_result(f"❌ 添加失败: {str(e)}")

    @gotostudy.command("remove")
    async def remove_target(self, event: AstrMessageEvent, qq: str):
        """移除目标QQ号
        用法: /gotostudy remove 114514
        """
        try:
            qq_number = str(qq).strip()

            target_qqs = self._get_config("target_qqs", [])
            if qq_number not in target_qqs:
                yield event.plain_result(f"⚠️ QQ {qq_number} 不在列表中！")
                return

            target_qqs.remove(qq_number)
            self._set_config("target_qqs", target_qqs)

            yield event.plain_result(f"✅ 已移除 QQ {qq_number}！")
        except Exception as e:
            logger.error(f"[GotoStudy] 移除目标失败: {e}")
            yield event.plain_result(f"❌ 移除失败: {str(e)}")

    @gotostudy.command("list")
    async def list_targets(self, event: AstrMessageEvent):
        """列出所有目标QQ号
        用法: /gotostudy list
        """
        target_qqs = self._get_config("target_qqs", [])
        group_whitelist = self._get_config("group_whitelist", [])
        reply_msg = self._get_config("reply_message", "去学习！")
        enabled = self._get_config("enabled", True)

        if not target_qqs:
            msg = "📋 目标QQ列表: 空\n"
        else:
            msg = f"📋 目标QQ列表 ({len(target_qqs)}个):\n"
            for i, qq in enumerate(target_qqs, 1):
                msg += f"  {i}. {qq}\n"

        if not group_whitelist:
            msg += "\n👥 群白名单: 空（所有群生效）\n"
        else:
            msg += f"\n👥 群白名单 ({len(group_whitelist)}个):\n"
            for i, group in enumerate(group_whitelist, 1):
                msg += f"  {i}. {group}\n"

        msg += f"\n💬 回复内容: {reply_msg}"
        msg += f"\n🔘 插件状态: {'启用' if enabled else '禁用'}"

        yield event.plain_result(msg)

    @gotostudy.command("setmsg")
    async def set_message(self, event: AstrMessageEvent, *, message: str):
        """设置回复消息内容
        用法: /gotostudy setmsg 滚去学习！
        """
        try:
            if not message or not message.strip():
                yield event.plain_result("❌ 回复消息不能为空！")
                return

            self._set_config("reply_message", message.strip())

            yield event.plain_result(f"✅ 回复消息已设置为: {message.strip()}")
        except Exception as e:
            logger.error(f"[GotoStudy] 设置消息失败: {e}")
            yield event.plain_result(f"❌ 设置失败: {str(e)}")

    @gotostudy.command("on")
    async def enable_plugin(self, event: AstrMessageEvent):
        """启用插件
        用法: /gotostudy on
        """
        self._set_config("enabled", True)
        yield event.plain_result("✅ 插件已启用！")

    @gotostudy.command("off")
    async def disable_plugin(self, event: AstrMessageEvent):
        """禁用插件
        用法: /gotostudy off
        """
        self._set_config("enabled", False)
        yield event.plain_result("✅ 插件已禁用！")

    @gotostudy.command("addgroup")
    async def add_group(self, event: AstrMessageEvent, group_id: str):
        """添加群白名单
        用法: /gotostudy addgroup 123456789
        """
        try:
            group_id = str(group_id).strip()
            if not group_id.isdigit():
                yield event.plain_result("❌ 群号必须是数字！")
                return

            group_whitelist = self._get_config("group_whitelist", [])
            if group_id in group_whitelist:
                yield event.plain_result(f"⚠️ 群 {group_id} 已经在白名单中了！")
                return

            group_whitelist.append(group_id)
            self._set_config("group_whitelist", group_whitelist)

            yield event.plain_result(f"✅ 已添加群 {group_id} 到白名单！")
        except Exception as e:
            logger.error(f"[GotoStudy] 添加群白名单失败: {e}")
            yield event.plain_result(f"❌ 添加失败: {str(e)}")

    @gotostudy.command("removegroup")
    async def remove_group(self, event: AstrMessageEvent, group_id: str):
        """移除群白名单
        用法: /gotostudy removegroup 123456789
        """
        try:
            group_id = str(group_id).strip()

            group_whitelist = self._get_config("group_whitelist", [])
            if group_id not in group_whitelist:
                yield event.plain_result(f"⚠️ 群 {group_id} 不在白名单中！")
                return

            group_whitelist.remove(group_id)
            self._set_config("group_whitelist", group_whitelist)

            yield event.plain_result(f"✅ 已移除群 {group_id}！")
        except Exception as e:
            logger.error(f"[GotoStudy] 移除群白名单失败: {e}")
            yield event.plain_result(f"❌ 移除失败: {str(e)}")

    @gotostudy.command("clear")
    async def clear_groups(self, event: AstrMessageEvent):
        """清空群白名单（在所有群生效）
        用法: /gotostudy clear
        """
        try:
            self._set_config("group_whitelist", [])
            yield event.plain_result("✅ 已清空群白名单，插件将在所有群生效！")
        except Exception as e:
            logger.error(f"[GotoStudy] 清空群白名单失败: {e}")
            yield event.plain_result(f"❌ 清空失败: {str(e)}")

    @gotostudy.command("help")
    async def show_help(self, event: AstrMessageEvent):
        """显示帮助信息
        用法: /gotostudy help
        """
        help_text = """📖 GotoStudy 插件使用帮助

【目标用户管理】
  /gotostudy add <QQ号>       - 添加目标QQ号
  /gotostudy remove <QQ号>    - 移除目标QQ号

【群白名单管理】
  /gotostudy addgroup <群号>  - 添加群白名单
  /gotostudy removegroup <群号> - 移除群白名单
  /gotostudy clear            - 清空群白名单（在所有群生效）
  💡 说明: 白名单为空时，插件在所有群生效；有值时只在指定群生效

【其他命令】
  /gotostudy list             - 查看配置列表
  /gotostudy setmsg <消息>    - 设置回复消息内容
  /gotostudy on               - 启用插件
  /gotostudy off              - 禁用插件
  /gotostudy help             - 显示此帮助

【配置方式】
  1. WebUI: 插件设置页面可视化配置
  2. 命令: 使用上述命令在聊天中配置

【示例】
  /gotostudy add 114514
  /gotostudy addgroup 123456789
  /gotostudy setmsg 滚去学习！
"""
        yield event.plain_result(help_text)
