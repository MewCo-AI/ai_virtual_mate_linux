import json
import logging
import random
import socket
import pygame as pg
from flask import Flask, send_from_directory, render_template_string
from web_settings import mmd_port

app = Flask(__name__, static_folder='dist')
logging.getLogger('werkzeug').setLevel(logging.ERROR)

mmd_web_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/png" href="assets/image/logo.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MMD 3D角色 - Aivmate LX3</title>
    <style>
        body {
            margin: 0;
            background-image: url('assets/image/bg.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        canvas {
            display: block;
        }
    </style>
</head>
<body>
    <script src="assets/mmd_core/ammo.js"></script>
    <script src="assets/mmd_core/mmdparser.min.js"></script>
    <script src="assets/mmd_core/three.min.js"></script>
    <script src="assets/mmd_core/CCDIKSolver.js"></script>
    <script src="assets/mmd_core/MMDPhysics.js"></script>
    <script src="assets/mmd_core/TGALoader.js"></script>
    <script src="assets/mmd_core/MMDLoader.js"></script>
    <script src="assets/mmd_core/OrbitControls.js"></script>
    <script src="assets/mmd_core/MMDAnimationHelper.js"></script>
    <script src="assets/mmd.js"></script>
</body>
</html>
"""

mmd_vmd_web_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/png" href="assets/image/logo.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MMD 3D动作 - Aivmate LX3</title>
    <style>
        body {
            margin: 0;
            background-image: url('assets/image/bg.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        canvas { display: block; }
    </style>
</head>
<body>
    <script src="assets/mmd_core/ammo.js"></script>
    <script src="assets/mmd_core/mmdparser.min.js"></script>
    <script src="assets/mmd_core/three.min.js"></script>
    <script src="assets/mmd_core/CCDIKSolver.js"></script>
    <script src="assets/mmd_core/MMDPhysics.js"></script>
    <script src="assets/mmd_core/TGALoader.js"></script>
    <script src="assets/mmd_core/MMDLoader.js"></script>
    <script src="assets/mmd_core/OrbitControls.js"></script>
    <script src="assets/mmd_core/MMDAnimationHelper.js"></script>
    <script src="assets/mmd_vmd.js"></script>
</body>
</html>
"""


def get_local_ip():  # 获取本机IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('119.29.29.29', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    return ip


lan_ip = get_local_ip()


# open_source_project_address:https://github.com/swordswind/ai_virtual_mate_linux
@app.route('/')
def index():  # MMD角色页面
    return render_template_string(mmd_web_template)


@app.route('/vmd')
def index_vmd():  # MMD动作页面
    return render_template_string(mmd_vmd_web_template)


@app.route('/assets/<path:path>')
def serve_static(path):  # 静态资源
    if path.endswith(".js"):
        return send_from_directory('./dist/assets', path, mimetype='application/javascript')
    return send_from_directory('./dist/assets', path)


@app.route('/api/get_mouth_y')
def check_play_state():
    is_playing = pg.mixer.music.get_busy() if pg.mixer.get_init() else False
    if is_playing:
        return json.dumps({"y": random.uniform(0.1, 0.9)})
    else:
        return json.dumps({"y": 0})


def run_mmd():  # 启动MMD服务
    print(f"MMD 3D角色网址：http://{lan_ip}:{str(mmd_port)}\nMMD 3D动作网址：http://{lan_ip}:{str(mmd_port)}/vmd\n")
    app.run(port=mmd_port, host="0.0.0.0")
