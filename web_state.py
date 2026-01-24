from llm import *

app = Flask(__name__, static_folder='dist')
logging.getLogger('werkzeug').setLevel(logging.ERROR)
ugv_robot_data = {'battery_percent': '-', 'speed_x': '-', 'speed_y': '-', 'acc_x': '-', 'acc_y': '-', 'acc_z': '-',
                  'gyro_x': '-', 'gyro_y': '-', 'gyro_z': '-'}
quad_robot_data = {'battery_voltage': '-', 'battery_percent': '-'}


def parse_data(bytes_list):  # 解析数据
    if bytes_list.startswith("7b") and bytes_list.endswith("7d") and len(bytes_list) == 48:
        bytes_list = ' '.join(bytes_list[i:i + 2] for i in range(0, len(bytes_list), 2))
        bytes_list = bytes_list.split()
        # XY双轴速度
        speed_x = int(bytes_list[2] + bytes_list[3], 16)
        if speed_x > 32767:
            speed_x = -(65536 - speed_x)
        speed_x = speed_x * 0.001
        speed_y = int(bytes_list[4] + bytes_list[5], 16)
        if speed_y > 32767:
            speed_y = -(65536 - speed_y)
        speed_y = speed_y * 0.001
        speed_z = int(bytes_list[6] + bytes_list[7], 16)
        if speed_z > 32767:
            speed_z = -(65536 - speed_z)
        speed_z = speed_z * 0.0573
        # IMU三轴加速度
        imu_acc_x = int(bytes_list[8] + bytes_list[9], 16)
        if imu_acc_x > 32767:
            imu_acc_x = -(65536 - imu_acc_x)
        imu_acc_x = imu_acc_x * 19.6 / (2 ** 15)
        imu_acc_y = int(bytes_list[10] + bytes_list[11], 16)
        if imu_acc_y > 32767:
            imu_acc_y = -(65536 - imu_acc_y)
        imu_acc_y = imu_acc_y * 19.6 / (2 ** 15)
        imu_acc_z = int(bytes_list[12] + bytes_list[13], 16)
        if imu_acc_z > 32767:
            imu_acc_z = -(65536 - imu_acc_z)
        imu_acc_z = imu_acc_z * 19.6 / (2 ** 15)
        # 三轴角速度
        gyro_x = int(bytes_list[14] + bytes_list[15], 16)
        if gyro_x > 32767:
            gyro_x = -(65536 - gyro_x)
        gyro_x = gyro_x * 500 / (2 ** 15)
        gyro_y = int(bytes_list[16] + bytes_list[17], 16)
        if gyro_y > 32767:
            gyro_y = -(65536 - gyro_y)
        gyro_y = gyro_y * 500 / (2 ** 15)
        # 电池电压
        battery_voltage = int(bytes_list[20] + bytes_list[21], 16)
        battery_voltage = battery_voltage * 0.001
        return speed_x, speed_y, imu_acc_x, imu_acc_y, imu_acc_z, gyro_x, gyro_y, speed_z, battery_voltage
    return None


def update_ugv_robot_state():  # 更新四轮机器人状态
    global ugv_robot_data
    try:
        ser = Serial(ugv_robot_port, 115200, timeout=0.1)
        line = ser.readline()
        stm32_output = line.hex()[:48]
        ser.close()
        stm32_result = parse_data(stm32_output)
        if stm32_result:
            cell_voltage = stm32_result[8]
            cell_percent = int(((cell_voltage - 20) / (23.5 - 20)) * 99 + 1)
            cell_percent = max(0, min(100, cell_percent))
            ugv_robot_data = {'battery_percent': f"{cell_percent}%", 'speed_x': f"{stm32_result[0]:.3f} m/s",
                              'speed_y': f"{stm32_result[1]:.3f} m/s", 'acc_x': f"{stm32_result[2]:.3f} m/s²",
                              'acc_y': f"{stm32_result[3]:.3f} m/s²", 'acc_z': f"{stm32_result[4]:.3f} m/s²",
                              'gyro_x': f"{stm32_result[5]:.3f} °/s", 'gyro_y': f"{stm32_result[6]:.3f} °/s",
                              'gyro_z': f"{stm32_result[7]:.3f} °/s"}
    except:
        pass


def update_quad_robot_state():  # 更新四足机器人状态
    global quad_robot_data
    quad_voltage2, quad_battery_percent2 = get_current_state()
    try:
        quad_robot_data = {'battery_voltage': f"{quad_voltage2:.2f}V", 'battery_percent': f"{quad_battery_percent2}%"}
    except Exception as e:
        print(f"更新四足机器人状态时出错: {e}")
        quad_robot_data = {'battery_voltage': '-', 'battery_percent': '-'}


state_web_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/png" href="assets/image/logo.png"/>
    <title>主机状态 - Aivmate LX3</title>
    <style>
        body{background-color:#003366;color:white;margin:0}
        .container{max-width:1900px;margin:0 auto;padding:10px;box-sizing:border-box;}
        .header{text-align:center;margin-bottom:20px;position:relative}
        .header h1{margin:0;font-size:28px}
        .dropdown-container {
            position: absolute;
            top: 60px;
            right: 10px;
            display: inline-block;
        }
        #dropdown-btn {
            background-color: #0066cc;
            color: white;
            border: none;
            padding: 10px 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        #dropdown-btn:hover {
            background-color: #0052a3;
        }
        .dropdown-content {
            display: none;
            position: absolute;
            right: 0;
            background-color: rgba(0, 50, 100, 0.9);
            min-width: 160px;
            box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
            z-index: 1;
            border-radius: 5px;
            overflow: hidden;
        }
        .dropdown-content button {
            color: white;
            padding: 10px 15px;
            text-decoration: none;
            display: block;
            width: 100%;
            text-align: left;
            border: none;
            background: none;
            cursor: pointer;
        }
        .dropdown-content button:hover {
            background-color: rgba(0, 80, 150, 0.7);
        }
        .show {
            display: block;
        }
        .panel{background-color:rgba(0,50,100,0.7);border-radius:5px;padding:10px;margin-bottom:10px;box-shadow:0 0 10px rgba(0,0,0,0.5)}
        .panel-title{font-size:18px;font-weight:bold;margin-bottom:15px;border-bottom:1px solid #0066cc;padding-bottom:5px}
        .metrics-row{display:flex;flex-wrap:wrap;justify-content:space-between}
        .metric-box{flex:1;min-width:150px;text-align:center;margin:5px;padding:5px;background-color:rgba(0,80,150,0.5);border-radius:5px}
        .metric-label{font-size:14px}
        .metric-value{font-size:24px;font-weight:bold}
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 20px;
        }
        .chat-messages {
            height: 300px;
            overflow-y: auto;
            background-color: rgba(0, 40, 80, 0.5);
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #0066cc;
            scrollbar-width: thin;
            scrollbar-color: #0066cc rgba(0, 40, 80, 0.5);
        }
        .chat-messages::-webkit-scrollbar {
            width: 8px;
        }
        .chat-messages::-webkit-scrollbar-track {
            background: rgba(0, 40, 80, 0.5);
            border-radius: 4px;
        }
        .chat-messages::-webkit-scrollbar-thumb {
            background: #0066cc;
            border-radius: 4px;
        }
        .chat-messages::-webkit-scrollbar-thumb:hover {
            background: #0052a3;
        }
        .message {
            margin-bottom: 10px;
            padding: 8px 12px;
            border-radius: 5px;
            max-width: 50%;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user-message {
            background-color: rgba(0, 100, 200, 0.5);
            align-self: flex-end;
            margin-left: auto;
            border-bottom-right-radius: 0;
        }
        .ai-message {
            background-color: rgba(0, 150, 100, 0.5);
            align-self: flex-start;
            border-bottom-left-radius: 0;
        }
        .chat-input-container {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .clear-button {
            padding: 8px 12px;
            background-color: #660000;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            white-space: nowrap;
            font-size: 14px;
        }
        .clear-button:hover {
            background-color: #330000;
        }
        .chat-input {
            flex: 1;
            padding: 8px;
            border: 1px solid #0066cc;
            border-radius: 4px;
            background-color: rgba(0, 80, 150, 0.5);
            color: white;
        }
        .chat-input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        .send-button {
            padding: 8px 16px;
            background-color: #0066cc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            white-space: nowrap;
        }
        .send-button:hover {
            background-color: #0052a3;
        }
        .robot-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .robot-table td {
            padding: 8px;
            border: 1px solid #0066cc;
            text-align: center;
        }
        .robot-table tr:first-child td {
            background-color: rgba(0, 80, 150, 0.7);
            font-weight: bold;
        }
        .loading {
            display: none;
            color: #00ccff;
            font-style: italic;
            text-align: center;
            padding: 5px;
        }
        .timestamp {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><img src="assets/image/logo.png" alt="Logo" style="width:25px; height:25px; margin-right:5px;">Aivmate LX3</h1>
            <div class="dropdown-container">
                <button id="dropdown-btn">📜功能菜单</button>
                <div id="dropdown-content" class="dropdown-content">
                    <button id="live2d-btn">👤Live2D角色</button>
                    <button id="mmd-btn">👤MMD 3D角色</button>
                    <button id="vmd-btn">💃MMD 3D动作</button>
                    <button id="vrm-btn">👤VRM 3D角色</button>
                    <button id="control-btn_quad">🎮四足机器人控制</button>
                    <button id="control-btn_ugv">🎮四轮机器人控制</button>
                    <button id="settings-btn">⚙️系统设置</button>
                </div>
            </div>
        </div>
        <div class="panel">
            <div class="panel-title">💻硬件状态</div>
            <div class="metrics-row">
                <div class="metric-box">
                    <div class="metric-label">💻CPU使用率</div>
                    <div class="metric-value" id="cpu_percent">0%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">💾内存使用率</div>
                    <div class="metric-value" id="memory_percent">0%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">🌡️内部温度</div>
                    <div class="metric-value" id="temp">0℃</div>
                </div>
            </div>
        </div>
        <div class="panel">
            <div class="panel-title">🌐网络状态</div>
            <div class="metrics-row">
                <div class="metric-box">
                    <div class="metric-label">🌍外部网络</div>
                    <div class="metric-value" id="wan_info">-</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">🏠内部网络</div>
                    <div class="metric-value" id="lan_info">-</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">📶WiFi</div>
                    <div class="metric-value" id="wifi_info">-</div>
                </div>
            </div>
        </div>
        <div class="panel">
            <div class="panel-title">💬AI聊天</div>
            <div class="chat-container">
                <div class="chat-messages" id="chat_messages">
                    <div class="message ai-message">
                        <div>哈喽,{{ username }},我是{{ mate_name }},欢迎使用Aivmate LX3✨</div>
                        <div class="timestamp">刚刚</div>
                    </div>
                </div>
                <div class="loading" id="loading">{{ mate_name }}正在思考与回答...</div>
                <div class="chat-input-container">
                    <button id="clear_button" class="clear-button">➕新对话</button>
                    <input type="text" id="chat_input" placeholder="请输入消息..." class="chat-input">
                    <button id="send_button" class="send-button">发送</button>
                </div>
            </div>
        </div>
        <div class="panel">
            <div class="panel-title">🤖四足机器人状态</div>
            <table class="robot-table">
                <tr>
                    <td>电池电压</td>
                    <td>电池电量</td>
                    <td>状态</td>
                </tr>
                <tr>
                    <td><span id="quad_battery_voltage">--</span></td>
                    <td><span id="quad_battery_percent">--</span></td>
                    <td><span id="quad_status">--</span></td>
                </tr>
            </table>
        </div>
        <div class="panel">
            <div class="panel-title">🤖四轮机器人状态</div>
            <table class="robot-table">
                <tr>
                    <td>电池电量</td>
                    <td>X方向速度</td>
                    <td>Y方向速度</td>
                </tr>
                <tr>
                    <td><span id="robot_battery_percent">--</span></td>
                    <td><span id="robot_speed_x">--</span></td>
                    <td><span id="robot_speed_y">--</span></td>
                </tr>
                <tr>
                    <td>X方向加速度</td>
                    <td>Y方向加速度</td>
                    <td>Z方向加速度</td>
                </tr>
                <tr>
                    <td><span id="robot_acc_x">--</span></td>
                    <td><span id="robot_acc_y">--</span></td>
                    <td><span id="robot_acc_z">--</span></td>
                </tr>
                <tr>
                    <td>X方向角速度</td>
                    <td>Y方向角速度</td>
                    <td>Z方向角速度</td>
                </tr>
                <tr>
                    <td><span id="robot_gyro_x">--</span></td>
                    <td><span id="robot_gyro_y">--</span></td>
                    <td><span id="robot_gyro_z">--</span></td>
                </tr>
            </table>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const dropdownBtn = document.getElementById('dropdown-btn');
            const dropdownContent = document.getElementById('dropdown-content');
            const chatMessages = document.getElementById('chat_messages');
            const loading = document.getElementById('loading');
            const clearButton = document.getElementById('clear_button');
            dropdownBtn.addEventListener('click', function() {
                dropdownContent.classList.toggle('show');
            });
            window.addEventListener('click', function(event) {
                if (!event.target.matches('#dropdown-btn')) {
                    if (dropdownContent.classList.contains('show')) {
                        dropdownContent.classList.remove('show');
                    }
                }
            });
            document.getElementById('live2d-btn').addEventListener('click', function() {
                window.open(document.getElementById('live2d_url').href, '_blank');
                dropdownContent.classList.remove('show');
            });
            document.getElementById('mmd-btn').addEventListener('click', function() {
                window.open(document.getElementById('mmd_url').href, '_blank');
                dropdownContent.classList.remove('show');
            });
            document.getElementById('vmd-btn').addEventListener('click', function() {
                window.open(document.getElementById('vmd_url').href, '_blank');
                dropdownContent.classList.remove('show');
            });
            document.getElementById('vrm-btn').addEventListener('click', function() {
                window.open(document.getElementById('vrm_url').href, '_blank');
                dropdownContent.classList.remove('show');
            });
            document.getElementById('control-btn_quad').addEventListener('click', function() {
                window.open(document.getElementById('control_url_quad').href, '_blank');
                dropdownContent.classList.remove('show');
            });
            document.getElementById('control-btn_ugv').addEventListener('click', function() {
                window.open(document.getElementById('control_url_ugv').href, '_blank');
                dropdownContent.classList.remove('show');
            });
            document.getElementById('settings-btn').addEventListener('click', function() {
                window.open(document.getElementById('settings_url').href, '_blank');
                dropdownContent.classList.remove('show');
            });
            const live2dUrl = document.createElement('a');
            live2dUrl.id = 'live2d_url';
            live2dUrl.style.display = 'none';
            document.body.appendChild(live2dUrl);           
            const mmdUrl = document.createElement('a');
            mmdUrl.id = 'mmd_url';
            mmdUrl.style.display = 'none';
            document.body.appendChild(mmdUrl);
            const vmdUrl = document.createElement('a');
            vmdUrl.id = 'vmd_url';
            vmdUrl.style.display = 'none';
            document.body.appendChild(vmdUrl);
            const vrmUrl = document.createElement('a');
            vrmUrl.id = 'vrm_url';
            vrmUrl.style.display = 'none';
            document.body.appendChild(vrmUrl);
            const controlUrlQuad = document.createElement('a');
            const controlUrlUgv = document.createElement('a');
            const settingsUrl = document.createElement('a');
            controlUrlQuad.id = 'control_url_quad';
            controlUrlUgv.id = 'control_url_ugv';
            settingsUrl.id = 'settings_url';
            controlUrlQuad.style.display = 'none';
            controlUrlUgv.style.display = 'none';
            settingsUrl.style.display = 'none';
            document.body.appendChild(controlUrlUgv);
            document.body.appendChild(controlUrlQuad);
            document.body.appendChild(settingsUrl);
            function formatTime() {
                const now = new Date();
                return now.getHours().toString().padStart(2, '0') + ':' + 
                       now.getMinutes().toString().padStart(2, '0') + ':' + 
                       now.getSeconds().toString().padStart(2, '0');
            }
            function addMessage(message, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = isUser ? 'message user-message' : 'message ai-message';
                const contentDiv = document.createElement('div');
                contentDiv.textContent = message;
                const timestampDiv = document.createElement('div');
                timestampDiv.className = 'timestamp';
                timestampDiv.textContent = formatTime();
                messageDiv.appendChild(contentDiv);
                messageDiv.appendChild(timestampDiv);
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            function clearChat() {
                chatMessages.innerHTML = `
                    <div class="message ai-message">
                        <div>聊天记录已清空</div>
                        <div class="timestamp">${formatTime()}</div>
                    </div>
                `;
            }
            clearButton.addEventListener('click', function() {
                if (confirm('确定要清空聊天记录吗？')) {
                    clearChat();
                }
            });
            function updateInfo() {
                fetch('/api/info')
                   .then(response => response.json())
                   .then(data => {
                        document.getElementById('cpu_percent').textContent = data.cpu_percent + '%';
                        document.getElementById('memory_percent').textContent = data.memory_percent + '%';
                        document.getElementById('temp').textContent = data.temp + '℃';
                        document.getElementById('wan_info').textContent = data.wan_info;
                        document.getElementById('lan_info').textContent = data.lan_info;
                        document.getElementById('wifi_info').textContent = data.wifi_info;
                        live2dUrl.href = data.live2d_url;
                        mmdUrl.href = data.mmd_url;
                        vmdUrl.href = data.vmd_url;
                        vrmUrl.href = data.vrm_url;
                        controlUrlUgv.href = data.control_url_ugv;
                        controlUrlQuad.href = data.control_url_quad;
                        settingsUrl.href = data.settings_url;
                        document.getElementById('robot_battery_percent').textContent = data.ugv_robot_data.battery_percent;
                        document.getElementById('robot_speed_x').textContent = data.ugv_robot_data.speed_x;
                        document.getElementById('robot_speed_y').textContent = data.ugv_robot_data.speed_y;
                        document.getElementById('robot_acc_x').textContent = data.ugv_robot_data.acc_x;
                        document.getElementById('robot_acc_y').textContent = data.ugv_robot_data.acc_y;
                        document.getElementById('robot_acc_z').textContent = data.ugv_robot_data.acc_z;
                        document.getElementById('robot_gyro_x').textContent = data.ugv_robot_data.gyro_x;
                        document.getElementById('robot_gyro_y').textContent = data.ugv_robot_data.gyro_y;
                        document.getElementById('robot_gyro_z').textContent = data.ugv_robot_data.gyro_z;
                        document.getElementById('quad_battery_voltage').textContent = data.quad_robot_data.battery_voltage;
                        document.getElementById('quad_battery_percent').textContent = data.quad_robot_data.battery_percent;
                        const batteryPercent = parseInt(data.quad_robot_data.battery_percent);
                        let status = '正常';
                        if (batteryPercent < 10) {
                            status = '极低电量';
                        } else if (batteryPercent < 20) {
                            status = '低电量';
                        }
                        document.getElementById('quad_status').textContent = status;
                    })
                   .catch(error => {
                        console.error('Error fetching data:', error);
                    });
            }
            document.getElementById('send_button').addEventListener('click', function() {
                const message = document.getElementById('chat_input').value;
                if (message.trim() === '') return;
                addMessage(message, true);
                document.getElementById('chat_input').value = '';
                loading.style.display = 'block';
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({message: message})
                })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = 'none';
                    if (data.status === 'success') {
                        addMessage(data.response);
                    } else {
                        addMessage('抱歉，处理您的请求时出现错误: ' + (data.message || '未知错误'));
                    }
                })
                .catch(error => {
                    loading.style.display = 'none';
                    console.error('Error:', error);
                    addMessage('抱歉，发送消息时出现错误，请稍后再试。');
                });
            });
            document.getElementById('chat_input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    document.getElementById('send_button').click();
                }
            });
            updateInfo();
            setInterval(updateInfo, 5000);
        });
    </script>
</body>
</html>"""


# open_source_project_address:https://github.com/swordswind/ai_virtual_mate_linux
@app.route('/')
def index():
    return render_template_string(state_web_html, mate_name=mate_name, username=username)


@app.route('/api/info')
def get_info():
    try:
        temps = psutil.sensors_temperatures()
        temp = int(temps[next(iter(temps))][0].current)
    except:
        temp = "-"
    if embody_ai_mode == "ugv":
        update_ugv_robot_state()
    elif embody_ai_mode == "quad":
        update_quad_robot_state()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory_percent = psutil.virtual_memory().percent
    wan_info = get_wan_info()
    lan_info = get_lan_info()
    wifi_info = get_wifi_info()
    return jsonify({
        'cpu_percent': cpu_percent, 'memory_percent': memory_percent, 'temp': temp, 'wan_info': wan_info,
        'lan_info': lan_info, 'wifi_info': wifi_info, 'live2d_url': f"http://{lan_ip}:{live2d_port}",
        'mmd_url': f"http://{lan_ip}:{mmd_port}", 'vmd_url': f"http://{lan_ip}:{mmd_port}/vmd",
        'vrm_url': f"http://{lan_ip}:{vrm_port}", 'control_url_quad': f"http://{lan_ip}:{control_quad_port}",
        'control_url_ugv': f"http://{lan_ip}:{control_ugv_port}", 'settings_url': f"http://{lan_ip}:5250",
        'ugv_robot_data': ugv_robot_data, 'quad_robot_data': quad_robot_data})


@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.json
    message = data.get('message')
    if message:
        try:
            res = chat_preprocess(message)
            return jsonify({'status': 'success', 'response': res})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': '消息未提供'}), 400


@app.route('/assets/<path:path>')
def serve_static(path):  # 静态资源
    return send_from_directory('./dist/assets', path)


def run_state_web():  # 启动主机状态监测服务
    print(f"主机状态网址：http://{lan_ip}:{str(state_port)}\n")
    app.run(port=state_port, host="0.0.0.0")
