# 历史上的今天 - Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)](https://github.com/lambilly/hass_tian_history)

通过**天聚数行 API** 获取“历史上的今天”数据，提供历史事件查询和自动滚动显示功能。支持每日自动更新、敏感词自定义过滤。

## 功能特点

- 📅 获取当天的历史事件（支持所有日期）
- 🔄 **自动过滤敏感内容**（敏感词可自定义，见下方说明）
- ⏰ 每天 **00:01** 自动更新，失败自动重试 2 次
- 📜 **头条滚动显示**，滚动间隔可配置（5‑300 秒）
- 🏷️ 两个实体：`sensor.jin_ri_li_shi`（今日历史）和 `sensor.gun_dong_li_shi`（滚动历史）
- 🌐 全中文界面，配置简单

## 安装

### 通过 HACS 安装（推荐）

1. 在 HACS 中点击 **集成** → 右下角 **自定义存储库**
2. 输入仓库地址：`https://github.com/lambilly/hass_tian_history`
3. 类别选择 **集成**
4. 点击 **添加**，然后搜索 **历史上的今天** 安装
5. 重启 Home Assistant

### 手动安装

1. 下载本仓库最新代码
2. 将 `custom_components/tian_history` 文件夹复制到 Home Assistant 的 `config/custom_components` 目录
3. 重启 Home Assistant

## 配置

### 第一步：获取 API 密钥

1. 访问 [天聚数行](https://www.tianapi.com/)
2. 注册账号并申请 **“历史上的今天”** API 接口（免费版足够使用）
3. 获取您的 API 密钥（32 位字符串）

### 第二步：添加集成

1. 进入 Home Assistant → **设置** → **设备与服务** → **集成**
2. 点击 **添加集成**，搜索 **历史上的今天**
3. 输入您的 API 密钥
4. 设置 **头条滚动间隔**（秒，默认 30，范围 5‑300）
5. 点击 **提交**

> 集成添加成功后，会自动创建一个设备 **信息查询**，包含两个传感器实体。

## 实体说明

| 实体 | 状态 | 属性 |
|------|------|------|
| `sensor.jin_ri_li_shi` | 当前日期（YYYY‑MM‑DD） | `today_item`（今日随机一条）、`history_list`（全部事件）、`total_count`、`update_time`（API 请求时间） |
| `sensor.gun_dong_li_shi` | 当前日期 | `title`、`year`、`lsdate`、`content`、`scroll_index`、`total_items`、`scroll_interval` |

## 敏感词自定义

集成会过滤包含特定关键词的历史事件（如“去世”、“逝世”等）。您可以通过编辑外部文件来增删敏感词。

**文件位置**：`/config/custom_components/tian_history/sensitive_words.txt`

**格式说明**：
- 每行一个敏感词
- 以 `#` 开头的行是注释，会被忽略
- 空行忽略

**示例**：
```text
# 这是我自定义的敏感词列表
去世
逝世
谋害
# 以下是我要排除的
暗杀
