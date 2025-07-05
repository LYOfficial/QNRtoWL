# QNRtoWL
> 从问卷到白名单，新一代的 Minecraft 服务器开放自申请方案。
>
> Questionnaire to Whitelist of Minecraft.

## 简介

本项目是基于 Flask 开发的系统搭建的网页问卷白名单自助申请系统，为 Minecraft 服务器提供的新一代解决方案。

系统第一页用于展示服务器基本信息，第二页为一个简单的问卷。其中问卷第一题为 Minecraft ID 输入项，系统会读取 Minecraft ID 并将其发送至基于终端复用器 Tmux 内的终端窗口，注入白名单。

## 环境

Windows / MacOS / Linux 均可使用

Python >= 3.7

安装 Flask

```
pip install flask
```

## 配置

对 `config.json` 进行修改：

```
{

 "web_port": 12010, #端口

 "tmux_session_name": "tex", #tmux session名称

 "whitelist_api": "mojang", #白名单 api

 "background_image_url": "https://pic.awa.ms/f/2025/07/05/6868e8f590055.png", # 背景图片

 "server_name": "TecoEX 探索服", # 服务器相关内容

 "rules_title": "TecoEX 探索服游玩规则", # 服务器相关内容，用于网页

 "survey_title": "TecoEX 探索服白名单申请问卷" # 服务器相关内容，用于网页

}
```

## 安装启动

### 1 克隆本项目

```
git clone https://github.com/LYOfficial/QNRtoWL.git
```

### 2 修改配置

```
cd QNRtoWL
```

参照上一章节修改配置

### 3 启动 Minecraft 服务端

```
tmux new -s xxx # xxx为终端名，自定义
```

### 4 启动 QNRtoWL

```
tmux new -s QNR
python app.py
```



