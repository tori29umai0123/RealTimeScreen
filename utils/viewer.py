import os
import sys
import threading
import time
import io
import tkinter as tk
from multiprocessing import  Queue
from typing import List
from PIL import Image, ImageTk
from streamdiffusion.image_utils import postprocess_image
import win32clipboard
import keyboard 

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_settings(filename):
    """ini ファイルから設定を読み込む。ファイルがない場合はデフォルト設定を作成する"""
    config = configparser.ConfigParser()
    if not os.path.exists(filename):
        create_default_settings_file(filename)
    config.read(filename)
    return config['Settings'] if 'Settings' in config else {}

tk_image = None
def update_image(image_data:Image, label: tk.Label) -> None:
    global tk_image  # グローバル変数を使用

    if tk_image is None:
        tk_image = ImageTk.PhotoImage(image_data)
    else:
        tk_image.paste(image_data)

    label.configure(image=tk_image)
    label.original_image = image_data

def _receive_images(
    queue: Queue, fps_queue: Queue, label: tk.Label, fps_label: tk.Label
) -> None:
    update_interval = 100 
    last_update_time = time.time()

    while True:
        current_time = time.time()
        if current_time - last_update_time >= update_interval / 1000.0:  # 指定した間隔が経過したか確認
            try:
                if not queue.empty():
                    label.after(
                        0,
                        update_image,
                        postprocess_image(queue.get(block=False), output_type="pil")[0],
                        label,
                    )
                    last_update_time = current_time  # 最後の更新時間を更新

                if not fps_queue.empty():
                    fps_label.config(text=f"FPS: {fps_queue.get(block=False):.2f}")

            except KeyboardInterrupt:
                return


def receive_images(queue: Queue, fps_queue: Queue, user_settings) -> None:
    root = tk.Tk()
    root.title("Image Viewer")
    root.attributes('-topmost', True)
    label = tk.Label(root)
    label.grid(column=0)
    fps_label = tk.Label(root, text="FPS: 0")
    fps_label.grid(column=1)

    def copy_image_to_clipboard():
        if hasattr(label, 'original_image'):
            with io.BytesIO() as output:
                label.original_image.save(output, format="BMP")
                data = output.getvalue()[14:]  # BMPヘッダーを除去
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
            print("画像をクリップボードにコピーしました")

    def on_copy_key_press():
        copy_image_to_clipboard()
   
    # 'copy_key' に対応する設定値を取得。デフォルトは 'p'
    copy_key = user_settings.get('copy_key', 'p')
    
    # 'P' キーが押されたときに on_copy_key_press 関数を呼び出す
    keyboard.add_hotkey(copy_key, on_copy_key_press)

    thread = threading.Thread(target=_receive_images, args=(queue, fps_queue, label, fps_label), daemon=True)
    thread.start()
    root.mainloop()
    # ウィンドウが閉じられた後にホットキーの設定を解除
    keyboard.unhook_all_hotkeys()