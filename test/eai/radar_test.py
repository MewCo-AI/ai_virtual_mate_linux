import os
import time
from threading import Thread
from serial import Serial

ugv_radar_port = "/dev/ttyACM0"


def parse_data(data):  # 定义一个函数来解析数据包
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


def radar_detect():
    global last_angle
    try:
        ser = Serial(ugv_radar_port, 460800, timeout=5)
    except Exception as e:
        ser = None
        print("激光雷达未连接或串口编号设置错误，请修改ugv_radar_port，错误详情：", e)
        os.kill(os.getpid(), 15)
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


front_distance, right_distance, left_distance = 0, 0, 0
Thread(target=radar_detect).start()
while True:
    time.sleep(1)
    print(f"前距：{front_distance} mm，左距：{left_distance} mm，右距：{right_distance} mm")
