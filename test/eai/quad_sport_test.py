import time
from serial import Serial

quad_robot_port = '/dev/ttyUSB0'
try:
    quad_ser = Serial(quad_robot_port, baudrate=115200)
except Exception as e1:
    print(f"无法打开四足机器人串口: {e1}")


def send_quad_msg(msg):
    try:
        quad_ser.write((str(msg) + "\n").encode())
    except Exception as e:
        print(f"四足机器人串口发送错误: {e}")


def display_quad(text):
    send_quad_msg({"T": 202, "line": 2, "text": text, "update": 1})


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
    send_quad_msg({"T": 111, "FB": 0, "LR": 0})
    display_quad("Sport: Stop")


display_quad("Aivmate LX3 Quad")
while True:
    command = input("请输入命令（w: 前进, s: 后退, a: 左转, d: 右转, q: 急停）：")
    if command == 'w':
        up_robot_quad()
    elif command == 's':
        down_robot_quad()
    elif command == 'a':
        turn_left_quad()
    elif command == 'd':
        turn_right_quad()
    elif command == 'q':
        emergency_stop_quad()
    else:
        print("无效的命令，请重新输入。")
    time.sleep(0.1)
