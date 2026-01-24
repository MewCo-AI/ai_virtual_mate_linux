from sport_ugv import *

run_ges = 0


def run_gesture():  # 手势控制
    def get_finger_direction():  # 用于检测手指方向的辅助函数
        finger_tips = [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP,
                       mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP,
                       mp_hands.HandLandmark.PINKY_TIP]
        if hand_landmarks:  # 获取各个指尖的坐标
            thumb_tip = hand_landmarks.landmark[finger_tips[0]]
            index_tip = hand_landmarks.landmark[finger_tips[1]]
            middle_tip = hand_landmarks.landmark[finger_tips[2]]
            thumb_tip_x, thumb_tip_y = thumb_tip.x, thumb_tip.y
            index_tip_x, index_tip_y = index_tip.x, index_tip.y
            middle_tip_x, middle_tip_y = middle_tip.x, middle_tip.y
            # 判断手势并执行操作
            if index_tip_y < thumb_tip_y and middle_tip_y < thumb_tip_y:  # 张开左手全部手指，面对镜头
                emergency_stop_ugv()
            else:
                if abs(index_tip_x - thumb_tip_x) > abs(index_tip_y - thumb_tip_y):
                    if index_tip_x > thumb_tip_x:
                        if embody_ai_mode == "ugv":
                            turn_right_ugv(ugv_rotate_gear)
                        else:
                            turn_right_quad()
                    else:
                        if embody_ai_mode == "ugv":
                            turn_left_ugv(ugv_rotate_gear)
                        else:
                            turn_left_quad()
                else:
                    if index_tip_y > thumb_tip_y:
                        if embody_ai_mode == "ugv":
                            down_robot_ugv(ugv_move_gear)
                        else:
                            down_robot_quad()
                    else:
                        if embody_ai_mode == "ugv":
                            up_robot_ugv(ugv_move_gear)
                        else:
                            up_robot_quad()

    global run_ges
    mp_hands = mp.solutions.hands  # 初始化MediaPipe手部检测模块
    # 设置MediaPipe手部检测的参数
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7,
                           min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(cam_num)
    run_ges = 1
    while run_ges == 1:
        ret, frame = cap.read()  # 读取视频帧
        if not ret:
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 转换为RGB格式
        results = hands.process(rgb_frame)
        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                get_finger_direction()  # 获取手指方向
        time.sleep(0.1)
    cap.release()


# open_source_project_address:https://github.com/swordswind/ai_virtual_mate_linux
def close_gesture():  # 关闭手势控制
    global run_ges
    run_ges = 0
    return "手势操控已关闭"
