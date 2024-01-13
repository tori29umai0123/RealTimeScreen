# -*- coding: utf-8 -*-
# https://github.com/kohya-ss/sd-scripts/blob/main/finetune/tag_images_by_wd14_tagger.py

import csv
import os
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

from PIL import Image
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from pathlib import Path


# from wd14 tagger
IMAGE_SIZE = 448

model = None  # Initialize model variable

def preprocess_image(image):
    image = np.array(image)
    image = image[:, :, ::-1]  # RGB->BGR

    # pad to square
    size = max(image.shape[0:2])
    pad_x = size - image.shape[1]
    pad_y = size - image.shape[0]
    pad_l = pad_x // 2
    pad_t = pad_y // 2
    image = np.pad(image, ((pad_t, pad_y - pad_t), (pad_l, pad_x - pad_l), (0, 0)), mode="constant", constant_values=255)

    interp = cv2.INTER_AREA if size > IMAGE_SIZE else cv2.INTER_LANCZOS4
    image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE), interpolation=interp)

    image = image.astype(np.float32)
    return image

def modelLoad(model_dir):
    global model  # Declare model as a global variable
    model = load_model(model_dir)
    return model

def analysis(image, model, model_dir):
    with open(os.path.join(model_dir, "selected_tags.csv"), "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        header = l[0]  # tag_id,name,category,count
        rows = l[1:]
    assert header[0] == "tag_id" and header[1] == "name" and header[2] == "category", f"unexpected csv format: {header}"

    general_tags = [row[1] for row in rows[1:] if row[2] == "0"]
    character_tags = [row[1] for row in rows[1:] if row[2] == "4"]

    tag_freq = {}
    undesired_tags = []

    def run_single_image(image, model):
        image = np.expand_dims(image, axis=0) # Convert single image to a batch.
        probs = model(image, training=False)
        prob = probs[0].numpy()  # Get the probabilities of the first image in the batch (the only image)

        combined_tags = []
        general_tag_text = ""
        character_tag_text = ""
        thresh = 0.35 
        for i, p in enumerate(prob[4:]):
            if i < len(general_tags) and p >= thresh:
                tag_name = general_tags[i]
                if tag_name not in undesired_tags:
                    tag_freq[tag_name] = tag_freq.get(tag_name, 0) + 1
                    general_tag_text += ", " + tag_name
                    combined_tags.append(tag_name)
            elif i >= len(general_tags) and p >= thresh:
                tag_name = character_tags[i - len(general_tags)]
                if tag_name not in undesired_tags:
                    tag_freq[tag_name] = tag_freq.get(tag_name, 0) + 1
                    character_tag_text += ", " + tag_name
                    combined_tags.append(tag_name)

        # 先頭のカンマを取る
        if len(general_tag_text) > 0:
            general_tag_text = general_tag_text[2:]
        if len(character_tag_text) > 0:
            character_tag_text = character_tag_text[2:]

        tag_text = ", ".join(combined_tags)
        return tag_text

    image = preprocess_image(image)
    tag = run_single_image(image, model)
    return tag


def character_analysis(image, model, model_dir):
    with open(os.path.join(model_dir, "selected_tags.csv"), "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        header = l[0]  # tag_id,name,category,count
        rows = l[1:]
    assert header[0] == "tag_id" and header[1] == "name" and header[2] == "category", f"unexpected csv format: {header}"

    character_tags = [row[1] for row in rows[1:] if row[2] == "4"]

    # character_tagsが空の場合、Noneを返す
    if not character_tags:
        return None

    tag_freq = {}
    undesired_tags = []

    def run_single_image(image, model, character_tags):
        image = np.expand_dims(image, axis=0)  # Convert single image to a batch.
        probs = model(image, training=False)
        prob = probs[0].numpy()  # Get the probabilities of the first image in the batch (the only image)

        character_tags_probs = []
        thresh = 0.90
        for i, p in enumerate(prob[4:]):  # 確率とインデックスを取得
            if p >= thresh and i < len(character_tags):  # 閾値とインデックス範囲のチェック
                tag_name = character_tags[i]  # 適切なタグ名を取得
                percentage_str = f"{p * 100:.2f}%"  # パーセンテージを文字列に変換し、末尾に "%" を追加
                character_tags_probs.append((tag_name, percentage_str))
        return character_tags_probs
    image = preprocess_image(image)
    tags_with_probs = run_single_image(image, model, character_tags)
    return tags_with_probs