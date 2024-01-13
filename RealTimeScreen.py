import os
import sys
import time
import threading
import multiprocessing
from multiprocessing import Process, Queue, Value
from typing import List, Literal, Dict, Optional
import numpy as np
import torch
from PIL import Image, ImageTk
import PIL.Image
import mss
import tkinter as tk
from tkinter import ttk, messagebox
import fire
import pyperclip
import io
import win32clipboard
import keyboard 
import configparser
from typing import Optional, Dict
from streamdiffusion.image_utils import pil2tensor, postprocess_image
from utils.viewer import receive_images
from utils.wrapper import StreamDiffusionWrapper
from utils.models_dl import download_diffusion_model, download_tagger_model
from utils.tagger import modelLoad, analysis, character_analysis



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


def image_generation_process(queue, fps_queue, model_id_or_path, t_index_list, lora_dict, prompt, negative_prompt, acceleration, monitor, inputs, use_safety_checker, update_interval, is_generating):
    frame_buffer_size = 1
    if acceleration == "tensorrt":
        original_width = width=monitor['width']
        original_height = height=monitor['height']
        max_size = 1024
        scale_factor = min(max_size / original_width, max_size / original_height)
        width = int(original_width * scale_factor)
        height = int(original_height * scale_factor)
        width = width - (width % 64)
        height = height - (height % 64)

    else:
        width=monitor['width']
        height=monitor['height']

    stream = StreamDiffusionWrapper(
        model_id_or_path=model_id_or_path,
        vae_id=None,
        lora_dict=lora_dict,
        t_index_list=t_index_list,
        frame_buffer_size=frame_buffer_size,
        width=width,
        height=height,
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
        use_safety_checker=use_safety_checker,
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
        if not is_generating.value:  # フラグをチェック
            time.sleep(0.1)  # 生成を一時停止
            continue

        current_time = time.time()
        if current_time - last_update_time >= update_interval / 1000.0:
            captured_image = screen(monitor)

            if acceleration == "tensorrt":
                original_width, original_height = captured_image.size
                max_size = 1024
                scale_factor = min(max_size / original_width, max_size / original_height)
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                new_width = width - (width % 64)
                new_height = height - (height % 64)
                captured_image = captured_image.resize((new_width, new_height))            

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
                    output_image = postprocess_image(output_image, output_type="pil")[0]

                    if acceleration == "tensorrt":
                        original_size = (monitor['width'], monitor['height'])
                        output_image = output_image.resize(original_size)
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
        'character_check': 'False',
        'nsfw_check': 'False',
        'copy_key': 'p',
        'monitor_key': 'ctrl+m',
        'agree_terms': 'False'
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
    """Save settings to an ini file."""
    config = configparser.ConfigParser()
    config.read(filename)  # Read existing settings

    if 'Settings' not in config:
        config['Settings'] = {}

    # Update with new settings, converting all values to strings
    for key, value in new_settings.items():
        config['Settings'][key] = str(value)  # Convert to string

    with open(filename, 'w') as configfile:
        config.write(configfile)


def save_terms_agreement(config_filename, agree_terms):
    """免責事項の同意を設定ファイルに保存する"""
    config = configparser.ConfigParser()
    config.read(config_filename)
    
    if 'Settings' not in config:
        config['Settings'] = {}

    config['Settings']['Agree_terms'] = str(agree_terms)
    
    with open(config_filename, 'w') as configfile:
        config.write(configfile)

def check_and_display_terms(config_filename):
    """初回起動時に免責事項を表示し、ユーザーの同意を得る"""
    config = configparser.ConfigParser()
    config.read(config_filename)

    # 免責事項に同意しているか確認
    if config.get('Settings', 'Agree_terms', fallback='False') == 'True':
        return True

    # 免責事項を表示
    terms_text = (
        "責任の免除\n"
        "このソフトウェアを使用して生成されたイラストに関して、ソフトウェアの制作者は一切の責任を負いません。"
        "イラストの使用に関連するすべての問題や損害について、ソフト開発者は責任を負いません。\n\n"
        "イラストの品質\n"
        "イラスト生成の結果に関して、制作者は品質、正確性、適切さについて保証を行いません。"
        "生成されたイラストは、アルゴリズムやデータに基づいて自動的に生成されるため、その品質は変動する可能性があります。\n\n"
        "著作権とライセンス\n"
        "このソフトウェアを使用して生成されたイラストに関する著作権やライセンスについては、ユーザー自身が確認し、遵守する責任があります。"
        "ソフト開発者は、生成されたイラストの著作権や使用権について責任を負いません。\n\n"
        "ソフトウェアの利用\n"
        "ユーザーは、このソフトウェアを適切に利用し、法的な規制や他人の権利を侵害しないように注意する必要があります。"
        "ソフト開発者は、ユーザーがソフトウェアを適切に使用することに関して責任を負いません。\n\n"
        "キャラクターチェック機能に関する注意\n"
        "このソフトウェアには版権キャラクターを構成する要素が含まれる可能性をAIによって判定する機能がありますが、"
        "これはあくまで参照用であり確定ではありません。他人の絵を読み込ませて誹謗中傷する等の悪用はしないでください。\n\n"
        "この免責事項に同意するには「OK」をクリックしてください。OKをクリックすることにより、ユーザーは本免責事項に同意したものとみなされます。\n\n"
        "この免責事項は、RealTimeScreenの使用に関するすべての問題やリスクに対するソフト開発者の責任を免除するものであり、"
        "ユーザーはこれを理解し、受け入れたものとみなされます。RealTimeScreenを使用する前に、この免責事項をよく読んでください。"
        )
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示にする
    response = messagebox.showinfo("免責事項", terms_text)
    root.destroy()  # メインウィンドウを破棄する

    if response == "ok":
        save_terms_agreement(config_filename, True)
        return True
    else:
        return False


model = None
class ConfigWindow:
    def __init__(self, root, config_filename, monitor, is_generating):

        self.root = root
        root.title("Config")
        label = tk.Label(root)
        self.root.geometry("600x250")  # ウィンドウのサイズを設定
        root.attributes('-topmost', True)  # ウィンドウを最前面に保つ
        self.settings_updated = False  # 更新フラグ
        self.monitor = monitor
        self.is_generating = is_generating
        self.ignore_list = []

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

        # キャラクターチェッカーの入力
        self.character_check_var = tk.BooleanVar()
        # チェックボックスの作成
        self.character_check = ttk.Checkbutton(root, text="Character Check", variable=self.character_check_var)
        self.character_check.grid(row=7, column=0, columnspan=2, sticky=tk.W)

        # NSFWチェッカーの入力
        self.nsfw_check_var = tk.BooleanVar()
        # チェックボックスの作成
        self.nsfw_check = ttk.Checkbutton(root, text="NSFW Check", variable=self.nsfw_check_var)
        self.nsfw_check.grid(row=8, column=0, columnspan=2, sticky=tk.W)

      # 設定ボタン
        self.update_button = ttk.Button(root, text="Setting", command=self.update_settings)
        self.update_button.grid(row=9, column=0, columnspan=2, sticky=tk.EW)

      # Prompt分析ボタン 
        self.prompt_analysis_button = ttk.Button(root, text="Prompt Analysis", command=self.prompt_analysis)
        self.prompt_analysis_button.grid(row=10, column=0, columnspan=2, sticky=tk.EW)          
        
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
        character_check_setting = self.settings.get('character_check', '') 
        nsfw_check_setting = self.settings.get('nsfw_check', '')

        # ブール値を直接セット
        self.character_check_var.set(character_check_setting)
        self.nsfw_check_var.set(nsfw_check_setting)


        # character_check_analysisの定期実行を開始
        self.schedule_character_check_analysis()

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
            'negative_prompt': self.negative_prompt_entry.get(),
            'character_check': self.character_check_var.get(),
            'nsfw_check': self.nsfw_check_var.get(),
        }


    def get_current_settings(self):
        """現在のUIから設定を取得する"""
        return {
            'model_id_or_path': self.model_id_entry.get(),
            't_index': self.t_index_entry.get(),
            'update_interval': self.update_interval_entry.get(),
            'lora_path': self.lora_path_entry.get(),
            'lora_strength': self.lora_strength_entry.get(),
            'prompt': self.prompt_entry.get(),
            'negative_prompt': self.negative_prompt_entry.get(),
            'character_check': self.character_check_var.get(),
            'nsfw_check': self.nsfw_check_var.get(),
        }

    def update_settings(self):
        self.settings = self.get_user_settings()
        self.settings_updated = True
        self.root.event_generate("<<SettingsUpdated>>", when="tail")

    def prompt_analysis(self):
        self.is_generating.value = False
        global model
        tagger_path = os.path.join(dpath, 'Models/')
        MODEL_ID = "SmilingWolf/wd-v1-4-moat-tagger-v2"
        model_dir = os.path.join(tagger_path, MODEL_ID)
        if not os.path.exists(model_dir):
            download_tagger_model(tagger_path, MODEL_ID)
        if model is None:
            model = modelLoad(model_dir)
    
        # 現在の画面のスクリーンショットを取得
        image = screen(self.monitor)
        # タグ分析を実行
        tag = analysis(image, model, model_dir)

        # タグをプロンプト入力フィールドに追加
        self.prompt_entry.delete(0, tk.END)
        self.prompt_entry.insert(0, tag)
        self.is_generating.value = True  # イラスト生成を再開

    def character_check_analysis(self):
        self.is_generating.value = False
        global model
        tagger_path = os.path.join(dpath, 'Models/')
        MODEL_ID = "SmilingWolf/wd-v1-4-moat-tagger-v2"
        model_dir = os.path.join(tagger_path, MODEL_ID)
        if not os.path.exists(model_dir):
            download_tagger_model(tagger_path, MODEL_ID)
        if model is None:
            model = modelLoad(model_dir)

        # 現在の画面のスクリーンショットを取得
        image = screen(self.monitor)
        # タグ分析を実行
        character_tags = character_analysis(image, model, model_dir)

        # タグ分析の結果がNone以外の場合、かつ無視リストに含まれていないタグが存在する場合、ダイアログを表示
        if character_tags and any(tag not in self.ignore_list for tag in character_tags):
            # キャラクターごとに改行してメッセージを作成
            message = "あなたのイラストには次の要素が含まれている可能性があります\n" + \
                      "（この判定は曖昧なものであり、あくまで参照用です。決して他者のイラストへの誹謗中傷等に使わないで下さい）\n" + \
                      "\n".join([tag for tag in character_tags if tag not in self.ignore_list]) + \
                      "\n\nこのままイラストを生成続行しますか？"
            # messagebox.showinfo を使用して、OK ボタンのみを表示
            messagebox.showinfo("キャラクターチェック", message)

            # OKが選択されたと見なし、キャラクタータグを無視リストに追加
            for tag in character_tags:
                if tag not in self.ignore_list:
                    self.ignore_list.append(tag)
        self.is_generating.value = True  # イラスト生成を再開

    def schedule_character_check_analysis(self):
        if self.character_check_var.get():  # character_checkがTrueの場合のみ実行
            self.character_check_analysis()
        # 5分（300000ミリ秒）後に再度スケジュール
        self.root.after(300000, self.schedule_character_check_analysis)

    def get_settings(self):
        if self.settings_updated:
            self.settings_updated = False  # フラグをリセット
            return self.settings
        return None


class MainApp:
    def __init__(self, acceleration):
        self.process1 = None
        self.process2 = None
        self.monitor = None
        self.inputs = []
        self.config_filename = os.path.join(dpath, 'settings.ini')
        self.acceleration = acceleration
        self.initial_width = 512
        self.initial_height = 512
        self.is_generating = Value('b', True)
        self.queue = Queue()
        self.fps_queue = Queue()
        self.monitor = dummy_screen(self.initial_width, self.initial_height)
        self.root = tk.Tk()
        self.config_window = ConfigWindow(self.root, self.config_filename, self.monitor, self.is_generating)
        self.settings = self.config_window.load_settings(self.config_filename)

        self.setup_callbacks()
        # 設定ファイルが存在しない場合にのみ、デフォルト設定ファイルを作成
        if not os.path.exists(self.config_filename):
            create_default_settings_file(self.config_filename)

        if not check_and_display_terms(self.config_filename):
            print("ユーザーが免責事項に同意しなかったため、アプリケーションを終了します。")
            sys.exit()

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

        use_safety_checker = bool(user_settings.get("nsfw_check"))

        # 新しいプロセスを作成して開始
        self.process1 = Process(target=image_generation_process, args=(self.queue, self.fps_queue, model_dir, t_index_list, lora_dict, user_settings["prompt"], user_settings["negative_prompt"], self.acceleration, self.monitor, self.inputs, use_safety_checker, update_interval, self.is_generating))
        self.process1.start()
        self.process2 = Process(target=receive_images, args=(self.queue, self.fps_queue, user_settings))
        self.process2.start()

    def cleanup(self):
        current_settings = self.config_window.get_current_settings()

        # 設定をINIファイルに保存
        save_settings(self.config_filename, current_settings)


        if self.process1 and self.process1.is_alive():
            self.process1.terminate()
            self.process1.join()

        if self.process2 and self.process2.is_alive():
            self.process2.terminate()
            self.process2.join()

        self.root.destroy()

        # 代替のホットキー解除処理
        keyboard.unhook_all()

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
    app = MainApp(acceleration)
    app.run()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    fire.Fire(main)