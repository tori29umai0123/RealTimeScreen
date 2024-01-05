import os
import sys
import time
import threading
import multiprocessing
from multiprocessing import Process, Queue
from typing import List, Literal, Dict, Optional
import numpy as np
import torch
from PIL import Image, ImageTk
import PIL.Image
import mss
import tkinter as tk
from tkinter import ttk
import fire
import pyperclip
import io
import win32clipboard
import keyboard 
import configparser
from typing import Optional, Dict
#import logging
from streamdiffusion.image_utils import pil2tensor, postprocess_image
from utils.viewer import receive_images
from utils.wrapper import StreamDiffusionWrapper
from utils.models_dl import download_diffusion_model
dpath = os.path.dirname(sys.argv[0])

def screen(monitor):
    with mss.mss() as sct:
        img = sct.grab(monitor)
        img = PIL.Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
        return img

def dummy_screen(width, height):
    screen_data = {'top': 0, 'left': 0, 'width': width, 'height': height}

    root = tk.Tk()
    root.title("Resize and Press Enter to start")
    root.geometry(f"{width}x{height}")
    root.resizable(True, True)
    root.attributes("-alpha", 0.8)
    root.configure(bg="black")

    def destroy(event):
        screen_data['width'] = root.winfo_width()
        screen_data['height'] = root.winfo_height()
        root.destroy()

    root.bind("<Return>", destroy)

    def update_geometry(event):
        screen_data['top'] = root.winfo_y()
        screen_data['left'] = root.winfo_x()

    root.bind("<Configure>", update_geometry)
    root.attributes('-topmost', True)
    root.mainloop()
    return screen_data


def image_generation_process(queue, fps_queue, model_id_or_path, t_index_list, lora_dict, prompt, negative_prompt, acceleration, monitor, inputs, update_interval):
    frame_buffer_size = 1
    stream = StreamDiffusionWrapper(
        model_id_or_path=model_id_or_path,
        vae_id=None,
        lora_dict=lora_dict,
        t_index_list=t_index_list,
        frame_buffer_size=frame_buffer_size,
        width=monitor['width'],
        height=monitor['height'],
        warmup=10,
        acceleration=acceleration,
        do_add_noise=True,
        enable_similar_image_filter=True,
        similar_image_filter_threshold=0.99,
        similar_image_filter_max_skip_frame=10,
        mode="img2img",
        use_denoising_batch=True,
        cfg_type="self",
        seed=2,
    )

    stream.prepare(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=50,
        guidance_scale=1.4,
        delta=1.0,
    )

    last_update_time = time.time()
    while True:
        current_time = time.time()
        if current_time - last_update_time >= update_interval / 1000.0:
            captured_image = screen(monitor)
            tensor_image = pil2tensor(captured_image)
            inputs.append(tensor_image)

            try:
                if len(inputs) < frame_buffer_size:
                    time.sleep(0.005)
                    continue

                start_time = time.time()
                sampled_inputs = []
                for i in range(frame_buffer_size):
                    index = (len(inputs) // frame_buffer_size) * i
                    sampled_inputs.append(inputs[len(inputs) - index - 1])

                input_batch = torch.cat(sampled_inputs)
                inputs.clear()
                output_images = stream.stream(
                    input_batch.to(device=stream.device, dtype=stream.dtype)
                ).cpu()

                if frame_buffer_size == 1:
                    output_images = [output_images]

                for output_image in output_images:
                    queue.put(output_image, block=False)

                fps = 1 / (time.time() - start_time)  # FPSの計算
                fps_queue.put(fps)  # FPSをキューに追加 (ここを修正)

                last_update_time = time.time()

            except KeyboardInterrupt:
                print(f"fps: {fps}")
                return

def create_default_settings_file(filename):
    """デフォルト設定を持つ settings.ini ファイルを作成する"""
    # デフォルト設定
    default_settings = {
        'model_id_or_path': 'KBlueLeaf/kohaku-v2.1',
        't_index': 32,
        'update_interval': 100,
        'lora_path': '',
        'lora_strength': 1.0,
        'prompt': '',
        'negative_prompt': 'low quality, bad quality, blurry, low resolution',
        'copy_key': 'p',
        'monitor_key': 'ctrl+m'
    }

    config = configparser.ConfigParser()

    # ".old" ファイルが存在するかチェック
    old_filename = filename + ".old"
    if os.path.exists(old_filename):
        # 既存の設定を読み込む
        config.read(old_filename)
        if 'Settings' in config:
            # 既存の設定にないデフォルト設定を追加
            for key, value in default_settings.items():
                if key not in config['Settings']:
                    config['Settings'][key] = str(value)
    else:
        # ".old" ファイルがない場合はデフォルト設定を使う
        config['Settings'] = default_settings

    # 新しい設定ファイルを書き込む
    with open(filename, 'w') as configfile:
        config.write(configfile)

def save_settings(filename, new_settings):
    """設定を ini ファイルに保存する"""
    config = configparser.ConfigParser()
    config.read(filename)  # 既存の設定を読み込む

    if 'Settings' not in config:
        config['Settings'] = {}

    # 既存の設定を保持しつつ、新しい設定で更新する
    for key, value in new_settings.items():
        config['Settings'][key] = value

    with open(filename, 'w') as configfile:
        config.write(configfile)



class ConfigWindow:
    def __init__(self, root, config_filename):

        self.root = root
        root.title("Config")
        label = tk.Label(root)
        self.root.geometry("600x170")  # ウィンドウのサイズを設定
        root.attributes('-topmost', True)  # ウィンドウを最前面に保つ
        self.settings_updated = False  # 更新フラグ

        # 第二列を伸縮可能に設定
        root.columnconfigure(1, weight=1)

        self.settings = {}

        # モデルIDの入力
        ttk.Label(root, text="ModelID").grid(row=0, column=0)
        self.model_id_entry = ttk.Entry(root)
        self.model_id_entry.grid(row=0, column=1, sticky=tk.EW)

        # t_indexの入力
        ttk.Label(root, text="t_index").grid(row=1, column=0)
        self.t_index_entry = ttk.Entry(root)
        self.t_index_entry.grid(row=1, column=1, sticky=tk.EW)

        # update_intervalの入力
        ttk.Label(root, text="update_interval").grid(row=2, column=0)
        self.update_interval_entry = ttk.Entry(root)
        self.update_interval_entry.grid(row=2, column=1, sticky=tk.EW)

        # LoRAモデルパス
        ttk.Label(root, text="LoRAPath").grid(row=3, column=0)
        self.lora_path_entry = ttk.Entry(root)
        self.lora_path_entry .grid(row=3, column=1, sticky=tk.EW)

        # LoRAstrength
        ttk.Label(root, text="LoRA_strength").grid(row=4, column=0)
        self.lora_strength_entry = ttk.Entry(root)
        self.lora_strength_entry.grid(row=4, column=1, sticky=tk.EW)

        # プロンプトの入力
        ttk.Label(root, text="Prompt").grid(row=5, column=0)
        self.prompt_entry = ttk.Entry(root)
        self.prompt_entry.grid(row=5, column=1, sticky=tk.EW)

        # ネガティブプロンプトの入力
        ttk.Label(root, text="Negative Prompt").grid(row=6, column=0)
        self.negative_prompt_entry = ttk.Entry(root)
        self.negative_prompt_entry.grid(row=6, column=1, sticky=tk.EW)

      # 設定ボタン
        self.update_button = ttk.Button(root, text="Setting", command=self.update_settings)
        self.update_button.grid(row=7, column=0, columnspan=2, sticky=tk.EW)

        if not os.path.exists(config_filename):
            create_default_settings_file(config_filename)

        self.settings = self.load_settings(config_filename)

        self.model_id_entry.insert(0, self.settings.get('model_id_or_path', ''))
        self.t_index_entry.insert(0, str(self.settings.get('t_index', '')))  # 数値は文字列に変換
        self.update_interval_entry.insert(0, str(self.settings.get('update_interval', '')))  # 数値は文字列に変換
        self.lora_path_entry.insert(0, self.settings.get('lora_path', ''))
        self.lora_strength_entry.insert(0, str(self.settings.get('lora_strength', '')))  # 数値は文字列に変換
        self.prompt_entry.insert(0, self.settings.get('prompt', ''))
        self.negative_prompt_entry.insert(0, self.settings.get('negative_prompt', ''))

    def load_settings(self, config_filename):
        """INIファイルから設定を読み込む"""
        config = configparser.ConfigParser()
        try:
            if not os.path.exists(config_filename):
                create_default_settings_file(config_filename)
            config.read(config_filename)
            return dict(config.items('Settings'))  # 'Settings' セクションの項目を辞書として取得
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}


    def get_user_settings(self):
        """ユーザーの設定を取得する"""
        return {
            'model_id_or_path': self.model_id_entry.get(),
            't_index': self.t_index_entry.get(),
            'update_interval': self.update_interval_entry.get(),
            'lora_path': self.lora_path_entry.get(),
            'lora_strength': self.lora_strength_entry.get(),
            'prompt': self.prompt_entry.get(),
            'negative_prompt': self.negative_prompt_entry.get()
        }

    def update_settings(self):
        self.settings = self.get_user_settings()
        self.settings_updated = True
        self.root.event_generate("<<SettingsUpdated>>", when="tail")


    def get_settings(self):
        if self.settings_updated:
            self.settings_updated = False  # フラグをリセット
            return self.settings
        return None


class MainApp:
    def __init__(self):
        self.process1 = None
        self.process2 = None
        self.monitor = None
        self.inputs = []
        self.config_filename = os.path.join(dpath, 'settings.ini')
        self.acceleration = "xformers"
        self.initial_width = 512
        self.initial_height = 512
        self.queue = Queue()
        self.fps_queue = Queue()
        self.monitor = dummy_screen(self.initial_width, self.initial_height)
        self.root = tk.Tk()
        self.config_window = ConfigWindow(self.root, self.config_filename)
        self.settings = self.config_window.load_settings(self.config_filename)

        self.setup_callbacks()
        create_default_settings_file(self.config_filename)
    def setup_callbacks(self):
        self.root.bind("<<SettingsUpdated>>", self.handle_settings_updated)
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)

        monitor_key = self.settings.get('monitor_key', 'ctrl+m')
        keyboard.add_hotkey(monitor_key, self.on_monitor_key_press)

    def on_monitor_key_press(self):
        self.monitor = dummy_screen(self.initial_width, self.initial_height)
        self.handle_settings_updated(None)

    def handle_settings_updated(self, event):
        user_settings = self.config_window.get_user_settings()
        save_settings(self.config_filename, user_settings)

        if user_settings:
            if self.process1:
                self.process1.terminate()
                self.process1.join()
            if self.process2:
                self.process2.terminate()
                self.process2.join()

        t_index_list = [int(user_settings.get("t_index")), 45]
        lora_dict = {}  # 既存の辞書がない場合
        lora_path = user_settings.get("lora_path")
        lora_path = lora_path.replace("\\", "/")
        lora_strength = float(user_settings.get("lora_strength"))
        update_interval = int(user_settings["update_interval"])
        if lora_path and lora_strength is not None:
                lora_dict[lora_path] = lora_strength
        else:
                lora_dict = None

        MODEL_ID = str(user_settings.get("model_id_or_path"))
        stable_diffusion_path = os.path.join(dpath, 'Models/')
        model_dir = stable_diffusion_path + MODEL_ID
        if not os.path.exists(model_dir):
                download_diffusion_model(stable_diffusion_path, MODEL_ID)
        # 新しいプロセスを作成して開始
        self.process1 = Process(target=image_generation_process, args=(self.queue, self.fps_queue, model_dir, t_index_list, lora_dict, user_settings["prompt"], user_settings["negative_prompt"], self.acceleration, self.monitor, self.inputs, update_interval))
        self.process1.start()
        self.process2 = Process(target=receive_images, args=(self.queue, self.fps_queue, user_settings))
        self.process2.start()

    def cleanup(self):
        if self.process1 and self.process1.is_alive():
            self.process1.terminate()
            self.process1.join()

        if self.process2 and self.process2.is_alive():
            self.process2.terminate()
            self.process2.join()

        self.root.destroy()
        keyboard.unhook_all_hotkeys()

    def run(self):
        self.root.mainloop()

def main(acceleration=None):
    acceleration_options = ["xformers", "tensorrt"]

    if acceleration is None:
        acceleration = "xformers"
    elif acceleration not in acceleration_options:
        print(f"Invalid acceleration option. Available options: {', '.join(acceleration_options)}")
        return

    # MainAppのインスタンスを作成し、アプリケーションを実行
    multiprocessing.freeze_support()
    app = MainApp()
    app.run()

if __name__ == "__main__":
    # log_path = os.path.join(dpath, 'error.log')
    # logging.basicConfig(filename=log_path, level=logging.DEBUG)

    # try:
    #     multiprocessing.freeze_support()
    #     fire.Fire(main)
    # except Exception as e:
    #     logging.exception("エラーが発生しました")

    multiprocessing.freeze_support()
    fire.Fire(main)