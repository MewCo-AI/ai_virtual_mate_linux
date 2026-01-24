from web_state import *
app4 = Flask(__name__, static_folder='dist')

quad_control_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/png" href="assets/image/logo.png"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>四足机器人控制 - Aivmate LX3</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 10px;
            background-color: #0a1929;
            color: white;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: white;
        }
        .panel {
            background-color: #1e3a5f;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border: 1px solid #2c5282;
        }
        h2 {
            font-size: 18px;
            margin-bottom: 10px;
            color: white;
        }
        .control-buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        .action-buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        button {
            padding: 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .direction-btn {
            background-color: #1565c0;
            color: white;
        }
        .direction-btn:hover {
            background-color: #0d47a1;
        }
        .stop-btn {
            background-color: #b71c1c;
            color: white;
        }
        .stop-btn:hover {
            background-color: #8a0000;
        }
        .action-btn {
            background-color: #2e7d32;
            color: white;
        }
        .action-btn:hover {
            background-color: #1b5e20;
        }
        .status {
            background-color: #0a2540;
            padding: 10px;
            border-radius: 3px;
            min-height: 40px;
            margin-top: 10px;
        }
        .battery-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .battery-bar {
            width: 100%;
            height: 20px;
            background-color: #333;
            border-radius: 10px;
            overflow: hidden;
        }
        .battery-fill {
            height: 100%;
            background-color: #4CAF50;
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><img src="assets/image/logo.png" alt="Logo" style="width: 25px; height: 25px; margin-right: 5px;">四足机器人控制</h1>
        <div class="panel">
            <h2>🔋电池状态</h2>
            <div class="battery-info">
                <span>电压: <span id="voltage">--</span> V</span>
                <span>电量: <span id="battery">--</span> %</span>
            </div>
            <div class="battery-bar">
                <div class="battery-fill" id="battery-fill" style="width: 0%"></div>
            </div>
        </div>
        <div class="panel">
            <h2>🎮方向控制</h2>
            <div class="control-buttons">
                <div></div>
                <button id="btnUp" class="direction-btn" onclick="sendCommand('up')">前进⬆️</button>
                <div></div>
                <button id="btnLeft" class="direction-btn" onclick="sendCommand('left')">⬅️左转</button>
                <button id="btnStop" class="stop-btn" onclick="sendCommand('stop')">急停⏹️</button>
                <button id="btnRight" class="direction-btn" onclick="sendCommand('right')">右转➡️</button>
                <div></div>
                <button id="btnDown" class="direction-btn" onclick="sendCommand('down')">后退⬇️</button>
                <div></div>
            </div>
        </div>
        <div class="panel">
            <h2>🤸动作控制</h2>
            <div class="action-buttons">
                <button id="btnSquat" class="action-btn" onclick="sendAction('squat')">下蹲🧎</button>
                <button id="btnWave" class="action-btn" onclick="sendAction('wave')">招手👋</button>
                <button id="btnJump" class="action-btn" onclick="sendAction('jump')">跳跃🦘</button>
            </div>
        </div>
        <div class="panel">
            <h2>ℹ️状态信息</h2>
            <div id="statusMessage" class="status">等待点击按钮...</div>
        </div>
    </div>
    <script>
        function sendCommand(command) {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', `/control?command=${command}`, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);
                        document.getElementById('statusMessage').textContent = response.message;
                        document.getElementById('statusMessage').style.backgroundColor = 
                            response.status === 'success' ? '#0a2540' : '#3d0a0a';
                    } else {
                        document.getElementById('statusMessage').textContent = '发送命令失败';
                        document.getElementById('statusMessage').style.backgroundColor = '#3d0a0a';
                    }
                }
            };
            xhr.send();
        }
        function sendAction(action) {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', `/action?action=${action}`, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);
                        document.getElementById('statusMessage').textContent = response.message;
                        document.getElementById('statusMessage').style.backgroundColor = 
                            response.status === 'success' ? '#0a2540' : '#3d0a0a';
                    } else {
                        document.getElementById('statusMessage').textContent = '发送动作命令失败';
                        document.getElementById('statusMessage').style.backgroundColor = '#3d0a0a';
                    }
                }
            };
            xhr.send();
        }
        function updateBatteryStatus() {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', '/battery_status', true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    document.getElementById('voltage').textContent = data.voltage;
                    document.getElementById('battery').textContent = data.battery;
                    document.getElementById('battery-fill').style.width = data.battery + '%';
                    const batteryFill = document.getElementById('battery-fill');
                    if (data.battery < 20) {
                        batteryFill.style.backgroundColor = '#f44336'; // 红色
                    } else if (data.battery < 50) {
                        batteryFill.style.backgroundColor = '#ff9800'; // 橙色
                    } else {
                        batteryFill.style.backgroundColor = '#4CAF50'; // 绿色
                    }
                }
            };
            xhr.send();
        }
        window.onload = function() {
            updateBatteryStatus();
            setInterval(updateBatteryStatus, 2000);
        };
    </script>
</body>
</html>"""


# open_source_project_address:https://github.com/swordswind/ai_virtual_mate_linux
@app4.route('/')
def index():
    return render_template_string(quad_control_html)


@app4.route('/control')
def control():
    command = request.args.get('command')
    try:
        if command == 'up':
            up_robot_quad()
            result = {"status": "success", "message": "机器人前进"}
        elif command == 'down':
            down_robot_quad()
            result = {"status": "success", "message": "机器人后退"}
        elif command == 'left':
            turn_left_quad()
            result = {"status": "success", "message": "机器人左转"}
        elif command == 'right':
            turn_right_quad()
            result = {"status": "success", "message": "机器人右转"}
        elif command == 'stop':
            emergency_stop_quad()
            result = {"status": "success", "message": "机器人停止"}
        else:
            result = {"status": "error", "message": "无效的命令"}
    except Exception as e:
        result = {"status": "error", "message": f"执行命令时出错: {e}"}
    return jsonify(result)


@app4.route('/action')
def run_action():
    action = request.args.get('action')
    try:
        if action == 'squat':
            run_quad_action("蹲")
            result = {"status": "success", "message": "执行下蹲动作"}
        elif action == 'wave':
            run_quad_action("手")
            result = {"status": "success", "message": "执行招手动作"}
        elif action == 'jump':
            run_quad_action("跳")
            result = {"status": "success", "message": "执行跳跃动作"}
        else:
            result = {"status": "error", "message": "无效的动作命令"}
    except Exception as e:
        result = {"status": "error", "message": f"执行动作时出错: {e}"}
    return jsonify(result)


@app4.route('/battery_status')
def battery_status():
    try:
        voltage, battery_percent = get_current_state()
        return jsonify({"voltage": f"{voltage:.2f}","battery": f"{battery_percent}"})
    except:
        return jsonify({"voltage": "--","battery": "--"})


@app4.route('/assets/<path:path>')
def serve_static(path):
    return send_from_directory('./dist/assets', path)


def run_control_web_quad():
    print(f"四足机器人控制网址：http://{lan_ip}:{control_quad_port}\n")
    app4.run(port=control_quad_port, host="0.0.0.0")
