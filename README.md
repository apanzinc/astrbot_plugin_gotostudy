# 去学习！ (GotoStudy)

[![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-blue)](https://github.com/Soulter/AstrBot)
[![License](https://img.shields.io/badge/license-AGPL--v3-green)](LICENSE)

一个 AstrBot 插件，当指定 QQ 用户发送消息时，自动提醒他们去学习！

## 功能

- 监控指定 QQ 号，自动回复学习提醒
- 支持群白名单设置
- 可自定义回复内容
- 冷却时间防刷屏（默认 5 分钟）

## 安装

在 AstrBot 插件市场搜索 "去学习" 安装，或通过 GitHub 仓库安装。

## 命令

```
/gotostudy add <QQ>        # 添加目标用户
/gotostudy remove <QQ>     # 移除目标用户
/gotostudy addgroup <群号> # 添加群白名单
/gotostudy setmsg <消息>   # 设置回复内容
/gotostudy setcd <秒>      # 设置冷却时间
/gotostudy list            # 查看配置
/gotostudy on/off          # 启用/禁用
/gotostudy help            # 显示帮助
```

**注意：所有命令仅管理员可用**

## 许可证

[AGPL-3.0](LICENSE)
