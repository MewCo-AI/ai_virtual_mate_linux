import time
from serial import Serial

ugv_robot_port = '/dev/ttyACM1'
move_gear = 2
rotate_gear = 3


def send_serial_ugv(msg):
    try:
        ser = Serial(ugv_robot_port, 115200, timeout=0.1)
        data = bytes.fromhex(msg)
        ser.write(data)
        ser.close()
    except Exception as e:
        print("四轮机器人未连接或串口编号设置错误，请修改ugv_robot_port，错误详情：", e)


def turn_left_ugv(gear):
    gear_hex_map = {6: "7B 00 00 00 00 00 00 01 2C 56 7D", 5: "7B 00 00 00 00 00 00 00 FA 81 7D",
                    4: "7B 00 00 00 00 00 00 00 C8 B3 7D", 3: "7B 00 00 00 00 00 00 00 96 ED 7D",
                    2: "7B 00 00 00 00 00 00 00 64 1F 7D", 1: "7B 00 00 00 00 00 00 00 32 49 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    send_serial_ugv(hex_data)
    print("机器人逆时针旋转")


def turn_right_ugv(gear):
    gear_hex_map = {6: "7B 00 00 00 00 00 00 FE D4 51 7D", 5: "7B 00 00 00 00 00 00 FF 06 82 7D",
                    4: "7B 00 00 00 00 00 00 FF 38 BC 7D", 3: "7B 00 00 00 00 00 00 FF 6A EE 7D",
                    2: "7B 00 00 00 00 00 00 FF 9C 18 7D", 1: "7B 00 00 00 00 00 00 FF CE 4A 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    send_serial_ugv(hex_data)
    print("机器人顺时针旋转")


def up_robot_ugv(gear):
    gear_hex_map = {6: "7B 00 00 01 2C 00 00 00 00 56 7D", 5: "7B 00 00 00 FA 00 00 00 00 81 7D",
                    4: "7B 00 00 00 C8 00 00 00 00 B3 7D", 3: "7B 00 00 00 96 00 00 00 00 ED 7D",
                    2: "7B 00 00 00 64 00 00 00 00 1F 7D", 1: "7B 00 00 00 32 00 00 00 00 49 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    send_serial_ugv(hex_data)
    print("机器人前进")


def down_robot_ugv(gear):
    gear_hex_map = {6: "7B 00 00 FE D4 00 00 00 00 51 7D", 5: "7B 00 00 FF 06 00 00 00 00 82 7D",
                    4: "7B 00 00 FF 38 00 00 00 00 BC 7D", 3: "7B 00 00 FF 6A 00 00 00 00 EE 7D",
                    2: "7B 00 00 FF 9C 00 00 00 00 18 7D", 1: "7B 00 00 FF CE 00 00 00 00 4A 7D"}
    hex_data = gear_hex_map.get(gear, "Gear Error")
    send_serial_ugv(hex_data)
    print("机器人后退")


def emergency_stop_ugv():
    send_serial_ugv('7B 00 00 00 00 00 00 00 00 7B 7D')
    print("机器人停止成功")


while True:
    command = input("请输入命令（w: 前进, s: 后退, a: 左转, d: 右转, q: 急停）：")
    if command == 'w':
        up_robot_ugv(move_gear)
    elif command == 's':
        down_robot_ugv(move_gear)
    elif command == 'a':
        turn_left_ugv(rotate_gear)
    elif command == 'd':
        turn_right_ugv(rotate_gear)
    elif command == 'q':
        emergency_stop_ugv()
    else:
        print("无效的命令，请重新输入。")
    time.sleep(0.1)
