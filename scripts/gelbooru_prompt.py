import random
import re
import traceback

import gradio as gr
import contextlib

from modules import script_callbacks, scripts, shared
from modules.shared import opts
import requests
import bs4
from bs4 import BeautifulSoup


def on_ui_settings():
    section = ('gelbooru-prompt', "Gelbooru Prompt")


def fetch(image):
    # update hash based on image
    name = image.orig_name
    # image.orig_name returns the path of the image, so we need to get the name of the file from that path
    # make this work for windows and linux
    if "\\" in name:
        name = name.split("\\")[-1]
    elif "/" in name:
        name = name.split("/")[-1]
    print("name: " + name)
    hash = name.split(".")[0]
    if hash.startswith("sample_"):
        hash = hash.replace("sample_", "")
    if hash.startswith("thumbnail_"):
        hash = hash.replace("thumbnail_", "")
    print("hash: " + hash)

    url = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=md5:" + hash
    req = requests.get(url)
    data = req.json()
    if data["@attributes"]["count"] > 1:
        return ("No image found with that hash...")
    else:
        post = data["post"][0]
        tags = post["tags"]

        parsed = []
        for tag in tags.split():
            tag = tag.replace("_", " ")
            parsed.append(tag)
        parsed = (", ").join(parsed)
        return (parsed)


class BooruPromptsScript(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

    def title(self):
        return ("Gelbooru Prompt")

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Group():
            with gr.Accordion("Gelbooru Prompt", open=False):
                fetch_tags = gr.Button(value='Get Tags', variant='primary')
                image = gr.File(type="file", label="Image with MD5 Hash")

            with contextlib.suppress(AttributeError):
                if is_img2img:
                    fetch_tags.click(fn=fetch, inputs=[image], outputs=[self.boxxIMG])
                else:
                    fetch_tags.click(fn=fetch, inputs=[image], outputs=[self.boxx])

        return [image, fetch_tags]

    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_prompt":
            self.boxx = component
        if kwargs.get("elem_id") == "img2img_prompt":
            self.boxxIMG = component


script_callbacks.on_ui_settings(on_ui_settings)
