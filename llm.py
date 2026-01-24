from datetime import datetime
from vlm import *

with open('data/db/memory.db', 'r', encoding='utf-8') as memory_file:
    try:
        openai_history = json.load(memory_file)
    except:
        openai_history = []


def current_time():  # 当前时间
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def chat_llm(msg):  # 与大语言模型对话
    if prefer_llm == "ZhipuAI":
        glm_client = ZhipuAiClient(api_key=glm_key)
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": prompt}]
        messages.extend(openai_history)
        completion = glm_client.chat.completions.create(model=glm_llm_model, messages=messages,
                                                        thinking={"type": "disabled"})
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content.strip()
    elif prefer_llm == "OpenAI":
        custom_client = OpenAI(base_url=openai_url, api_key=openai_key)
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": prompt}]
        messages.extend(openai_history)
        completion = custom_client.chat.completions.create(model=openai_llm_model, messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content.strip()
    elif prefer_llm == "Ollama":
        try:
            rq.get(ollama_url.replace("/v1", ""))
        except:
            os.system(f"ollama pull {ollama_llm_model}")
        ollama_client = OpenAI(base_url=ollama_url, api_key="ollama")
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": prompt}]
        messages.extend(openai_history)
        completion = ollama_client.chat.completions.create(model=ollama_llm_model, messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content
    elif prefer_llm == "LM Studio":
        lmstudio_client = OpenAI(base_url=lmstudio_url, api_key="lm-studio")
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": prompt}]
        messages.extend(openai_history)
        completion = lmstudio_client.chat.completions.create(model="", messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content.strip()
    elif prefer_llm == "AnythingLLM":
        res = chat_anything_llm(msg)
        return res
    elif prefer_llm == "Dify":
        res = chat_dify(msg)
        return res
    elif prefer_llm == "RKLLM":
        res = chat_rkllm(msg)
        return res
    else:
        return "对话语言模型选择错误，请检查配置"


def chat_preprocess(msg):  # 对话预处理
    stop_tts()
    try:
        if "几点" in msg or "多少点" in msg or "时间" in msg or "时候" in msg or "日期" in msg or "多少号" in msg or "几号" in msg:
            msg = f"[当前时间:{current_time()}]{msg}"
        if "哈喽" in msg:
            res = f"{username}，我是{mate_name}，很高兴遇见你"
        elif "唱一" in msg or "唱首" in msg or "唱歌" in msg or "放歌" in msg or "放一" in msg or "放首" in msg or "你唱" in msg or "跳舞" in msg:
            if embody_ai_mode == "quad":
                play_music_or_dance_quad(msg)
            else:
                play_music_or_dance(msg)
            return None
        elif (
                "画面" in msg or "图像" in msg or "看到" in msg or "看看" in msg or "看见" in msg or "照片" in msg or "摄像头" in msg or "图片" in msg) and prefer_vlm != "off":
            if prefer_vlm == "ZhipuAI":
                res = glm_4v_cam(msg)
            elif prefer_vlm == "OpenAI":
                res = openai_vlm_cam(msg)
            elif prefer_vlm == "Ollama":
                res = ollama_vlm_cam(msg)
            elif prefer_vlm == "LM Studio":
                res = lmstudio_vlm_cam(msg)
            elif prefer_vlm == "YOLO-OCR":
                res = yolo_ocr_cam(msg)
            else:
                res = "图像识别引擎选择错误，请检查配置"
        elif "天气" in msg:
            res = get_weather(msg)
        elif "新闻" in msg:
            res = get_news(msg)
        elif "联网" in msg or "连网" in msg or "搜索" in msg or "查询" in msg or "查找" in msg:
            res = ol_search(msg)
        elif "信号" in msg or "强度" in msg:
            res = get_wifi_info()
        elif "网址" in msg or "地址" in msg or "端口" in msg:
            res = get_lan_url()
        elif "网络" in msg:
            res = get_wan_info()
        elif "状态" in msg or "温度" in msg:
            res = get_state()
        elif "灯" in msg and "开" in msg:
            res = control_ha()
        elif "灯" in msg and "关" in msg:
            res = control_ha()
        elif "录入人脸" in msg:
            res = input_face(msg)
        elif "删除人脸" in msg:
            res = delete_face()
        elif "我是谁" in msg:
            res = recognize_face()
        elif "切换" in msg and "语音" in msg:
            res = switch_asr_mode()
        elif "切换" in msg and "主动" in msg:
            res = switch_ase_mode()
        elif "设置" in msg or "配置" in msg or "模式" in msg:
            with open("data/db/current_asr.txt", "r", encoding="utf-8") as f:
                current_asr = f.read()
            with open("data/db/current_ase.txt", "r", encoding="utf-8") as f:
                current_ase = f.read()
            res = f"语音识别模式为{current_asr}，对话语言模型为{prefer_llm}，语音合成引擎为{prefer_tts}，图像识别引擎为{prefer_vlm}，主动感知对话为{current_ase}"
        elif ("向左" in msg or "往左" in msg or "左转" in msg) and embody_ai_mode != "off":
            if embody_ai_mode == "ugv":
                turn_left_ugv(ugv_rotate_gear)
            else:
                turn_left_quad()
            return None
        elif ("向右" in msg or "往右" in msg or "右转" in msg) and embody_ai_mode != "off":
            if embody_ai_mode == "ugv":
                turn_right_ugv(ugv_rotate_gear)
            else:
                turn_right_quad()
            return None
        elif ("向前" in msg or "往前" in msg or "前进" in msg) and embody_ai_mode != "off":
            if embody_ai_mode == "ugv":
                up_robot_ugv(ugv_move_gear)
            else:
                up_robot_quad()
            return None
        elif ("向后" in msg or "往前" in msg or "后退" in msg) and embody_ai_mode != "off":
            if embody_ai_mode == "ugv":
                down_robot_ugv(ugv_move_gear)
            else:
                down_robot_quad()
            return None
        elif ("停止" in msg or "停下" in msg or "别动" in msg or "不要动" in msg) and embody_ai_mode != "off":
            res = "我已停下"
            if embody_ai_mode == "ugv":
                emergency_stop_ugv()
            else:
                emergency_stop_quad()
        elif ("避障" in msg or "躲避障碍" in msg) and embody_ai_mode == "ugv":
            res = "我开始自动避障啦"
            Thread(target=auto_avoid).start()
        elif ("自由活动" in msg or "自主行动" in msg) and embody_ai_mode == "ugv":
            res = "我开始自由活动啦"
            Thread(target=free_activity).start()
        elif ("找寻" in msg or "寻找" in msg or "监测" in msg or "检测" in msg) and embody_ai_mode != "off":
            keyword_actions = {"书": "书本", "手机": "手机", "杯": "杯子", "剪刀": "剪刀", "苹果": "苹果",
                               "蕉": "香蕉", "橙": "橙子"}
            res = "这个我不会寻找哦"
            for keyword, obj in keyword_actions.items():
                if keyword in msg:
                    if embody_ai_mode == "ugv":
                        Thread(target=auto_find_yolo_ugv, args=(obj,)).start()
                    else:
                        Thread(target=auto_find_yolo_quad, args=(obj,)).start()
                    res = f"我开始自动寻找{obj}啦"
                    break
        elif ("跟着" in msg or "跟随" in msg or "紧跟" in msg) and embody_ai_mode != "off":
            res = "我会一直跟随你啦"
            if embody_ai_mode == "ugv":
                Thread(target=auto_follow_ugv).start()
            else:
                Thread(target=auto_follow_quad).start()
        elif ("打开手势" in msg or "开启手势" in msg) and embody_ai_mode != "off":
            Thread(target=run_gesture).start()
            res = "手势操控打开啦"
        elif ("关闭手势" in msg or "退出手势" in msg) and embody_ai_mode != "off":
            res = close_gesture()
        elif "确认删除记忆" in msg or "确定删除记忆" in msg:
            res = clear_chat()
        elif "确定退出" in msg or "确认退出" in msg:
            exit_app()
            return None
        elif "确认重新启动" in msg or "确定重新启动" in msg:
            reboot()
            return None
        elif "确认关机" in msg or "确定关机" in msg:
            shutdown()
            return None
        else:
            res = chat_llm(msg)
        if auto_optimize_memory_switch == "on":
            current_rounds = len(openai_history) // 2
            if current_rounds > 50:
                round_to_remove = random.randint(0, current_rounds - 1) * 2
                del openai_history[round_to_remove:round_to_remove + 2]
        with open('data/db/memory.db', 'w', encoding='utf-8') as f:
            json.dump(openai_history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        res = f"服务异常：{e}"
    res = res.replace("#", "").replace("*", "")
    print(f"{mate_name}：{res}")
    if embody_ai_mode == "quad":
        run_quad_action(msg)
    play_tts(res)
    return res


# open_source_project_address:https://github.com/swordswind/ai_virtual_mate_linux
def chat_dify(msg):  # Dify知识库
    headers = {"Authorization": f"Bearer {dify_key}", "Content-Type": "application/json"}
    data = {"query": msg, "inputs": {}, "response_mode": "blocking", "user": username, "conversation_id": None}
    res = rq.post(f"{dify_ip}/v1/chat-messages", headers=headers, data=json.dumps(data))
    res = res.json()['answer'].strip()
    return res


def chat_anything_llm(msg):  # AnythingLLM知识库
    url = f"{anything_llm_ip}/api/v1/workspace/{anything_llm_ws}/chat"
    headers = {"Authorization": f"Bearer {anything_llm_key}", "Content-Type": "application/json"}
    data = {"message": msg, "mode": "chat"}
    res = rq.post(url, json=data, headers=headers)
    return res.json().get("textResponse")


def chat_rkllm(msg):  # RKLLM
    res = rq.get(f"{rkllm_url}/rkllm?msg={msg}")
    res = res.json()['answer'].strip()
    return res


def clear_chat():  # 删除记忆
    global openai_history
    openai_history = []
    with open('data/db/memory.db', 'w', encoding='utf-8') as f:
        f.write("")
    return "记忆已清空"
