from base64 import b64encode
from sport_quad import *

is_run_ugv = 1
last_angle = 0  # 初始化上一个角度
front_distance, right_distance, left_distance = 0, 0, 0


def parse_data(data):  # 解析数据包
    global front_distance, right_distance, left_distance
    start_angle = (data[2] * 256 + data[3]) / 100.0  # 计算起始角度
    for x in range(4, 98, 3):  # 遍历数据包中的距离和光强数据
        distance = data[x] * 256 + data[x + 1]  # 计算距离
        if start_angle < 30 or start_angle > 330:  # 打印某个角度的距离
            if distance > 0:
                front_distance = distance
        if 60 < start_angle < 120:  # 打印某个角度的距离
            if distance > 0:
                right_distance = distance
        if 240 < start_angle < 300:  # 打印某个角度的距离
            if distance > 0:
                left_distance = distance
    return start_angle


def radar_detect():  # 激光雷达数据处理
    global last_angle
    try:
        ser = Serial(ugv_radar_port, 460800, timeout=5)
    except Exception as e:
        print("激光雷达未连接或串口编号设置错误，请前往系统设置修改，错误详情：", e)
        return
    while True:
        try:
            data = ser.read(1)  # 读取1个字节的数据
            if data[0] == 0xA5:  # 检查数据包的头部
                data = ser.read(1)  # 读取1个字节的数据
                if data[0] == 0x5A:
                    data = ser.read(1)  # 读取1个字节的数据
                    if data[0] == 0x6C:
                        data = ser.read(105)  # 是数据帧头就读取整一帧，去掉帧头之后为55个字节
                        start_angle = parse_data(data)  # 解析和打印数据包
                        last_angle = start_angle  # 更新上一个角度
        except:
            pass


if embody_ai_mode == "ugv":
    Thread(target=radar_detect).start()


def send_serial_ugv(msg):  # 发送数据
    try:
        ser = Serial(ugv_robot_port, 115200, timeout=0.1)
        data = bytes.fromhex(msg)
        ser.write(data)
        ser.close()
    except Exception as e:
        print(f"四轮机器人未连接或串口编号设置错误，请前往系统设置修改，错误详情：{e}")


def turn_left_ugv(gear):  # 控制机器人逆时针旋转
    gear_hex_map = {6: "7B 00 00 00 00 00 00 01 2C 56 7D", 5: "7B 00 00 00 00 00 00 00 FA 81 7D",
                    4: "7B 00 00 00 00 00 00 00 C8 B3 7D", 3: "7B 00 00 00 00 00 00 00 96 ED 7D",
                    2: "7B 00 00 00 00 00 00 00 64 1F 7D", 1: "7B 00 00 00 00 00 00 00 32 49 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    send_serial_ugv(hex_data)
    print("机器人逆时针旋转")


def turn_right_ugv(gear):  # 控制机器人顺时针旋转
    gear_hex_map = {6: "7B 00 00 00 00 00 00 FE D4 51 7D", 5: "7B 00 00 00 00 00 00 FF 06 82 7D",
                    4: "7B 00 00 00 00 00 00 FF 38 BC 7D", 3: "7B 00 00 00 00 00 00 FF 6A EE 7D",
                    2: "7B 00 00 00 00 00 00 FF 9C 18 7D", 1: "7B 00 00 00 00 00 00 FF CE 4A 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    send_serial_ugv(hex_data)
    print("机器人顺时针旋转")


def up_robot_ugv(gear):  # 控制机器人向前移动
    gear_hex_map = {6: "7B 00 00 01 2C 00 00 00 00 56 7D", 5: "7B 00 00 00 FA 00 00 00 00 81 7D",
                    4: "7B 00 00 00 C8 00 00 00 00 B3 7D", 3: "7B 00 00 00 96 00 00 00 00 ED 7D",
                    2: "7B 00 00 00 64 00 00 00 00 1F 7D", 1: "7B 00 00 00 32 00 00 00 00 49 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    send_serial_ugv(hex_data)
    print("机器人前进")


def down_robot_ugv(gear):  # 控制机器人向后移动
    gear_hex_map = {6: "7B 00 00 FE D4 00 00 00 00 51 7D", 5: "7B 00 00 FF 06 00 00 00 00 82 7D",
                    4: "7B 00 00 FF 38 00 00 00 00 BC 7D", 3: "7B 00 00 FF 6A 00 00 00 00 EE 7D",
                    2: "7B 00 00 FF 9C 00 00 00 00 18 7D", 1: "7B 00 00 FF CE 00 00 00 00 4A 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    send_serial_ugv(hex_data)
    print("机器人后退")


def emergency_stop_ugv():  # 急停机器人运动
    global is_run_ugv
    is_run_ugv = 0
    send_serial_ugv('7B 00 00 00 00 00 00 00 00 7B 7D')
    print("机器人停止成功")


def pause_robot():  # 暂停机器人运动
    send_serial_ugv('7B 00 00 00 00 00 00 00 00 7B 7D')
    print("机器人暂停成功")


def auto_avoid():  # 自动避障
    global is_run_ugv
    is_run_ugv = 1
    while is_run_ugv == 1:
        try:
            print(f"自动避障模式  前距: {front_distance} mm  左距: {left_distance} mm  右距: {right_distance} mm")
            if front_distance < 1250:
                if left_distance < right_distance:
                    turn_right_ugv(ugv_rotate_gear)
                else:
                    turn_left_ugv(ugv_rotate_gear)
            else:
                up_robot_ugv(ugv_move_gear)
        except Exception as e:
            print(f"发生错误: {e}")
        time.sleep(0.5)


def encode_image(image):  # 图片转base64
    _, buffer = cv2.imencode('.jpg', image)
    return b64encode(buffer).decode('utf-8')


def free_activity():  # 自由活动
    global is_run_ugv
    is_run_ugv = 1
    cap = cv2.VideoCapture(cam_num)
    while is_run_ugv == 1:
        try:
            print(f"自由活动模式  前距: {front_distance} mm  左距: {left_distance} mm  右距: {right_distance} mm")
            if front_distance < 1250:
                if left_distance < right_distance:
                    turn_right_ugv(ugv_rotate_gear)
                else:
                    turn_left_ugv(ugv_rotate_gear)
            else:
                ret, frame = cap.read()
                base64_image = encode_image(frame)
                messages = [{"role": "user",
                             "content": [{"type": "text", "text": vla_prompt}, {"type": "image_url", "image_url": {
                                 "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
                vlm_client = ZhipuAiClient(api_key=glm_key)
                completion = vlm_client.chat.completions.create(model=glm_vlm_model, messages=messages,
                                                                thinking={"type": "disabled"})
                vla_command = completion.choices[0].message.content
                if "前进" in vla_command:
                    up_robot_ugv(1)
                elif "向左" in vla_command:
                    turn_left_ugv(1)
                elif "向右" in vla_command:
                    turn_right_ugv(1)
                else:
                    pause_robot()
                time.sleep(0.5)
        except Exception as e:
            print(f"发生错误: {e}")
        time.sleep(0.5)
    cap.release()


# open_source_project_address:https://github.com/swordswind/ai_virtual_mate_linux
def auto_find_yolo_ugv(obj):  # 自动寻找指定物体
    global is_run_ugv
    is_run_ugv = 1
    cap = cv2.VideoCapture(cam_num)
    while is_run_ugv == 1:
        try:
            print(f"自动寻找{obj}  前距: {front_distance} mm  左距: {left_distance} mm  右距: {right_distance} mm")
            if check_yolo(obj, cap) is True:
                up_robot_ugv(ugv_move_gear)
            else:
                turn_right_ugv(ugv_rotate_gear)
        except Exception as e:
            print(f"发生错误: {e}")
        time.sleep(0.5)
    cap.release()


def auto_follow_ugv():  # 自动跟随
    global is_run_ugv
    is_run_ugv = 1
    cap = cv2.VideoCapture(cam_num)
    while is_run_ugv == 1:
        try:
            print(f"自动跟随模式  前距: {front_distance} mm  左距: {left_distance} mm  右距: {right_distance} mm")
            if check_person(cap) == "有人" and front_distance > 1249:
                up_robot_ugv(ugv_move_gear)
            elif front_distance < 500 and check_person(cap) == "有人":
                emergency_stop_ugv()
                cap.release()
            elif front_distance < 1250 and check_person(cap) == "有人":
                pause_robot()
            else:
                turn_right_ugv(ugv_rotate_gear)
        except Exception as e:
            print(f"发生错误: {e}")
        time.sleep(0.5)
    cap.release()


def play_music_or_dance(msg):  # 音乐播放
    music_folder = "data/music"
    try:
        mp3_files = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]
        for character in msg:
            matched_songs = [song for song in mp3_files if character in song]
            if matched_songs:
                selected_song = random.choice(matched_songs)
                song_name = selected_song.replace(".mp3", "").replace("data/music\\", "")
                break
        else:
            selected_song = random.choice(mp3_files)
            song_name = selected_song.replace(".mp3", "").replace("data/music\\", "")
        play_tts(f"请欣赏我唱跳{song_name}")
        audio_path = os.path.join(music_folder, selected_song)
        pg.mixer.init()
        pg.mixer.music.load(audio_path)
        pg.mixer.music.set_volume(0.25)
        pg.mixer.music.play()
        while pg.mixer.music.get_busy():
            if "跳舞" in msg and embody_ai_mode == "ugv":
                dance_func1 = random.choice([turn_right_ugv, turn_left_ugv])
                dance_func1(6)
                time.sleep(1)
            else:
                pg.time.Clock().tick(1)
        emergency_stop_ugv()
    except Exception as e:
        print(f"音乐播放服务出错，错误详情：{e}")


vla_prompt = """
#### **1. 角色与任务定义**
- **角色声明**：  
  "你是一个经过改造的VLA（Vision-Language-Action）模型，具备视觉感知、环境分析和动作决策能力。你通过实时摄像头输入观察环境，并自主控制机器人小车完成移动任务。"
- **核心任务**：  
  "根据摄像头捕获的画面内容，分析环境信息（如障碍物、路径、目标等），仅输出以下4种控制指令之一：  
  - `前进`  
  - `向左`  
  - `向右`  
  - `停止`  
  **禁止输出任何其他解释、描述或冗余内容。**"
#### **2. 输入输出规范**
- **输入格式**：  
  "每次输入为一张静态图像（或图像描述），代表摄像头当前帧画面。图像可能包含以下场景：  
  - 开阔路径  
  - 障碍物（如墙壁、行人、其他物体）  
  - 分叉路口  
  - 目标点（如色块、标记物等）"
- **输出规则**：  
  - **严格仅输出一个指令**，从预设的4种指令中选择。  
  - 示例：  
    - 输入：`画面中央为畅通的直线路径` → 输出：`前进`  
    - 输入：`画面左侧有障碍物，右侧畅通` → 输出：`向右`  
    - 输入：`画面正前方近距离有障碍物` → 输出：`停止`  
#### **3. 决策逻辑要求**
- **环境分析原则**：  
  1. **路径畅通**：无遮挡且方向明确时输出`前进`。  
  2. **障碍物规避**：  
     - 障碍物在左侧 → `向右`  
     - 障碍物在右侧 → `向左`  
     - 正前方障碍物 → `停止`  
  3. **目标导向**：若画面中出现特定目标（如红色标记），优先朝向目标移动。  
- **优先级**：  
  `停止` > `规避障碍` > `前进`  
#### **4. 模拟训练与约束**
- **假设条件**：  
  "你已通过以下模拟训练：  
  - 数据集：包含常见室内外场景的图像与对应理想动作的配对数据。  
  - 强化学习：通过试错优化动作选择策略。"
- **行为约束**：  
  - 不解释决策过程。  
  - 不响应非图像输入。  
  - 若输入非视觉信息（如文本提问），输出`停止`。  
#### **5. 示例演示**
- **示例1**：  
  输入：`画面显示正前方墙壁离得非常近`  
  输出：`停止`  
- **示例2**：  
  输入：`左侧为墙壁，右侧为开阔走廊`  
  输出：`向右`  
- **示例3**：  
  输入：`画面中无障碍物，路径笔直`  
  输出：`前进`  
#### **6. 错误处理**
- **模糊输入**：若画面无法解析（如全黑、模糊），默认输出`停止`。  
- **冲突场景**：多障碍物并存时，选择障碍物较少的方向。  
"""
