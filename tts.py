import asyncio
import glob
import os
import re
print("正在加载语音合成模块...")
import edge_tts
import sherpa_onnx
import pygame as pg
import requests as rq
import soundfile as sf
print("正在加载大模型模块...")
from openai import OpenAI
from web_settings import *

#vits_target_dir = "E:/model/TTS"
vits_target_dir = "data/model/TTS"
vits_model_dir = f"{vits_target_dir}/{vits_model_name}"
vits_tts = None
try:
    vits_model_path = glob.glob(os.path.join(vits_model_dir, "*.onnx"))[0]
    vits_tokens_path = f"{vits_model_dir}/tokens.txt"
    vits_data_dir = f"{vits_model_dir}/espeak-ng-data"
    vits_tts_config = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=vits_model_path, tokens=vits_tokens_path, data_dir=vits_data_dir), provider="cpu",
        num_threads=os.cpu_count()))
except Exception as e1:
    print(f"VITS模型加载错误，详情：{e1}")
voice_path = 'data/cache/cache_voice'
play_tts_flag = 0


def stop_tts():
    global play_tts_flag
    pg.quit()
    play_tts_flag = 0


def play_tts(text):  # 语音合成
    global play_tts_flag
    play_tts_flag = 1

    def play_voice():  # 播放语音
        pg.mixer.init()
        try:
            pg.mixer.music.load(voice_path)
            pg.mixer.music.play()
            while pg.mixer.music.get_busy() and play_tts_flag == 1:
                pg.time.Clock().tick(1)
            pg.mixer.music.stop()
        except:
            pass
        pg.quit()

    def split_text(text2):
        segments2 = re.split(r'([\n:：!！?？;；。])', text2)
        combined = []
        for i in range(0, len(segments2), 2):
            if i + 1 < len(segments2):
                combined.append(segments2[i] + segments2[i + 1])
            elif segments2[i].strip():  # 处理最后可能剩余的文本部分
                combined.append(segments2[i])
        return [seg.strip() for seg in combined if seg.strip()]  # 过滤空字符串

    async def ms_edge_tts(segment2):  # 带分段参数的edge_tts处理
        communicate = edge_tts.Communicate(segment2, voice=edge_speaker, rate=edge_rate, pitch=edge_pitch)
        await communicate.save(voice_path)

    processed_text = text.split("</think>")[-1].strip()
    processed_text = re.sub(r'[(（].*?[)）]', '', processed_text)
    if stream_tts_switch == "on":
        segments = split_text(processed_text)
        if not segments:  # 确保至少有一个分段
            segments = [processed_text]
    else:
        segments = [processed_text]  # 不分段，使用完整文本
    try:
        for segment in segments:
            if play_tts_flag != 1:
                break
            if prefer_tts == "edge-tts":
                try:
                    asyncio.run(ms_edge_tts(segment))
                    play_voice()
                except Exception as e:
                    print(f"edge-tts服务拥挤，错误详情：{e}")
            elif prefer_tts == "VITS":
                try:
                    tts_vits(segment)
                    play_voice()
                except Exception as e:
                    print(f"内置VITS服务拥挤，错误详情：{e}")
            elif prefer_tts == "GPT-SoVITS":
                url = f'{gsv_api}/tts?text={segment}&text_lang={gsv_lang}&prompt_text={gsv_prompt}&prompt_lang={gsv_prompt_lang}&ref_audio_path={gsv_ref_audio_path}'
                try:
                    res = rq.get(url)
                    with open(voice_path, 'wb') as f:
                        f.write(res.content)
                    play_voice()
                except Exception as e:
                    print(f"GPT-SoVITS整合包API服务器未开启，错误详情：{e}")
            elif prefer_tts == "CosyVoice":
                url = f'{cosy_api}/cosyvoice/?text={segment}'
                try:
                    res = rq.get(url)
                    with open(voice_path, 'wb') as f:
                        f.write(res.content)
                    play_voice()
                except Exception as e:
                    print(f"CosyVoice整合包API服务器未开启，错误详情：{e}")
            elif prefer_tts == "Qwen-TTS":
                url = f'{qwentts_api}/qwen_tts/?text={segment}'
                try:
                    res = rq.get(url)
                    with open(voice_path, 'wb') as f:
                        f.write(res.content)
                    play_voice()
                except Exception as e:
                    print(f"Qwen-TTS整合包API服务器未开启，错误详情：{e}")
            elif prefer_tts == "VoxCPM":
                url = f'{voxcpm_api}/voxcpm/?text={segment}'
                try:
                    res = rq.get(url)
                    with open(voice_path, 'wb') as f:
                        f.write(res.content)
                    play_voice()
                except Exception as e:
                    print(f"VoxCPM整合包API服务器未开启，错误详情：{e}")
            elif prefer_tts == "Index-TTS":
                url = f'{index_api}/indextts/?text={segment}'
                try:
                    res = rq.get(url)
                    with open(voice_path, 'wb') as f:
                        f.write(res.content)
                    play_voice()
                except Exception as e:
                    print(f"Index-TTS整合包API服务器未开启，错误详情：{e}")
            elif prefer_tts == "CustomTTS":
                try:
                    custom_tts(segment)
                    play_voice()
                except Exception as e:
                    print(f"自定义TTS API配置错误，错误详情：{e}")
    except Exception as e:
        print(f"语音合成服务出错：{str(e)}")


# open_source_project_address:https://github.com/swordswind/ai_virtual_mate_linux
def tts_vits(text):
    global vits_tts
    if vits_tts is None:
        vits_tts = sherpa_onnx.OfflineTts(vits_tts_config)
    audio = vits_tts.generate(text, sid=0, speed=1.0)
    sf.write(voice_path, audio.samples, samplerate=audio.sample_rate, subtype="PCM_16", format="wav")


def custom_tts(text):
    client = OpenAI(api_key=custom_tts_key, base_url=custom_tts_url)
    with client.audio.speech.with_streaming_response.create(
            model=custom_tts_model, voice=custom_tts_voice, input=text, response_format="mp3") as response:
        response.stream_to_file(voice_path)
