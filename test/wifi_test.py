import time
import pywifi

net_num = 1
wifi = pywifi.PyWiFi()
try:
    iface = wifi.interfaces()[net_num]
except:
    print("未连接无线网卡或网卡编号设置错误，可前往本文件wifi_test.py第4行修改net_num(该情况不影响正常使用)")


def get_wifi_signal_strength():
    try:
        if iface.status() == pywifi.const.IFACE_CONNECTED:
            iface.scan()
            time.sleep(1)
            scan_results = iface.scan_results()
            result = scan_results[0]
            signal = result.signal
            if signal >= -25:
                signal_percent = 100
            elif signal <= -95:
                signal_percent = 0
            else:
                signal_percent = int((signal - (-95)) / ((-25) - (-95)) * 100)
            print(f"信号强度{signal_percent}%")
        else:
            print("WiFi已开启，但未连接")
    except:
        print("WiFi未开启")


get_wifi_signal_strength()
