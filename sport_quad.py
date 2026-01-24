import random
from threading import Thread
from serial import Serial
from function import *

quad_voltage, quad_battery_percent = 0, 0
is_run_quad = 1
if embody_ai_mode == "quad":
    try:
        quad_ser = Serial(quad_robot_port, baudrate=115200)
    except Exception as e1:
        print(f"无法打开四足机器人串口: {e1}")


def send_quad_msg(msg):
    try:
        quad_ser.write((str(msg) + "\n").encode())
    except:
        pass


def turn_left_quad():
    send_quad_msg({"T": 111, "FB": 0, "LR": -1})
    display_quad("Sport: Left")


def turn_right_quad():
    send_quad_msg({"T": 111, "FB": 0, "LR": 1})
    display_quad("Sport: Right")


def up_robot_quad():
    send_quad_msg({"T": 111, "FB": 1, "LR": 0})
    display_quad("Sport: Up")


def down_robot_quad():
    send_quad_msg({"T": 111, "FB": -1, "LR": 0})
    display_quad("Sport: Down")


def emergency_stop_quad():
    global is_run_quad
    is_run_quad = 0
    send_quad_msg({"T": 111, "FB": 0, "LR": 0})
    display_quad("Sport: Stop")


def display_quad(text):
    send_quad_msg({"T": 202, "line": 2, "text": text, "update": 1})


def display_quad_state(text):
    send_quad_msg({"T": 202, "line": 1, "text": text, "update": 1})


def run_quad_action(msg):
    msg = msg.replace(prompt, "")
    if "蹲" in msg or "坐" in msg:
        display_quad("Action: StayLow")
        send_quad_msg({"T": 112, "func": 1})
    elif "手" in msg or "足" in msg or "脚" in msg:
        display_quad("Action: HandShake")
        send_quad_msg({"T": 112, "func": 2})
    elif "跳" in msg:
        display_quad("Action: Jump")
        send_quad_msg({"T": 112, "func": 3})


def get_quad_cell_percent():
    try:
        res = quad_ser.readline().decode()
        data = json.loads(res)
        voltage = data.get("v")
        if voltage is not None:
            percentage = int(max(0, min(100, (voltage - 6.0) / 2.3 * 100)))
            return voltage, percentage
        else:
            print("未找到四足机器人电压数据")
            return 0, 0
    except:
        return 0, 0


# open_source_project_address:https://github.com/swordswind/ai_virtual_mate_linux
def get_quad_cell_percent_th():
    global quad_voltage, quad_battery_percent
    time.sleep(2)
    while True:
        quad_voltage, quad_battery_percent = get_quad_cell_percent()
        time.sleep(2)


def refresh_quad_screen():
    while True:
        time.sleep(2)
        current_time = time.strftime("%H:%M", time.localtime())
        display_quad_state(f"{current_time} Battery:{quad_battery_percent}%")


def get_current_state():
    return quad_voltage, quad_battery_percent


def auto_find_yolo_quad(obj):
    global is_run_quad
    is_run_quad = 1
    cap = cv2.VideoCapture(cam_num)
    while is_run_quad == 1:
        try:
            if check_yolo(obj, cap) is True:
                up_robot_quad()
            else:
                turn_right_quad()
        except Exception as e:
            print(f"发生错误: {e}")
        time.sleep(0.5)
    cap.release()


def auto_follow_quad():
    global is_run_quad
    is_run_quad = 1
    cap = cv2.VideoCapture(cam_num)
    while is_run_quad == 1:
        try:
            if check_person(cap) == "有人":
                up_robot_quad()
            else:
                turn_right_quad()
        except Exception as e:
            print(f"发生错误: {e}")
        time.sleep(0.5)
    cap.release()


def play_music_or_dance_quad(msg):  # 音乐播放
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
            if "跳舞" in msg:
                dance_func1 = random.choice([turn_right_quad, turn_left_quad])
                dance_func1()
                time.sleep(1)
            else:
                pg.time.Clock().tick(1)
        emergency_stop_quad()
    except Exception as e:
        print(f"音乐播放服务出错，错误详情：{e}")


if embody_ai_mode == "quad":
    display_quad("Aivmate LX3 Quad")
    Thread(target=get_quad_cell_percent_th).start()
    Thread(target=refresh_quad_screen).start()
