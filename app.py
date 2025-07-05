import os
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

# --- 初始化 Flask 应用 ---
app = Flask(__name__)

# --- 加载配置 ---
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"错误：无法加载 config.json 文件。请确保文件存在且格式正确。错误信息: {e}")
    exit(1)

# --- 确保 submissions 目录存在 ---
if not os.path.exists('submissions'):
    os.makedirs('submissions')

def send_to_tmux(command):
    """向指定的 tmux 会话发送指令"""
    session_name = config.get('tmux_session_name', 'tex')
    try:
        # 使用 'send-keys' 发送命令，并附加 'C-m' (回车) 来执行
        subprocess.run([
            'tmux', 'send-keys', '-t', session_name, command, 'C-m'
        ], check=True)
        print(f"成功向 tmux 会话 '{session_name}' 发送指令: {command}")
        return True
    except FileNotFoundError:
        print("错误: 'tmux' 命令未找到。请确保 tmux 已安装并处于 PATH 中。")
        return False
    except subprocess.CalledProcessError as e:
        print(f"错误: 无法向 tmux 会话 '{session_name}' 发送指令。请确保会话存在且正在运行。错误: {e}")
        return False

# --- 网页路由 ---

@app.route('/')
def index():
    """规则首页"""
    return render_template('index.html', config=config)

@app.route('/survey')
def survey():
    """问卷页面"""
    return render_template('survey.html', config=config)

@app.route('/submit', methods=['POST'])
def submit():
    """处理问卷提交"""
    form_data = request.form.to_dict(flat=False)
    
    # 将只有一个值的字段从列表简化为字符串
    processed_data = {}
    for key, value in form_data.items():
        if len(value) == 1:
            processed_data[key] = value[0]
        else:
            processed_data[key] = value

    # 获取 Minecraft ID
    player_id = processed_data.get('minecraft_id')
    if not player_id or not player_id.strip():
        return jsonify({"status": "error", "message": "Minecraft 游戏ID是必填项，不能为空！"}), 400

    player_id = player_id.strip()

    # 获取账号类型
    account_type = processed_data.get('account_type')
    if not account_type:
        return jsonify({"status": "error", "message": "账号类型是必填项，请选择你的Minecraft账号类型！"}), 400

    # 获取QQ账号
    qq_number = processed_data.get('qq_number')
    if not qq_number or not qq_number.strip():
        return jsonify({"status": "error", "message": "QQ账号是必填项，不能为空！"}), 400

    # 获取QQ昵称
    qq_nickname = processed_data.get('qq_nickname')
    if not qq_nickname or not qq_nickname.strip():
        return jsonify({"status": "error", "message": "QQ昵称是必填项，不能为空！"}), 400

    # 检查是否同意服务器准则
    agree_rules = processed_data.get('agree_rules')
    if not agree_rules:
        return jsonify({"status": "error", "message": "必须同意遵守服务器游玩准则才能提交申请！"}), 400

    # 1. 准备并发送白名单指令
    if account_type == 'mojang':
        whitelist_command = f"!!whitelist add {player_id} Mojang"
    elif account_type == 'littleskin':
        whitelist_command = f"!!whitelist add {player_id} LittleSkin"
    elif account_type == 'xbox':
        whitelist_command = f"whitelist add {player_id}"
    else:
        return jsonify({"status": "error", "message": "无效的账号类型！"}), 400
    
    if not send_to_tmux(whitelist_command):
         return jsonify({"status": "error", "message": "向服务器后台发送指令失败，请联系服主处理。"}), 500

    # 2. 将问卷数据保存为 JSON 文件
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"submission_{player_id}_{timestamp}.json"
    filepath = os.path.join('submissions', filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"警告：白名单指令已发送，但保存问卷文件失败！错误: {e}")
        # 即使保存失败，也应该告诉用户成功了，因为核心功能（白名单）已完成
        pass

    # 3. 返回成功信息
    return render_template('success.html', player_id=player_id, config=config)


# --- 启动服务器 ---
if __name__ == '__main__':
    port = config.get('web_port', 5000)
    print(f"TecoEX 白名单申请站已启动，请访问 http://YOUR_SERVER_IP:{port}")
    app.run(host='0.0.0.0', port=port)