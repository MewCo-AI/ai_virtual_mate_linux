from rapidocr_openvino import RapidOCR
from gesture import *

cls_model, det_model, ocr = None, None, None
vlm_prompt = prompt + "。你拥有图像识别能力"


def glm_4v_cam(question):  # 多模态摄像头画面聊天
    cap = cv2.VideoCapture(cam_num)
    if not cap.isOpened():
        return "无法打开摄像头"
    ret, frame = cap.read()
    cap.release()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = ZhipuAiClient(api_key=glm_key)
    completion = vlm_client.chat.completions.create(model=glm_vlm_model, messages=messages,
                                                    thinking={"type": "disabled"})
    return completion.choices[0].message.content


def ollama_vlm_cam(question):
    try:
        rq.get(ollama_url.replace("/v1", ""))
    except:
        os.system(f"ollama pull {ollama_vlm_model}")
    cap = cv2.VideoCapture(cam_num)
    if not cap.isOpened():
        return "无法打开摄像头"
    ret, frame = cap.read()
    cap.release()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = OpenAI(base_url=ollama_url, api_key="ollama")
    completion = vlm_client.chat.completions.create(model=ollama_vlm_model, messages=messages)
    return completion.choices[0].message.content


def lmstudio_vlm_cam(question):
    cap = cv2.VideoCapture(cam_num)
    if not cap.isOpened():
        return "无法打开摄像头"
    ret, frame = cap.read()
    cap.release()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = OpenAI(base_url=lmstudio_url, api_key="lm-studio")
    completion = vlm_client.chat.completions.create(model="", messages=messages)
    return completion.choices[0].message.content


def openai_vlm_cam(question):
    cap = cv2.VideoCapture(cam_num)
    if not cap.isOpened():
        return "无法打开摄像头"
    ret, frame = cap.read()
    cap.release()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = OpenAI(base_url=openai_url, api_key=openai_key)
    completion = vlm_client.chat.completions.create(model=openai_vlm_model, messages=messages)
    return completion.choices[0].message.content


# open_source_project_address:https://github.com/MewCo-AI/ai_virtual_mate_linux
def yolo_ocr_cam(question):  # 本地YOLO-OCR-LLM摄像头画面识别理解
    global cls_model, det_model, ocr
    if cls_model is None or det_model is None or ocr is None:
        cls_model = YOLO('data/model/YOLO/yolo11s-cls.pt')
        det_model = YOLO('data/model/YOLO/yolo11s.pt')
        ocr = RapidOCR()
    cap = cv2.VideoCapture(cam_num)
    if not cap.isOpened():
        return "无法打开摄像头"
    ret, frame = cap.read()
    cap.release()
    cls_results = cls_model(frame)
    probs = cls_results[0].probs.data.cpu().numpy()
    names = cls_results[0].names
    top5_indices = probs.argsort()[-5:][::-1]
    scene_detection_result = []
    for cls_index in top5_indices:
        cls_name = names[cls_index]
        cls_conf = probs[cls_index]
        scene_detection_result.append(f"{cls_name},{cls_conf:.2f}")
    scene_detection_result = ";".join(scene_detection_result)
    det_results = det_model(frame)
    object_detection_result = []
    object_count = {}
    for det in det_results[0].boxes:
        det_name = det_results[0].names[int(det.cls)]
        if det_name in object_count:
            object_count[det_name] += 1
        else:
            object_count[det_name] = 1
    for obj_name, count in object_count.items():
        object_detection_result.append(f"{obj_name},{count}个")
    object_detection_result = ";".join(object_detection_result)
    ocr_results, _ = ocr(frame)
    text_detection_result = []
    try:
        for ocr_result in ocr_results:
            text_detection_result.append(ocr_result[1])
    except:
        print("OCR结果为空")
    text_detection_result = "\n".join(text_detection_result)
    if len(text_detection_result) > 0:
        text_detection_result = "文字检测结果:" + text_detection_result
    yolo_ocr_result = f"场景检测结果(场景名称,置信度):{scene_detection_result}\n物体检测结果(物体名称,数量):{object_detection_result}\n{text_detection_result}"
    ollama_client = OpenAI(base_url=ollama_url, api_key="ollama")
    messages = [{"role": "system",
                 "content": "你是一个专业的多模态大模型，请扮演一个有情感的人类和我对话，需要结合你看到的内容回答我的问题，仅需输出推测的场景行为。/no_think"},
                {"role": "user",
                 "content": f"\n{yolo_ocr_result}以上是你看到的内容，不要提及任何英文、置信度，不能拒绝回答我的问题。我的问题是:{question}"}]
    completion = ollama_client.chat.completions.create(model=ollama_llm_model, messages=messages)
    return completion.choices[0].message.content
