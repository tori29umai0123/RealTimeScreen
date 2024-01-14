**Switch to Japanese version**: [README.md](README.md)  
**Switch to English version**: [README_en.md](README_en.md)

# RealTimeScreen
A fast i2i capture app using StreamDiffusion. (80x speed video)  <br>
![80](https://github.com/tori29umai0123/RealTimeScreen/assets/72191117/b218f707-a339-4594-8e70-2a1e2b26e80b)<br>

# Disclaimer
## Limitation of Liability
The creators of this software bear no responsibility for any issues or damages related to the illustrations generated using this software. The software developers are not liable for any problems or damages associated with the use of these illustrations.

## Quality of Illustrations
Regarding the results of the illustration generation, the creators do not guarantee the quality, accuracy, or appropriateness of the generated illustrations. As they are automatically generated based on algorithms and data, their quality may vary.

## Copyright and Licensing
Users are responsible for verifying and complying with the copyright and licensing of illustrations generated using this software. The software developers do not hold responsibility for the copyright or usage rights of the generated illustrations.

## Use of Software
Users should use this software appropriately, ensuring not to violate legal regulations or infringe upon the rights of others. The software developers are not responsible for the proper usage of the software by the users.

## Notice Regarding Character Check Function
This software includes a function that uses AI to determine the potential inclusion of elements constituting copyrighted characters. However, this is solely for reference purposes and is not definitive. Please do not misuse this feature by uploading someone else's artwork for defamation or other malicious purposes.

This disclaimer absolves the software developers of any responsibility for all issues and risks associated with the use of RealTimeScreen. Users are deemed to have understood and accepted this upon using RealTimeScreen. Please read this disclaimer carefully before using RealTimeScreen.

## Prerequisites
OS: Confirmed on Windows 10  <br>
Ensure the following are installed:  <br>
- git: [git](https://git-scm.com/downloads)<br>
- Python: [3.10.8](https://www.python.org/downloads/release/python-3108/)<br>
- CUDA Toolkit: [12.1](https://developer.nvidia.com/cuda-12-1-0-download-archive)<br>

# How to use
For those who just want to get it running.<br>. Built<br>
https://note.com/tori29umai/n/nd5a21a2b1227

# How to use (using command prompt)
1. Clone the repository in a suitable directory from the command prompt:<br>

```
cd C:/
git clone https://github.com/tori29umai0123/RealTimeScreen.git
```
2. Right-click on `install.ps1` and run with PowerShell (takes about 15 minutes). Wait until "Install completed" is displayed.<br>
3. Right-click on `RealTimeScreen.ps1` and run with PowerShell.<br>
4. A translucent dummy screen appears upon launch. Place it over the area you want to capture (size is adjustable).<br>
5. Press the "Setting" button to start generation. Press the "P" key to paste the image to the clipboard, and "Ctrl+M" to reselect the capture area. These keyboard shortcuts can also be set in the settings.ini file.<br>
When the 'Prompt Analysis' button is pressed, it analyzes the prompt of the illustration within the capture range<br>
Please note that when loading a model for the first time, it will take time to download, so be aware of this (for the first time only, an online connection is required for the download)<br>
When you press the 'Character Check' button, it will check whether the captured area of the illustration contains any elements of copyrighted characters.

## How to Use (TensorRT)
For those familiar with TensorRT. <br>

1. Follow steps 1 to 2 as above.<br>
2. Right-click on `install_tensorrt.ps1` and run with PowerShell (takes 30 minutes to 1 hour). Wait for "Install completed" to be displayed.<br>
3. Right-click on `RealTimeScreen_tensorrt.ps1` and run with PowerShell.<br>
4. Follow steps 4 and 5 as above.

## Updates
1. Right-click on `update.ps1` (or `update_tensorrt.ps1`) and run with PowerShell.<br>
2. When asked "Do you want to proceed?", type "y".<br>
3. The update begins. If it doesn't work, please reinstall.

## Example Settings

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


## Parameter Explanation
- `model_id_or_path`: Name of the generation model
- `t_index`: Aim for 20-40. Higher values are closer to the original image.
- `update_interval`: Aim for 50-200. Generation update frequency. Higher values mean slower updates.
- `lora_path`: Path to LoRA
- `lora_strength`: Strength of LoRA effect. About 1.4 might be good for style LoRA.
- `prompt`: Prompt
- `negative_prompt`: Negative prompt
- `nsfw_check`: Checks if the content being generated is Not Safe For Work (NSFW). If it is NSFW, a completely black image is generated.
- `copy_key`: Key to copy the generated image to the clipboard (default "P")
- `monitor_key`: Key to reset the capture screen (default "ctrl+m")
 
# Build Instructions (For Developers)
1. Follow the How to Use mentioned above.
2. In your security software settings, add the folder and executable file names to the exclusion list. 
   Example: For Windows Defender, navigate to Windows Security → Virus & threat protection → Virus & threat protection settings → Manage settings → Exclusions, and specify:
   - RealTimeScreen.exe (Process)
   - C:\RealTimeScreen (Folder)
3. Execute `venv.cmd`.
```
pip install pyinstaller
pyinstaller C:/RealTimeScreen/RealTimeScreen.py
xcopy /E /I /Y venv\Lib\site-packages\xformers dist\RealTimeScreen\_internal\xformers
xcopy /E /I /Y venv\Lib\site-packages\tensorrt dist\RealTimeScreen\_internal\tensorrt
xcopy /E /I /Y venv\Lib\site-packages\cuda dist\RealTimeScreen\_internal\cuda
xcopy /E /I /Y venv\Lib\site-packages\tensorrt_bindings dist\RealTimeScreen\_internal\tensorrt_bindings
xcopy /E /I /Y venv\Lib\site-packages\tensorrt_libs dist\RealTimeScreen\_internal\tensorrt_libs
```
