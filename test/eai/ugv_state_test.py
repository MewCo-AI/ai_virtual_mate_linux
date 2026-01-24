import time
from serial import Serial

ugv_robot_port = "/dev/ttyACM1"


def parse_data(bytes_list):
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


def print_robot_state():
    while True:
        try:
            ser = Serial(ugv_robot_port, 115200, timeout=0.1)
            line = ser.readline()
            stm32_output = line.hex()[:48]
            ser.close()
            stm32_result = parse_data(stm32_output)
            if stm32_result:
                cell_voltage = stm32_result[8]
                cell_percent = int(((cell_voltage - 20) / (23.5 - 20)) * 99 + 1)
                if cell_percent > 100:
                    cell_percent = 100
                if cell_percent < 0:
                    cell_percent = 0
                print("\n=== 机器人状态 ===")
                print(f"电池电量: {cell_percent} %")
                print(f"X速度: {stm32_result[0]:.3f} m/s")
                print(f"Y速度: {stm32_result[1]:.3f} m/s")
                print(f"X加速度: {stm32_result[2]:.3f} m/s²")
                print(f"Y加速度: {stm32_result[3]:.3f} m/s²")
                print(f"Z加速度: {stm32_result[4]:.3f} m/s²")
                print(f"X角速度: {stm32_result[5]:.3f} °/s")
                print(f"Y角速度: {stm32_result[6]:.3f} °/s")
                print(f"Z角速度: {stm32_result[7]:.3f} °/s")
        except Exception as e:
            print(f"四轮机器人未连接或串口编号设置错误，请修改ugv_robot_port，错误详情：{e}")
            exit()
        time.sleep(1)


print_robot_state()
