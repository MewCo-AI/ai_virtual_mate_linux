import json
import time
from serial import Serial

quad_robot_port = "/dev/ttyUSB0"
try:
    quad_ser = Serial(quad_robot_port, baudrate=115200)
except Exception as e1:
    print(f"无法打开四足机器人串口: {e1}")
quad_voltage, quad_battery_percent = 0, 0


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
    except Exception as e:
        print(f"四足机器人电量解析发生错误: {e}")
        return 0, 0


def get_quad_cell_percent_th():
    global quad_voltage, quad_battery_percent
    time.sleep(2)
    while True:
        quad_voltage, quad_battery_percent = get_quad_cell_percent()
        print(f"四足机器人电压：{quad_voltage:.2f}V, 电量：{quad_battery_percent}%")
        time.sleep(2)


get_quad_cell_percent_th()
