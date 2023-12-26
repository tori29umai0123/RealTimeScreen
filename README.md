# RealTimeScreen
LCM-LoRAを用いた高速i2iの検証用リポジトリ

# 前提環境
OS：Windows10で確認済み<br>
以下をインストールしておくこと<br>
git: [git](https://git-scm.com/downloads)<br>
Python: [3.10.8](https://www.python.org/downloads/release/python-3810/)<br>
CUDA Toolkit: [12.1](https://developer.nvidia.com/cuda-12-1-0-download-archive))<br>

# 使い方
①コマンドプロンプトから適当なディレクトリでリポジトリをgit clone<br>
```
cd C:/
git clone --branch test https://github.com/tori29umai0123/RealTimeScreen.git
```
②install.ps1を右クリック→PowerShellで実行（15分位かかります）<br>
③RealTimeScreen.ps1を右クリック→PowerShellで実行<br>
④起動すると半透明のダミースクリーンが現れるのでキャプチャしたい範囲に配置（大きさも変えられます）<br>
⑤『Setting』ボタンを押すと生成が開始されます。『P』キーを押すとクリップボードに画像が貼り付けられ、『Ctrl+M』でキャプチャ範囲の再指定ができます。
このキーボードショートカットはsettings.iniファイルから設定することもできます。

# 設定例
model_id_or_path = 852wa/SDHK<br>
t_index = 32<br>
lora_path = C:\stable-diffusion-webui\models\Lora\test-1.5-trnkegr_04-128_sdhk.safetensors
lora_strength = 1.0<br>
prompt = 1girl, chibi<br>
negative_prompt = low quality, bad quality, blurry, low resolution<br>
copy_key = p<br>
monitor_key = ctrl+m


