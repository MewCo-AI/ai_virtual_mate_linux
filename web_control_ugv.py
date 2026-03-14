from web_control_quad import *

app2 = Flask(__name__, static_folder='dist')
current_move_gear = ugv_move_gear
current_rotate_gear = ugv_rotate_gear


def send_serial_ugv_web(msg):
    try:
        ser = Serial(ugv_robot_port, 115200, timeout=0.1)
        data = bytes.fromhex(msg.replace(" ", ""))
        ser.write(data)
        ser.close()
        return {"status": "success", "message": "命令发送成功"}
    except Exception as e:
        error_msg = f"四轮机器人未连接或串口编号设置错误，请前往系统设置修改，错误详情：{e}"
        print(error_msg)
        return {"status": "error", "message": error_msg}


def turn_left_ugv_web(gear):
    gear_hex_map = {6: "7B 00 00 00 00 00 00 01 2C 56 7D", 5: "7B 00 00 00 00 00 00 00 FA 81 7D",
                    4: "7B 00 00 00 00 00 00 00 C8 B3 7D", 3: "7B 00 00 00 00 00 00 00 96 ED 7D",
                    2: "7B 00 00 00 00 00 00 00 64 1F 7D", 1: "7B 00 00 00 00 00 00 00 32 49 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    if hex_data == "Gear Error":
        return {"status": "error", "message": "无效的旋转档位"}
    result = send_serial_ugv_web(hex_data)
    if result["status"] == "success":
        result["message"] = "机器人逆时针旋转"
    return result


def turn_right_ugv_web(gear):
    gear_hex_map = {6: "7B 00 00 00 00 00 00 FE D4 51 7D", 5: "7B 00 00 00 00 00 00 FF 06 82 7D",
                    4: "7B 00 00 00 00 00 00 FF 38 BC 7D", 3: "7B 00 00 00 00 00 00 FF 6A EE 7D",
                    2: "7B 00 00 00 00 00 00 FF 9C 18 7D", 1: "7B 00 00 00 00 00 00 FF CE 4A 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    if hex_data == "Gear Error":
        return {"status": "error", "message": "无效的旋转档位"}
    result = send_serial_ugv_web(hex_data)
    if result["status"] == "success":
        result["message"] = "机器人顺时针旋转"
    return result


def up_robot_ugv_web(gear):
    gear_hex_map = {6: "7B 00 00 01 2C 00 00 00 00 56 7D", 5: "7B 00 00 00 FA 00 00 00 00 81 7D",
                    4: "7B 00 00 00 C8 00 00 00 00 B3 7D", 3: "7B 00 00 00 96 00 00 00 00 ED 7D",
                    2: "7B 00 00 00 64 00 00 00 00 1F 7D", 1: "7B 00 00 00 32 00 00 00 00 49 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    if hex_data == "Gear Error":
        return {"status": "error", "message": "无效的移动档位"}
    result = send_serial_ugv_web(hex_data)
    if result["status"] == "success":
        result["message"] = "机器人前进"
    return result


def down_robot_ugv_web(gear):
    gear_hex_map = {6: "7B 00 00 FE D4 00 00 00 00 51 7D", 5: "7B 00 00 FF 06 00 00 00 00 82 7D",
                    4: "7B 00 00 FF 38 00 00 00 00 BC 7D", 3: "7B 00 00 FF 6A 00 00 00 00 EE 7D",
                    2: "7B 00 00 FF 9C 00 00 00 00 18 7D", 1: "7B 00 00 FF CE 00 00 00 00 4A 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    if hex_data == "Gear Error":
        return {"status": "error", "message": "无效的移动档位"}
    result = send_serial_ugv_web(hex_data)
    if result["status"] == "success":
        result["message"] = "机器人后退"
    return result


def emergency_stop_ugv_web():
    result = send_serial_ugv_web('7B 00 00 00 00 00 00 00 00 7B 7D')
    if result["status"] == "success":
        result["message"] = "机器人停止成功"
    return result


html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/png" href="assets/image/logo.png"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>四轮机器人控制 - Aivmate LX3</title>
    <style>
        .button-row {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 10px;
        }
        .control-button {
            padding: 10px;
            border: none;
            cursor: pointer;
            color: white;
            flex: 0 0 110px;
            text-align: center;
        }
        .button-container {
            max-width: 600px;
            margin: 0 auto;
        }
    </style>
</head>
<body style="font-family: Arial, sans-serif; margin: 10px; background-color: #0a1929; color: white;">
    <h1 style="text-align: center; color: white;"><img src="assets/image/logo.png" alt="Logo" style="width: 25px; height: 25px; margin-right: 5px;">四轮机器人控制</h1>
    <div class="button-container">
        <div style="background-color: #1e3a5f; padding: 15px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #2c5282;">
            <h2 style="font-size: 18px; margin-bottom: 10px; color: white;">🚗移动档位</h2>
            <input type="range" id="moveGear" min="1" max="6" value="{{ move_gear }}" 
                   style="width: 100%;" onchange="updateGear('move', this.value)">
            <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 14px; color: white;">
                <span>慢速</span>
                <span id="moveGearValue">{{ move_gear }}</span>
                <span>快速</span>
            </div>
        </div>
        <div style="background-color: #1e3a5f; padding: 15px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #2c5282;">
            <h2 style="font-size: 18px; margin-bottom: 10px; color: white;">🔄旋转档位</h2>
            <input type="range" id="rotateGear" min="1" max="6" value="{{ rotate_gear }}" 
                   style="width: 100%;" onchange="updateGear('rotate', this.value)">
            <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 14px; color: white;">
                <span>慢速</span>
                <span id="rotateGearValue">{{ rotate_gear }}</span>
                <span>快速</span>
            </div>
        </div>
        <div style="background-color: #1e3a5f; padding: 15px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #2c5282;">
            <h2 style="font-size: 18px; margin-bottom: 15px; color: white;">🎮操控面板</h2>
            
            <div class="button-row">
                <button id="btnUp" class="control-button" style="background-color: #4CAF50;" onclick="sendCommand('up')">
                    前进⬆️
                </button>
            </div>
            <div class="button-row">
                <button id="btnLeft" class="control-button" style="background-color: #1565c0;" onclick="sendCommand('left')">
                    ⬅️左转
                </button>
                <button id="btnStop" class="control-button" style="background-color: #b71c1c;" onclick="sendCommand('stop')">
                    急停⏹️
                </button>
                <button id="btnRight" class="control-button" style="background-color: #1565c0;" onclick="sendCommand('right')">
                    右转➡️
                </button>
            </div>
            <div class="button-row">
                <button id="btnDown" class="control-button" style="background-color: #4CAF50;" onclick="sendCommand('down')">
                    后退⬇️
                </button>
            </div>
        </div>
        <div style="background-color: #1e3a5f; padding: 15px; border-radius: 5px; border: 1px solid #2c5282;">
            <h2 style="font-size: 18px; margin-bottom: 10px; color: white;">ℹ️状态信息</h2>
            <div id="statusMessage" style="min-height: 40px; padding: 10px; background-color: #0a2540; border-radius: 3px; font-size: 14px; color: white;">
                等待点击按钮...
            </div>
        </div>
    </div>
    <script>
        function updateGear(type, value) {
            const valueElement = type === 'move' ? document.getElementById('moveGearValue') : document.getElementById('rotateGearValue');
            valueElement.textContent = value;
            const xhr = new XMLHttpRequest();
            xhr.open('GET', `/set_gear?type=${type}&value=${value}`, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);
                        if (response.status !== 'success') {
                            document.getElementById('statusMessage').textContent = response.message;
                            document.getElementById('statusMessage').style.backgroundColor = '#3d0a0a';
                        }
                    } else {
                        document.getElementById('statusMessage').textContent = '更新档位失败';
                        document.getElementById('statusMessage').style.backgroundColor = '#3d0a0a';
                    }
                }
            };
            xhr.send();
        }
        function sendCommand(command) {
            const moveGear = document.getElementById('moveGear').value;
            const rotateGear = document.getElementById('rotateGear').value;
            let params = `command=${command}`;
            if (command === 'up' || command === 'down') {
                params += `&gear=${moveGear}`;
            } else if (command === 'left' || command === 'right') {
                params += `&gear=${rotateGear}`;
            }
            const xhr = new XMLHttpRequest();
            xhr.open('GET', `/control?${params}`, true);
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
    </script>
</body>
</html>"""


# open_source_project_address:https://github.com/MewCo-AI/ai_virtual_mate_linux
@app2.route('/')
def index():
    return render_template_string(html_template, move_gear=current_move_gear, rotate_gear=current_rotate_gear)


@app2.route('/control')
def control():
    command = request.args.get('command')
    gear = request.args.get('gear', type=int)
    try:
        if command == 'up':
            result = up_robot_ugv_web(gear)
        elif command == 'down':
            result = down_robot_ugv_web(gear)
        elif command == 'left':
            result = turn_left_ugv_web(gear)
        elif command == 'right':
            result = turn_right_ugv_web(gear)
        elif command == 'stop':
            result = emergency_stop_ugv_web()
        else:
            result = {"status": "error", "message": "无效的命令"}
    except Exception as e:
        result = {"status": "error", "message": f"执行命令时出错: {e}"}
    return jsonify(result)


@app2.route('/set_gear')
def set_gear():
    global current_move_gear, current_rotate_gear
    gear_type = request.args.get('type')
    value = request.args.get('value', type=int)
    if gear_type == 'move':
        current_move_gear = value
    elif gear_type == 'rotate':
        current_rotate_gear = value
    else:
        return jsonify({"status": "error", "message": "无效的档位类型"})
    return jsonify({"status": "success", "message": f"{gear_type}档位已设置为 {value}"})


@app2.route('/assets/<path:path>')
def serve_static(path):  # 静态资源
    return send_from_directory('./dist/assets', path)


def run_control_web_ugv():  # 启动四轮机器人控制网页服务
    print(f"四轮机器人控制网址：http://{lan_ip}:{str(control_ugv_port)}\n")
    app2.run(port=control_ugv_port, host="0.0.0.0")
