import json
import logging
import socket
from flask import Flask, render_template_string, request, jsonify, send_from_directory

app5 = Flask(__name__, static_folder='dist')
logging.getLogger('werkzeug').setLevel(logging.ERROR)
CONFIG_FILE = 'data/db/config.json'
DEFAULT_CONFIG_FILE = 'data/db/config_default.json'


def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置失败，将使用默认配置文件，错误详情: {e}")
        with open(DEFAULT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)


def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存设置失败，错误详情: {e}")
        return False


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/png" href="assets/image/logo.png"/>
    <title>系统设置 - Aivmate LX3</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #001f3f;
            color: white;
            margin: 0;
            padding: 0;
            line-height: 1.6;
            height: 100vh;
            overflow-x: hidden;
        }
        .container {
            width: 99%;
            max-width: 100%;
            min-height: 100vh;
            margin: 0;
            background-color: #003366;
            padding: 20px;
            border-radius: 0;
            box-sizing: border-box;
            box-shadow: none;
        }
        @media screen and (max-width: 768px) {
            .tabs {
                flex-wrap: wrap;
                border-bottom: none;
            }
            .tab {
                flex: 1 1 calc(33.33% - 5px);
                margin-right: 0;
                margin-bottom: 5px;
                text-align: center;
                font-size: 14px;
                padding: 8px 5px;
            }
            .form-group {
                margin-bottom: 12px;
            }
            input, select, textarea {
                font-size: 14px;
                padding: 10px;
            }
            h1 {
                font-size: 1.5rem;
                padding: 10px 0;
                margin-bottom: 15px;
            }
            .section h2 {
                font-size: 1.2rem;
            }
            button {
                width: 100%;
                padding: 12px 0;
                font-size: 16px;
            }
            .notification {
                top: 10px;
                right: 10px;
                left: 10px;
                text-align: center;
                padding: 12px;
            }
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            color: #ffffff;
        }
        .section {
            margin-bottom: 30px;
            padding: 15px;
            background-color: #004080;
            border-radius: 8px;
        }
        .section h2 {
            margin-top: 0;
            color: #66b3ff;
            border-bottom: 1px solid #0066cc;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select, textarea {
            width: 99%;
            padding: 8px;
            background-color: #0055aa;
            border: 1px solid #0077dd;
            border-radius: 4px;
            color: white;
        }
        input[type="number"] {
            width: 100px;
        }
        button {
            background-color: #0077dd;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background-color: #0099ff;
        }
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            display: none;
            z-index: 1000;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #0066cc;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            background-color: #004080;
            border: 1px solid #0066cc;
            border-bottom: none;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
            font-size: 13px;
        }
        .tab.active {
            background-color: #0055aa;
            color: #ffffff;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><img src="assets/image/logo.png" alt="Logo" style="width: 25px; height: 25px; margin-right: 5px;">系统设置</h1>
        <div class="tabs">
            <div class="tab active" data-tab="ai-engine">🤖AI引擎</div>
            <div class="tab" data-tab="basic-info">ℹ️基本信息</div>
            <div class="tab" data-tab="zhipuai">🔷ZhipuAI</div>
            <div class="tab" data-tab="openai">🔧自定义OpenAI兼容</div>
            <div class="tab" data-tab="ollama">🦙Ollama和LM Studio</div>
            <div class="tab" data-tab="speech-recognition">🎙️语音识别</div>
            <div class="tab" data-tab="voiceprint">👂声纹识别</div>
            <div class="tab" data-tab="tts">🔊语音合成</div>
            <div class="tab" data-tab="image-recognition">📸图像识别</div>
            <div class="tab" data-tab="knowledge-base">📚知识库</div>
            <div class="tab" data-tab="home-assistant">🏠Home Assistant</div>
            <div class="tab" data-tab="robot">🦾具身机器人</div>
            <div class="tab" data-tab="other">⚙️其他设置</div>
        </div>
        <form id="config-form">
            <div class="tab-content active" id="ai-engine">
                <div class="section">
                    <h2>AI引擎选择</h2>
                    <div class="form-group">
                        <label for="prefer_asr">语音识别模式(ASR)</label>
                        <select id="prefer_asr" name="prefer_asr">
                            <option value="RealTime">RealTime(实时语音识别)</option>
                            <option value="WakeWord">WakeWord(自定义唤醒词)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="prefer_llm">对话语言模型(LLM)</label>
                        <select id="prefer_llm" name="prefer_llm">
                            <option value="ZhipuAI">ZhipuAI(云端)</option>
                            <option value="OpenAI">OpenAI(自定义)</option>
                            <option value="Ollama">Ollama(本地/局域网)</option>
                            <option value="LM Studio">LM Studio(局域网)</option>
                            <option value="AnythingLLM">AnythingLLM(局域网)</option>
                            <option value="Dify">Dify(本地/局域网)</option>
                            <option value="RKLLM">RKLLM(本地)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="prefer_tts">语音合成引擎(TTS)</label>
                        <select id="prefer_tts" name="prefer_tts">
                            <option value="edge-tts">edge-tts(云端)</option>
                            <option value="VITS">VITS(本地内置)</option>
                            <option value="GPT-SoVITS">GPT-SoVITS(局域网)</option>
                            <option value="CosyVoice">CosyVoice(局域网)</option>
                            <option value="Qwen-TTS">Qwen-TTS(局域网)</option>
                            <option value="VoxCPM">VoxCPM(局域网)</option>
                            <option value="Index-TTS">Index-TTS(局域网)</option>
                            <option value="CustomTTS">CustomTTS(自定义)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="prefer_vlm">图像识别引擎(VLM)</label>
                        <select id="prefer_vlm" name="prefer_vlm">
                            <option value="ZhipuAI">ZhipuAI(云端)</option>
                            <option value="OpenAI">OpenAI(自定义)</option>
                            <option value="Ollama">Ollama(本地/局域网)</option>
                            <option value="LM Studio">LM Studio(局域网)</option>
                            <option value="YOLO-OCR">YOLO-OCR(本地)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="prefer_ase">主动感知对话</label>
                        <select id="prefer_ase" name="prefer_ase">
                            <option value="on">on(开启)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="tab-content" id="basic-info">
                <div class="section">
                    <h2>基本信息设置</h2>
                    <div class="form-group">
                        <label for="username">用户名</label>
                        <input type="text" id="username" name="username">
                    </div>
                    <div class="form-group">
                        <label for="mate_name">虚拟伙伴名称</label>
                        <input type="text" id="mate_name" name="mate_name">
                    </div>
                    <div class="form-group">
                        <label for="prompt">虚拟伙伴人设(对于思考模型,如需提升回答速度可在结尾添加/no_think)</label>
                        <textarea id="prompt" name="prompt" rows="10"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="vrm_model_name">VRM 3D模型名称(存放于dist/assets/vrm_model文件夹)</label>
                        <input type="text" id="vrm_model_name" name="vrm_model_name">
                    </div>
                    <div class="form-group">
                        <label>Live2D模型<br>存放于dist/assets/live2d_model文件夹<br>可修改dist/assets/live2d.js进行更换<br>根据需求修改模型路径、模型坐标、模型大小参数</label>
                    </div>
                    <div class="form-group">
                        <label>MMD 3D模型和动作<br>分别存放于dist/assets/mmd_model和mmd_action文件夹<br>可分别修改dist/assets/mmd.js和mmd_vmd.js进行更换<br>根据需求修改模型路径、表情索引、动作路径参数</label>
                    </div>
                </div>
            </div>
            <div class="tab-content" id="speech-recognition">
                <div class="section">
                    <h2>语音识别设置</h2>
                    <div class="form-group">
                        <label for="speech_end_wait_time">语音识别结束等待秒数(>0.1)</label>
                        <input type="number" step="0.1" id="speech_end_wait_time" name="speech_end_wait_time">
                    </div>
                    <div class="form-group">
                        <label for="wake_word">唤醒词(推荐设置为常用的词汇)</label>
                        <input type="text" id="wake_word" name="wake_word">
                    </div>
                    <div class="form-group">
                        <label for="mic_num">麦克风编号</label>
                        <input type="number" id="mic_num" name="mic_num">
                    </div>
                    <div class="form-group">
                        <label for="sound_sense_switch">音频事件检测开关</label>
                        <select id="sound_sense_switch" name="sound_sense_switch">
                            <option value="on">on(开启)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="sound_sense_threshold">音频事件检测阈值(0.1~0.9)</label>
                        <input type="number" step="0.1" id="sound_sense_threshold" name="sound_sense_threshold">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="voiceprint">
                <div class="section">
                    <h2>声纹识别设置</h2>
                    <div class="form-group">
                        <label for="voiceprint_switch">声纹识别开关(开启前需将声纹文件放入指定路径)</label>
                        <select id="voiceprint_switch" name="voiceprint_switch">
                            <option value="on">on(开启)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="voiceprint_threshold">声纹识别阈值(0.1~0.9)</label>
                        <input type="number" step="0.1" id="voiceprint_threshold" name="voiceprint_threshold">
                    </div>
                    <div class="form-group">
                        <label for="myvoice_path">用户声纹文件路径</label>
                        <input type="text" id="myvoice_path" name="myvoice_path">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="zhipuai">
                <div class="section">
                    <h2>ZhipuAI设置</h2>
                    <div class="form-group">
                        <label for="glm_key">ZhipuAI密钥api_key(从BigModel平台获取)</label>
                        <input type="password" id="glm_key" name="glm_key">
                    </div>
                    <div class="form-group">
                        <label for="glm_llm_model">ZhipuAI大语言模型llm-model</label>
                        <input type="text" id="glm_llm_model" name="glm_llm_model">
                    </div>
                    <div class="form-group">
                        <label for="glm_vlm_model">ZhipuAI视觉语言模型vlm-model</label>
                        <input type="text" id="glm_vlm_model" name="glm_vlm_model">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="openai">
                <div class="section">
                    <h2>OpenAI兼容设置(自定义API)</h2>
                    <div class="form-group">
                        <label for="openai_url">OpenAI兼容地址base_url</label>
                        <input type="text" id="openai_url" name="openai_url">
                    </div>
                    <div class="form-group">
                        <label for="openai_key">OpenAI兼容密钥api_key</label>
                        <input type="password" id="openai_key" name="openai_key">
                    </div>
                    <div class="form-group">
                        <label for="openai_llm_model">OpenAI兼容大语言模型llm-model</label>
                        <input type="text" id="openai_llm_model" name="openai_llm_model">
                    </div>
                    <div class="form-group">
                        <label for="openai_vlm_model">OpenAI兼容视觉语言模型vlm-model</label>
                        <input type="text" id="openai_vlm_model" name="openai_vlm_model">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="ollama">
                <div class="section">
                    <h2>Ollama和LM Studio设置</h2>
                    <div class="form-group">
                        <label for="ollama_url">Ollama地址base_url</label>
                        <input type="text" id="ollama_url" name="ollama_url">
                    </div>
                    <div class="form-group">
                        <label for="ollama_llm_model">Ollama大语言模型llm-model</label>
                        <input type="text" id="ollama_llm_model" name="ollama_llm_model">
                    </div>
                    <div class="form-group">
                        <label for="ollama_vlm_model">Ollama视觉语言模型vlm-model</label>
                        <input type="text" id="ollama_vlm_model" name="ollama_vlm_model">
                    </div>
                    <div class="form-group">
                        <label for="lmstudio_url">LM Studio地址base_url</label>
                        <input type="text" id="lmstudio_url" name="lmstudio_url">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="knowledge-base">
                <div class="section">
                    <h2>知识库设置</h2>
                    <div class="form-group">
                        <label for="anything_llm_ip">AnythingLLM地址</label>
                        <input type="text" id="anything_llm_ip" name="anything_llm_ip">
                    </div>
                    <div class="form-group">
                        <label for="anything_llm_ws">AnythingLLM工作区</label>
                        <input type="text" id="anything_llm_ws" name="anything_llm_ws">
                    </div>
                    <div class="form-group">
                        <label for="anything_llm_key">AnythingLLM密钥</label>
                        <input type="text" id="anything_llm_key" name="anything_llm_key">
                    </div>
                    <div class="form-group">
                        <label for="dify_ip">Dify地址</label>
                        <input type="text" id="dify_ip" name="dify_ip">
                    </div>
                    <div class="form-group">
                        <label for="dify_key">Dify密钥</label>
                        <input type="text" id="dify_key" name="dify_key">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="tts">
                <div class="section">
                    <h2>语音合成设置</h2>
                    <div class="form-group">
                        <label for="stream_tts_switch">流式语音合成开关</label>
                        <select id="stream_tts_switch" name="stream_tts_switch">
                            <option value="on">on(开启)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="edge_speaker">edge-tts音色</label>
                            <select id="edge_speaker" name="edge_speaker">
                                <option value="zh-CN-XiaoyiNeural">zh-CN-XiaoyiNeural(晓艺-年轻女声)</option>
                                <option value="zh-CN-XiaoxiaoNeural">zh-CN-XiaoxiaoNeural(晓晓-成稳女声)</option>
                                <option value="zh-CN-YunjianNeural">zh-CN-YunjianNeural(云健-大型纪录片男声)</option>
                                <option value="zh-CN-YunxiNeural">zh-CN-YunxiNeural(云希-短视频热门男声)</option>
                                <option value="zh-CN-YunxiaNeural">zh-CN-YunxiaNeural(云夏-年轻男声)</option>
                                <option value="zh-CN-YunyangNeural">zh-CN-YunyangNeural(云扬-成稳男声)</option>
                                <option value="zh-CN-liaoning-XiaobeiNeural">zh-CN-liaoning-XiaobeiNeural(晓北-辽宁话女声)</option>
                                <option value="zh-CN-shaanxi-XiaoniNeural">zh-CN-shaanxi-XiaoniNeural(晓妮-陕西话女声)</option>
                                <option value="zh-HK-HiuGaaiNeural">zh-HK-HiuGaaiNeural(晓佳-粤语成稳女声)</option>
                                <option value="zh-HK-HiuMaanNeural">zh-HK-HiuMaanNeural(晓满-粤语年轻女声)</option>
                                <option value="zh-HK-WanLungNeural">zh-HK-WanLungNeural(云龙-粤语男声)</option>
                                <option value="zh-TW-HsiaoChenNeural">zh-TW-HsiaoChenNeural(晓辰-台湾话年轻女声)</option>
                                <option value="zh-TW-HsiaoYuNeural">zh-TW-HsiaoYuNeural(晓宇-台湾话成稳女声)</option>
                                <option value="zh-TW-YunJheNeural">zh-TW-YunJheNeural(云哲-台湾话男声)</option>
                                <option value="ja-JP-KeitaNeural">ja-JP-KeitaNeural(佳太-日语男声)</option>
                                <option value="ja-JP-NanamiNeural">ja-JP-NanamiNeural(七海-日语女声)</option>
                            </select>
                    </div>
                    <div class="form-group">
                        <label for="edge_rate">edge-tts语速</label>
                        <input type="text" id="edge_rate" name="edge_rate">
                    </div>
                    <div class="form-group">
                        <label for="edge_pitch">edge-tts音高</label>
                        <input type="text" id="edge_pitch" name="edge_pitch">
                    </div>
                    <div class="form-group">
                        <label for="vits_model_name">VITS-ONNX模型名称(存放于data/model/TTS文件夹)</label>
                        <input type="text" id="vits_model_name" name="vits_model_name">
                    </div>
                    <div class="form-group">
                        <label for="gsv_api">GPT-SoVITS地址</label>
                        <input type="text" id="gsv_api" name="gsv_api">
                    </div>
                    <div class="form-group">
                        <label for="gsv_prompt">GPT-SoVITS参考音频文本</label>
                        <input type="text" id="gsv_prompt" name="gsv_prompt">
                    </div>
                    <div class="form-group">
                        <label for="gsv_ref_audio_path">GPT-SoVITS参考音频路径</label>
                        <input type="text" id="gsv_ref_audio_path" name="gsv_ref_audio_path">
                    </div>
                    <div class="form-group">
                        <label for="gsv_prompt_lang">GPT-SoVITS参考音频语言</label>
                        <input type="text" id="gsv_prompt_lang" name="gsv_prompt_lang">
                    </div>
                    <div class="form-group">
                        <label for="gsv_lang">GPT-SoVITS合成输出语言</label>
                        <input type="text" id="gsv_lang" name="gsv_lang">
                    </div>
                    <div class="form-group">
                        <label for="cosy_api">CosyVoice地址</label>
                        <input type="text" id="cosy_api" name="cosy_api">
                    </div>
                    <div class="form-group">
                        <label for="qwentts_api">Qwen-TTS地址</label>
                        <input type="text" id="qwentts_api" name="qwentts_api">
                    </div>
                    <div class="form-group">
                        <label for="voxcpm_api">VoxCPM地址</label>
                        <input type="text" id="voxcpm_api" name="voxcpm_api">
                    </div>
                    <div class="form-group">
                        <label for="index_api">Index-TTS地址</label>
                        <input type="text" id="index_api" name="index_api">
                    </div>
                    <div class="form-group">
                        <label for="custom_tts_url">自定义TTS地址</label>
                        <input type="text" id="custom_tts_url" name="custom_tts_url">
                    </div>
                    <div class="form-group">
                        <label for="custom_tts_model">自定义TTS模型</label>
                        <input type="text" id="custom_tts_model" name="custom_tts_model">
                    </div>
                    <div class="form-group">
                        <label for="custom_tts_voice">自定义TTS音色</label>
                        <input type="text" id="custom_tts_voice" name="custom_tts_voice">
                    </div>
                    <div class="form-group">
                        <label for="custom_tts_key">自定义TTS密钥</label>
                        <input type="password" id="custom_tts_key" name="custom_tts_key">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="image-recognition">
                <div class="section">
                    <h2>图像识别设置</h2>
                    <div class="form-group">
                        <label for="cam_num">摄像头编号</label>
                        <input type="number" id="cam_num" name="cam_num">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="home-assistant">
                <div class="section">
                    <h2>Home Assistant智能家居设置</h2>
                    <div class="form-group">
                        <label for="ha_api">Home Assistant地址</label>
                        <input type="text" id="ha_api" name="ha_api">
                    </div>
                    <div class="form-group">
                        <label for="ha_key">Home Assistant长期访问令牌</label>
                        <input type="text" id="ha_key" name="ha_key">
                    </div>
                    <div class="form-group">
                        <label for="entity_id">Home Assistant实体ID(支持按钮类,button开头)</label>
                        <input type="text" id="entity_id" name="entity_id">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="other">
                <div class="section">
                    <h2>其他设置</h2>
                    <div class="form-group">
                        <label for="net_num">无线网卡编号(该设置不影响正常使用)</label>
                        <input type="number" id="net_num" name="net_num">
                    </div>
                    <div class="form-group">
                        <label for="router_ip">路由器IP(该设置不影响正常使用)</label>
                        <input type="text" id="router_ip" name="router_ip">
                    </div>
                    <div class="form-group">
                        <label for="weather_city">天气城市</label>
                        <input type="text" id="weather_city" name="weather_city">
                    </div>
                    <div class="form-group">
                        <label for="rkllm_url">RKLLM地址</label>
                        <input type="text" id="rkllm_url" name="rkllm_url">
                    </div>
                    <div class="form-group">
                        <label for="auto_optimize_memory_switch">自动优化记忆开关</label>
                        <select id="auto_optimize_memory_switch" name="auto_optimize_memory_switch">
                            <option value="on">on(开启)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="welcome_voice_switch">欢迎语开关</label>
                        <select id="welcome_voice_switch" name="welcome_voice_switch">
                            <option value="on">on(开启)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="state_port">主机状态网页端口</label>
                        <input type="number" id="state_port" name="state_port">
                    </div>
                    <div class="form-group">
                        <label for="live2d_port">Live2D角色网页端口</label>
                        <input type="number" id="live2d_port" name="live2d_port">
                    </div>
                    <div class="form-group">
                        <label for="mmd_port">MMD 3D角色网页端口</label>
                        <input type="number" id="mmd_port" name="mmd_port">
                    </div>
                    <div class="form-group">
                        <label for="vrm_port">VRM 3D角色网页端口</label>
                        <input type="number" id="vrm_port" name="vrm_port">
                    </div>
                </div>
            </div>
            <div class="tab-content" id="robot">
                <div class="section">
                    <h2>具身机器人设置</h2>
                    <div class="form-group">
                        <label for="embody_ai_mode">具身智能模式</label>
                        <select id="embody_ai_mode" name="embody_ai_mode">
                            <option value="ugv">ugv(四轮机器人)</option>
                            <option value="quad">quad(四足机器人)</option>
                            <option value="off">off(关闭)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="ugv_radar_port">四轮机器人激光雷达串口号</label>
                        <input type="text" id="ugv_radar_port" name="ugv_radar_port">
                    </div>
                    <div class="form-group">
                        <label for="ugv_robot_port">四轮机器人串口号</label>
                        <input type="text" id="ugv_robot_port" name="ugv_robot_port">
                    </div>
                    <div class="form-group">
                        <label for="ugv_move_gear">四轮机器人移动档位(1~6)</label>
                        <input type="number" id="ugv_move_gear" name="ugv_move_gear" min="1" max="6">
                    </div>
                    <div class="form-group">
                        <label for="ugv_rotate_gear">四轮机器人旋转档位(1~6)</label>
                        <input type="number" id="ugv_rotate_gear" name="ugv_rotate_gear" min="1" max="6">
                    </div>
                    <div class="form-group">
                        <label for="control_ugv_port">四轮机器人控制网页端口</label>
                        <input type="number" id="control_ugv_port" name="control_ugv_port">
                    </div>
                    <div class="form-group">
                        <label for="quad_robot_port">四足机器人串口号</label>
                        <input type="text" id="quad_robot_port" name="quad_robot_port">
                    </div>
                    <div class="form-group">
                        <label for="control_quad_port">四足机器人控制网页端口</label>
                        <input type="number" id="control_quad_port" name="control_quad_port">
                    </div>
                </div>
            </div>
            <button type="button" id="save-btn">保存设置</button>
        </form>
    </div>
    <div class="notification" id="notification">保存成功，重启软件生效</div>
    <script>
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                const tabId = tab.getAttribute('data-tab');
                document.getElementById(tabId).classList.add('active');
            });
        });
        document.getElementById('save-btn').addEventListener('click', () => {
            const formData = new FormData(document.getElementById('config-form'));
            const configData = {};
            for (let [key, value] of formData.entries()) {
                if (!isNaN(value) && value !== '') {
                    configData[key] = Number(value);
                } else {
                    configData[key] = value;
                }
            }
            fetch('/save_config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(configData),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const notification = document.getElementById('notification');
                    notification.style.display = 'block';
                    setTimeout(() => {
                        notification.style.display = 'none';
                    }, 3000);
                } else {
                    alert('保存失败: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('保存失败: ' + error);
            });
        });
        window.addEventListener('DOMContentLoaded', () => {
            fetch('/get_config')
                .then(response => response.json())
                .then(data => {
                    Object.keys(data).forEach(key => {
                        const element = document.getElementById(key);
                        if (element) {
                            element.value = data[key];
                        }
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    </script>
</body>
</html>
"""


# open_source_project_address:https://github.com/swordswind/ai_virtual_mate_linux
@app5.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app5.route('/get_config')
def get_config():
    cfg = load_config()
    return jsonify(cfg)



@app5.route('/save_config', methods=['POST'])
def save_config_route():
    try:
        new_config_data = request.json
        cfg = load_config()
        cfg.update(new_config_data)
        if save_config(cfg):
            return jsonify({"success": True, "message": "保存成功，重启软件生效"})
        else:
            return jsonify({"success": False, "message": "保存设置失败"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app5.route('/assets/<path:path>')
def serve_static(path):  # 静态资源
    return send_from_directory('./dist/assets', path)


def get_local_ip():  # 获取本机IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('119.29.29.29', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    return ip


config = load_config()
prefer_asr = config["prefer_asr"]
prefer_llm = config["prefer_llm"]
prefer_tts = config["prefer_tts"]
prefer_vlm = config["prefer_vlm"]
prefer_ase = config["prefer_ase"]
username = config["username"]
mate_name = config["mate_name"]
prompt = config["prompt"]
vrm_model_name = config["vrm_model_name"]
speech_end_wait_time = config["speech_end_wait_time"]
wake_word = config["wake_word"]
mic_num = config["mic_num"]
sound_sense_switch = config["sound_sense_switch"]
sound_sense_threshold = config["sound_sense_threshold"]
voiceprint_switch = config["voiceprint_switch"]
voiceprint_threshold = config["voiceprint_threshold"]
myvoice_path = config["myvoice_path"]
glm_key = config["glm_key"]
glm_llm_model = config["glm_llm_model"]
glm_vlm_model = config["glm_vlm_model"]
openai_url = config["openai_url"]
openai_key = config["openai_key"]
openai_llm_model = config["openai_llm_model"]
openai_vlm_model = config["openai_vlm_model"]
ollama_url = config["ollama_url"]
ollama_llm_model = config["ollama_llm_model"]
ollama_vlm_model = config["ollama_vlm_model"]
lmstudio_url = config["lmstudio_url"]
anything_llm_ip = config["anything_llm_ip"]
anything_llm_ws = config["anything_llm_ws"]
anything_llm_key = config["anything_llm_key"]
dify_ip = config["dify_ip"]
dify_key = config["dify_key"]
stream_tts_switch = config["stream_tts_switch"]
edge_speaker = config["edge_speaker"]
edge_rate = config["edge_rate"]
edge_pitch = config["edge_pitch"]
vits_model_name = config["vits_model_name"]
gsv_api = config["gsv_api"]
gsv_prompt = config["gsv_prompt"]
gsv_ref_audio_path = config["gsv_ref_audio_path"]
gsv_prompt_lang = config["gsv_prompt_lang"]
gsv_lang = config["gsv_lang"]
cosy_api = config["cosy_api"]
qwentts_api = config["qwentts_api"]
voxcpm_api = config["voxcpm_api"]
index_api = config["index_api"]
custom_tts_url = config["custom_tts_url"]
custom_tts_model = config["custom_tts_model"]
custom_tts_voice = config["custom_tts_voice"]
custom_tts_key = config["custom_tts_key"]
cam_num = config["cam_num"]
ha_api = config["ha_api"]
ha_key = config["ha_key"]
entity_id = config["entity_id"]
net_num = config["net_num"]
router_ip = config["router_ip"]
weather_city = config["weather_city"]
rkllm_url = config["rkllm_url"]
auto_optimize_memory_switch = config["auto_optimize_memory_switch"]
welcome_voice_switch = config["welcome_voice_switch"]
state_port = config["state_port"]
live2d_port = config["live2d_port"]
mmd_port = config["mmd_port"]
vrm_port = config["vrm_port"]
embody_ai_mode = config["embody_ai_mode"]
ugv_radar_port = config["ugv_radar_port"]
ugv_robot_port = config["ugv_robot_port"]
ugv_move_gear = config["ugv_move_gear"]
ugv_rotate_gear = config["ugv_rotate_gear"]
control_ugv_port = config["control_ugv_port"]
quad_robot_port = config["quad_robot_port"]
control_quad_port = config["control_quad_port"]
lan_ip = get_local_ip()


def run_settings_web():  # 启动系统设置服务
    print(f"系统设置网址：http://{lan_ip}:5250\n")
    app5.run(port=5250, host="0.0.0.0")
