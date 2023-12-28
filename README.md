# RealTimeScreen
StreamDiffusionを用いた高速i2iキャプチャアプリ。（80倍速動画）<br>
![80](https://github.com/tori29umai0123/RealTimeScreen/assets/72191117/b218f707-a339-4594-8e70-2a1e2b26e80b)<br>


# 前提環境
OS：Windows10で確認済み<br>
以下をインストールしておくこと<br>
git: [git](https://git-scm.com/downloads)<br>
Python: [3.10.8](https://www.python.org/downloads/release/python-3810/)<br>
CUDA Toolkit: [12.1](https://developer.nvidia.com/cuda-12-1-0-download-archive)<br>

# 使い方
とりあえず動けばいい人向け。<br>
①コマンドプロンプトから適当なディレクトリでリポジトリをgit clone<br>
```
cd C:/
git clone https://github.com/tori29umai0123/RealTimeScreen.git
```
②install.ps1を右クリック→PowerShellで実行（15分位かかります）。『Install completed』と表示されたら終了<br>
③RealTimeScreen.ps1を右クリック→PowerShellで実行<br>
④起動すると半透明のダミースクリーンが現れるのでキャプチャしたい範囲に配置（大きさも変えられます）<br>
⑤『Setting』ボタンを押すと生成が開始されます。『P』キーを押すとクリップボードに画像が貼り付けられ、『Ctrl+M』でキャプチャ範囲の再指定ができます。
このキーボードショートカットはsettings.iniファイルから設定することもできます。

# 使い方（TensorRT）
分かる人だけ使って下さい。はじめて使うモデルをよみこむ時はTensorRTがモデルをビルドするので時間がかかります（初回だけ）<br>
①コマンドプロンプトから適当なディレクトリでリポジトリをgit clone<br>
```
cd C:/
git clone https://github.com/tori29umai0123/RealTimeScreen.git
```
②install_tensorrt.ps1を右クリック→PowerShellで実行（30分～1時間位かかります）。『Install completed』と表示されたら終了<br>
初回のモデルエンジンビルドにめちゃくちゃ時間かかって不安になるけど『Install completed』が出てくるまで我慢してください。<br>
③RealTimeScreen_tensorrt.ps1を右クリック→PowerShellで実行<br>
④起動すると半透明のダミースクリーンが現れるのでキャプチャしたい範囲に配置（大きさも変えられます）<br>
⑤『Setting』ボタンを押すと生成が開始されます。『P』キーを押すとクリップボードに画像が貼り付けられ、『Ctrl+M』でキャプチャ範囲の再指定ができます。
このキーボードショートカットはsettings.iniファイルから設定することもできます。

# 更新
①update.ps1（あるいはupdate_tensorrt.ps1）を右クリック→PowerShellで実行<br>
②『Do you want to proceed?』と聞かれるので『y』を入力<br>
③更新が始まります。うまくいかなかったから諦めて普通に再インストールして下さい。

# 設定例
model_id_or_path = 852wa/SDHK<br>
t_index = 32<br>
update_interval = 100<br>
lora_path = C:\stable-diffusion-webui\models\Lora\test-1.5-trnkegr_04-128_sdhk.safetensors<br>
lora_strength = 1.0<br>
prompt = 1girl, chibi<br>
negative_prompt = low quality, bad quality, blurry, low resolution<br>
copy_key = p<br>
monitor_key = ctrl+m

# パラメータ解説
model_id_or_path：生成モデル名<br>
t_index：20～40目安。数値が高いほど元の画像に近くなる<br>
update_interval：50～200目安。生成更新頻度。数値が高いほど更新ペースが遅くなる。お絵描きソフト等の挙動が重い時に数値を上げる<br>
lora_path：LoRAのpath<br>
lora_strength:LoRAの効き具合。絵柄LoRAの場合1.4位でいいかも<br>
prompt：プロンプト<br>
negative_prompt：ネガティブプロンプト<br>
copy_key：クリップボードに生成画像がコピーされるキー（デフォルト『P』）<br>
monitor_key；キャプチャ画面を再設定するキー（デフォルト『ctrl+m』）



