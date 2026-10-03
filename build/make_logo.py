# -*- coding: utf-8 -*-
"""びわから基金ロゴ（横組・背景透明）の余白を切って images/logo.png に置く（2026-10-03）。
投稿デスクのヘッダーに出す。原本は 池田様/写真素材/ にある法人支給のロゴ。"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\yabem\OneDrive\デスクトップ\池田様\写真素材\びわから基金ロゴ　横組 (背景透明)_0.png"
im = Image.open(SRC).convert("RGBA")
im = im.crop(im.getchannel("A").getbbox())
w = 560
im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
im.save(os.path.join(os.path.dirname(HERE), "images", "logo.png"), optimize=True)
print("logo", im.size)
