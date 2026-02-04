# Nexus Skill

这是一个全能的留学生生活助手技能，集成了 Canvas 作业提醒、日历日程管理和邮件摘要功能。从各种渠道获取信息，整合后输出。可以用于生成早报晚报、提醒课程和作业等。

## Configuration

使用前需要配置以下凭证：
1.  **Canvas Token**: 用于访问 Canvas LMS (canvas.vt.edu)。
2.  **Calendar URLs**: 课程表的 .ics 链接。
3.  **Gmail Token**: 用于读取重要邮件。

配置将保存在 `Nexus/config.json` 中。

## Tools

### `nexus_status`
检查当前助手的配置状态，查看缺少哪些 Token 或 Key。
- **Use when**: 初次运行或需要确认服务是否连接正常时。
- **Parameters**: None

### `nexus_config`
设置或更新配置项。
- **Use when**: 用户提供 Token 或 URL 时。
- **Parameters**:
    - `key`: 配置项名称 (canvas_token | gmail_token | calendar_urls)
    - `value`: 配置项的值 (calendar_urls 可以是逗号分隔的字符串)

### `nexus_report`
获取今日/明日的综合早报数据，包括作业 Due、日程安排和重要邮件。
- **Use when**: 用户询问“今天有什么课”、“有什么作业”或请求发送早报时。
- **Parameters**: None
- **Returns**: 包含所有信息的 Markdown 格式文本。

---

## 🧠 Workflows & Guidelines (For Agents)

当处理 `nexus_report` 返回的数据时，请严格遵守以下规则：

### 1. 优先级判断 (Priority Rules)
你必须先对信息进行分级，不要罗列流水账：
- **🔴 红色警报 (Immediate Action)**:
  - 今天 (Today) 23:59 前截止的 Canvas 作业。
  - 已经开始或 1 小时内开始的课程/会议。
  - 来自 "Professor", "Visa", "Offer", "Job" 等关键词的未读邮件。
- **🟡 黄色预警 (Plan Ahead)**:
  - 明天 (Tomorrow) 的早八课程 (08:00 AM classes)。
  - 未来 3 天内截止的作业。
- **🟢 绿色信息 (FYI)**:
  - 7 天后的作业。
  - 普通通知邮件（如 Newsletter）。

### 2. 语气与人设 (Persona)
- **Role**: 你是用户的私人学术管家，既专业又带点幽默感（适当吐槽）。
- **Tone**: 
  - 如果有 Due：**紧迫、严肃** ("🔥 别睡了起来嗨！").
  - 如果无事：**轻松、调侃** ("🎉 恭喜，今天可以躺平了").
- **Language**: 默认使用中文（除非用户用英文提问）。

### 3. 输出模板 (Response Template)
请参考以下 Markdown 格式输出：

```markdown
### 🦞 [日期] 每日早报

**🚨 紧急事项 (Action Required)**
- 🔥 **[作业]** CS 2505 Homework (23:59 截止) - *还剩 X 小时！*
- 📧 **[邮件]** 教授发来了关于 "Midterm" 的邮件，请立即查看。

**📅 今日日程 (Today's Schedule)**
- ✅ 10:10 Math (已结束)
- 🏃 14:30 Gym (准备出发)

**🔮 未来展望 (Looking Ahead)**
- 明早有 8:00 的 STAT 课，建议今晚 23:00 前睡觉。
- 下周三有个大 Project Due。
```

---

## Implementation

```python
!tool_impl
import json
import os
import sys
import subprocess

# Resolve paths
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
CONFIG_UTILS = os.path.join(SCRIPTS_DIR, "config_utils.py")
CHECK_CANVAS = os.path.join(SCRIPTS_DIR, "check_canvas.py")
CHECK_CALENDAR = os.path.join(SCRIPTS_DIR, "check_calendar.py")
CHECK_MAIL = os.path.join(SCRIPTS_DIR, "check_mail.py")

def _load_config():
    try:
        cfg_path = os.path.join(SKILL_DIR, "config.json")
        with open(cfg_path, 'r') as f:
            return json.load(f)
    except:
        return {}

async def nexus_status(params):
    """Check configuration status."""
    result = subprocess.run(
        [sys.executable, CONFIG_UTILS, "status"],
        capture_output=True, text=True, cwd=SCRIPTS_DIR
    )
    return result.stdout

async def nexus_config(params):
    """Update configuration."""
    key = params.get("key")
    value = params.get("value")
    
    result = subprocess.run(
        [sys.executable, CONFIG_UTILS, "set", key, value],
        capture_output=True, text=True, cwd=SCRIPTS_DIR
    )
    return result.stdout

async def nexus_report(params):
    """Generate the full briefing report."""
    config = _load_config()
    report = []
    
    # 1. Canvas
    if config.get("canvas_token"):
        try:
            res = subprocess.run(
                [sys.executable, CHECK_CANVAS], # No args needed, reads config
                capture_output=True, text=True, timeout=15, cwd=SCRIPTS_DIR
            )
            report.append(f"### 📚 Canvas Status\n{res.stdout}")
        except Exception as e:
            report.append(f"### 📚 Canvas Status\nError: {str(e)}")
    else:
        report.append("### 📚 Canvas Status\nNot configured (Missing canvas_token)")

    # 2. Calendar
    try:
        res = subprocess.run(
            [sys.executable, CHECK_CALENDAR],
            capture_output=True, text=True, timeout=15, cwd=SCRIPTS_DIR
        )
        report.append(f"### 📅 Schedule\n{res.stdout}")
    except Exception as e:
        report.append(f"### 📅 Schedule\nError: {str(e)}")

    # 3. Mail
    if config.get("gmail_token"):
        try:
            res = subprocess.run(
                [sys.executable, CHECK_MAIL], # No args needed, reads config
                capture_output=True, text=True, timeout=15, cwd=SCRIPTS_DIR
            )
            report.append(f"### 📧 Inbox\n{res.stdout}")
        except Exception as e:
            report.append(f"### 📧 Inbox\nError: {str(e)}")
    
    return "\n\n".join(report)
```
