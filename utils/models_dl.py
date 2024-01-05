import os
import requests

def download_file(url, output_file):
    # URLからファイルをダウンロードしてoutput_fileに保存する関数
    response = requests.get(url)
    with open(output_file, "wb") as f:
        f.write(response.content)

def download_files(repo_id, subfolder, files, cache_dir):
    # リポジトリから指定されたファイルをダウンロードする関数
    for file in files:
        url = f"https://huggingface.co/{repo_id}/resolve/main/{subfolder}/{file}"
        output_file = os.path.join(cache_dir, file)
        if not os.path.exists(output_file):
            print(f"{file} を {url} から {output_file} にダウンロードしています...")
            download_file(url, output_file)
            print(f"{file} のダウンロードが完了しました！")
        else:
            print(f"{file} は既にダウンロードされています")

def check_and_download_model(model_dir, model_id, sub_dirs, files):
    # モデルディレクトリが存在しない場合、モデルをダウンロードする
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print(f"モデルを {model_dir} にダウンロードしています。モデルID: {model_id}")

        # サブディレクトリごとにファイルをダウンロードする
        for sub_dir, sub_dir_files in sub_dirs:
            sub_dir_path = os.path.join(model_dir, sub_dir)
            if not os.path.exists(sub_dir_path):
                os.makedirs(sub_dir_path)
            download_files(model_id, sub_dir, sub_dir_files, sub_dir_path)

        # ルートディレクトリのファイルをダウンロードする
        for file in files:
            url = f"https://huggingface.co/{model_id}/resolve/main/{file}"
            output_file = os.path.join(model_dir, file)
            if not os.path.exists(output_file):
                print(f"{file} を {url} から {output_file} にダウンロードしています...")
                download_file(url, output_file)
                print(f"{file} のダウンロードが完了しました！")
            else:
                print(f"{file} は既にダウンロードされています")

        print("モデルのダウンロードが完了しました。")
    else:
        print("モデルは既にダウンロード済みです。")

def download_tagger_model(tagger_path, MODEL_ID):  
    SUB_DIRS = [
        ("variables", ["variables.data-00000-of-00001", "variables.index"]),
    ]
    FILES = ["keras_metadata.pb", "saved_model.pb", "selected_tags.csv"]
    model_dir = tagger_path + MODEL_ID
    check_and_download_model(model_dir, MODEL_ID, SUB_DIRS, FILES)


def download_diffusion_model(stable_diffusion_path, MODEL_ID):
    SUB_DIRS = [
        ("feature_extractor", ["preprocessor_config.json"]),
        ("scheduler", ["scheduler_config.json"]),
        ("safety_checker", ["config.json", "pytorch_model.bin"]),
        ("text_encoder", ["config.json", "pytorch_model.bin"]),
        ("tokenizer", ["merges.txt", "special_tokens_map.json", "tokenizer_config.json", "vocab.json"]),
        ("unet", ["config.json", "diffusion_pytorch_model.bin"]),
        ("vae", ["config.json", "diffusion_pytorch_model.bin"]),
    ]
    FILES = ["model_index.json"]
    model_dir = stable_diffusion_path + MODEL_ID
    check_and_download_model(model_dir, MODEL_ID, SUB_DIRS, FILES)

if __name__ == "__main__":
    stable_diffusion_path = "Models/Stable_diffusion/"
    MODEL_ID = "852wa/SDHK"
    download_diffusion_model(stable_diffusion_path, MODEL_ID)

    tagger_path = os.path.join(parent_directory, 'Models/')
    MODEL_ID = "SmilingWolf/wd-v1-4-moat-tagger-v2"
    model_dir = stable_diffusion_path + MODEL_ID
    download_tagger_model(tagger_path, MODEL_ID)