# 🎓 OpenClaw Student Assistant (Nexus)

> **Your AI-powered academic butler. Never miss a deadline again.**
> **你的 AI 学术管家，从此告别 "Due Date" 焦虑。**

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-purple)](https://github.com/openclaw/openclaw)
[![Universal Agent Compatible](https://img.shields.io/badge/Compatible-OpenCode%20|%20ClaudeCode-blue)](https://github.com/openclaw/openclaw)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## 🇺🇸 English

> **Universal Agent Skill**: Designed for **OpenClaw**, but 100% compatible with **OpenCode**, **Claude Code**, or any local agent runtime that supports Python tool execution.

### Why?
As a CS student (at VT 🦃), I was tired of checking **Canvas, Gmail, and Google Calendar** separately every single morning. I missed assignments, forgot about club meetings, and let important internship emails get buried in spam.

So I built this **OpenClaw Skill**. It acts as a backend service for your AI agent, giving it real-time access to your academic life. It doesn't just "show" data; it **understands** your schedule.

### ✨ Features
*   **📚 Canvas Integration**:
    *   Directly talks to Canvas API (no slow scraping).
    *   Uses **Concurrent Fetching** to scan all your courses in seconds.
    *   Alerts you on assignments due in the next 7 days.
*   **📅 Smart Calendar**:
    *   Robust `.ics` parsing (supports Weekly/Daily recurrence & Exclusion dates).
    *   **Auto-Timezone**: Automatically detects your local system time (no more hardcoded UTC offsets!).
    *   Merges multiple calendar sources (Course schedule + Personal life).
*   **📧 Inbox Zero Assistant**:
    *   Connects via IMAP to summarize recent emails.
    *   Perfect for catching "Waitlist Notifications" or "Internship Interview Invites" that usually get lost.
*   **🔒 Privacy First**:
    *   All tokens and data live **locally** in `config.json`.
    *   No third-party servers. You own your data.

### 🚀 Quick Start

#### 1. Installation
Clone this repository into your OpenClaw skills directory (or workspace):
```bash
git clone https://github.com/YOUR_USERNAME/Nexus.git Nexus
```

#### 2. Configuration
You can configure it interactively by talking to OpenClaw:
> **You**: "Configure student assistant."
> **AI**: "Sure, I need your Canvas Token..."

Or manually create a `config.json` in the skill folder:
```json
{
  "canvas_token": "YOUR_CANVAS_API_TOKEN",
  "gmail_user": "your.email@gmail.com",
  "gmail_token": "YOUR_APP_PASSWORD",
  "calendar_urls": [
    "https://canvas.vt.edu/feeds/calendars/user_....ics",
    "https://calendar.google.com/calendar/ical/.../basic.ics"
  ]
}
```

#### 3. Usage
Just ask your agent:
*   *"What assignments are due this week?"*
*   *"Generate my daily briefing."*
*   *"Do I have any classes tomorrow morning?"*

---

<a name="chinese"></a>
## 🇨🇳 中文介绍

> **通用 Agent 技能**: 本项目专为 **OpenClaw** 设计，但同样完美兼容 **OpenCode**, **Claude Code**, 以及任何支持运行 Python 工具的桌面端 AI Agent。

### 初衷
作为一名留学生（坐标 VT 🦃），我受够了每天早上要在 Canvas、Gmail 和 Google Calendar 之间来回切换。不仅效率低，还容易因为漏看消息而错过作业 Due 或者重要的面试邮件。

于是我开发了这个 **OpenClaw 技能插件**。它不仅是一个简单的爬虫，更是你的 **AI 学术管家**。它能把分散在各个平台的信息汇总成一份 **“每日早报”**，直接喂给 AI，让 AI 告诉你今天该干嘛。

### ✨ 核心功能
*   **📚 Canvas 作业同步**:
    *   直连 Canvas API（非网页抓取，稳定快速）。
    *   **并发查询**: 秒级扫描所有课程，不仅看 Assignment，还看即将到来的 Quiz。
    *   智能过滤：只提醒未来 7 天内未完成的任务。
*   **📅 智能课表**:
    *   强大的 `.ics` 解析引擎：支持复杂的循环课程（Daily/Weekly）和放假跳过（ExDate）。
    *   **自动时区**: 自动识别你当前的系统时区，回国/返校无需手动改代码。
*   **📧 邮件摘要**:
    *   通过 IMAP 读取最新邮件。
    *   过滤垃圾信息，高亮显示诸如“租房提醒”、“面试通知”、“教授回复”等关键内容。
*   **🔒 隐私安全**:
    *   所有 Token 仅保存在本地 `config.json`。
    *   代码开源，无后门，不上传数据。

### 🚀 快速开始

#### 1. 安装
将此仓库克隆到你的 OpenClaw skills 目录：
```bash
git clone https://github.com/YOUR_USERNAME/Nexus.git Nexus
```

#### 2. 配置
你可以直接跟 OpenClaw 对话进行配置，或者手动创建 `config.json` 文件：
```json
{
  "canvas_token": "你的_CANVAS_TOKEN",
  "gmail_user": "你的邮箱@gmail.com",
  "gmail_token": "你的应用专用密码(App Password)",
  "calendar_urls": [
    "你的课程表.ics链接",
    "你的个人日历.ics链接"
  ]
}
```

#### 3. 使用
直接问你的 AI Agent：
*   *“今天有什么课？”*
*   *“生成今日早报。”*
*   *“这周有几个 Due？”*

---

## 🛠️ Tech Stack (技术栈)
*   **Python 3.9+**
*   **Requests & ThreadPoolExecutor** (High-performance API fetching)
*   **OpenClaw Agent Framework**

## 📄 License
MIT License
