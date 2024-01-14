**Switch to Japanese version**: [README.md](README.md)  
**Switch to English version**: [README_en.md](README_en.md)

# RealTimeScreen
StreamDiffusionを用いた高速i2iキャプチャアプリ。（80倍速動画）<br>
![80](https://github.com/tori29umai0123/RealTimeScreen/assets/72191117/b218f707-a339-4594-8e70-2a1e2b26e80b)<br>


# 前提環境
OS：Windows10で確認済み<br>
以下をインストールしておくこと<br>
git: [git](https://git-scm.com/downloads)<br>
Python: [3.10.8](https://www.python.org/downloads/release/python-3108/)<br>
CUDA Toolkit: [12.1](https://developer.nvidia.com/cuda-12-1-0-download-archive)<br>

# 使い方
とりあえず動けばいい人向け。<br>
https://note.com/tori29umai/n/nd5a21a2b1227

# 免責事項
## 責任の免除
このソフトウェアを使用して生成されたイラストに関して、ソフトウェアの制作者は一切の責任を負いません。イラストの使用に関連するすべての問題や損害について、ソフト開発者は責任を負いません。

## イラストの品質
イラスト生成の結果に関して、制作者は品質、正確性、適切さについて保証を行いません。生成されたイラストは、アルゴリズムやデータに基づいて自動的に生成されるため、その品質は変動する可能性があります。

## 著作権とライセンス
このソフトウェアを使用して生成されたイラストに関する著作権やライセンスについては、ユーザー自身が確認し、遵守する責任があります。ソフト開発者は、生成されたイラストの著作権や使用権について責任を負いません。

## ソフトウェアの利用
ユーザーは、このソフトウェアを適切に利用し、法的な規制や他人の権利を侵害しないように注意する必要があります。ソフト開発者は、ユーザーがソフトウェアを適切に使用することに関して責任を負いません。

## キャラクターチェック機能に関する注意
このソフトウェアには版権キャラクターを構成する要素が含まれる可能性をAIによって判定する機能がありますが、これはあくまで参照用であり確定ではありません。他人の絵を読み込ませて誹謗中傷する等の悪用はしないでください。

この免責事項は、RealTimeScreenの使用に関するすべての問題やリスクに対するソフト開発者の責任を免除するものであり、ユーザーはこれを理解し、受け入れたものとみなされます。RealTimeScreenを使用する前に、この免責事項をよく読んでください。


# 使い方（コマンドプロンプト使用）
①コマンドプロンプトから適当なディレクトリでリポジトリをgit clone<br>
```
cd C:/
git clone https://github.com/tori29umai0123/RealTimeScreen.git
```
②install.ps1を右クリック→PowerShellで実行（15分位かかります）。『Install completed』と表示されたら終了<br>
③RealTimeScreen.ps1を右クリック→PowerShellで実行<br>
④起動すると半透明のダミースクリーンが現れるのでキャプチャしたい範囲に配置（大きさも変えられます）<br>
⑤『Setting』ボタンを押すと生成が開始されます。『P』キーを押すとクリップボードに画像が貼り付けられ、『Ctrl+M』でキャプチャ範囲の再指定ができます。<br>
このキーボードショートカットはsettings.iniファイルから設定することもできます。<br>
『Prompt Analysis』ボタンを押すとキャプチャ範囲のイラストのprompt分析をします。<br>
『Charact Check』ボタンを押すとキャプチャ範囲のイラストが版権キャラクターの要素を含んでいないかのチェックをします。<br>

# 使い方（TensorRT）
分かる人だけ使って下さい。はじめて使うモデルをよみこむ時はTensorRTがモデルをビルドするので時間がかかります（初回だけ）<br>
①コマンドプロンプトから適当なディレクトリでリポジトリをgit clone<br>
②install_tensorrt.ps1を右クリック→PowerShellで実行（30分～1時間位かかります）。『Install completed』と表示されたら終了<br>
初回のモデルエンジンビルドにめちゃくちゃ時間かかって不安になるけど『Install completed』が出てくるまで我慢してください。<br>
③RealTimeScreen_tensorrt.ps1を右クリック→PowerShellで実行<br>
④起動すると半透明のダミースクリーンが現れるのでキャプチャしたい範囲に配置（大きさも変えられます）<br>
⑤『Setting』ボタンを押すと生成が開始されます。『P』キーを押すとクリップボードに画像が貼り付けられ、『Ctrl+M』でキャプチャ範囲の再指定ができます。<br>
このキーボードショートカットはsettings.iniファイルから設定することもできます。<br>
『Prompt Analysis』ボタンを押すとキャプチャ範囲のイラストのprompt分析をします。<br>
『Charact Check』ボタンを押すとキャプチャ範囲のイラストが版権キャラクターの要素を含んでいないかのチェックをします。<br>

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
nsfw_check = True<br>
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
character_check：版権キャラクターの要素を含んでいないかのチェック（5分に一度反映される）<br>
nsfw_check：nsfwなコンテンツを生成してないかのチェック（NSFWの場合真黒な画像が生成される）<br>
copy_key：クリップボードに生成画像がコピーされるキー（デフォルト『P』）<br>
monitor_key；キャプチャ画面を再設定するキー（デフォルト『ctrl+m』）

# ビルド設定（開発者向け）
①上記のインストールに従ってインストール（install_tensorrt.ps1を）<br>
②セキュリティーソフトの設定で、フォルダと実行ファイル名を除外リストに追加する。<br>
例：Windows Defenderの場合、Windows セキュリティ→ウイルスと脅威の防止→ウイルスと脅威の防止の設定→設定の管理→除外<br>
RealTimeScreen.exe(プロセス)<br>
C:\RealTimeScreen（フォルダ）<br>
のように指定する。<br>
③venv.cmdを実行。
```
pip install pyinstaller
pyinstaller C:/RealTimeScreen/RealTimeScreen.py
xcopy /E /I /Y venv\Lib\site-packages\xformers dist\RealTimeScreen\_internal\xformers
xcopy /E /I /Y venv\Lib\site-packages\tensorrt dist\RealTimeScreen\_internal\tensorrt
xcopy /E /I /Y venv\Lib\site-packages\cuda dist\RealTimeScreen\_internal\cuda
xcopy /E /I /Y venv\Lib\site-packages\tensorrt_bindings dist\RealTimeScreen\_internal\tensorrt_bindings
xcopy /E /I /Y venv\Lib\site-packages\tensorrt_libs dist\RealTimeScreen\_internal\tensorrt_libs
```
