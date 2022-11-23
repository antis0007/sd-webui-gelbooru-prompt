import random
import re
import traceback

import gradio as gr

from modules import script_callbacks, scripts, shared
from modules.shared import opts
import requests
import bs4
from bs4 import BeautifulSoup


def on_ui_settings():
	section = ('gelbooru-prompt', "Gelbooru Prompt")

def fetch(image):
	#update hash based on image
	#name = image.name
	name = image.orig_name
	print("name: " + name)
	hash = name.split(".")[0]
	print("hash: " + hash)
	#update global hash
	

	url = "https://gelbooru.com/index.php?page=post&s=list&tags=md5%3a" + hash
	req = requests.get(url, 'html.parser')
	soup = BeautifulSoup(req.content , 'html.parser')
	found = None
	for link in soup.find_all('a'):
		link = link.get('href')
		if link.startswith("https://gelbooru.com/index.php?page=post"):
			if not link.endswith("tags=all"):
				found = link
				break
	if found is not None:
		if found.startswith("sample_"):
			found = found.replace("sample_", "")
		#print("FOUND: " + found)
		req = requests.get(found, 'html.parser') 
		soup = BeautifulSoup(req.content , 'html.parser')
		#tag_data = soup.find_all("textarea")
		tag_data = soup.find_all("textarea", {"id": "tags"})
		if len(tag_data) > 0:
			#print(tag_data)
			tag_data = tag_data[0].string.split(" ")
		else:
			return("Invalid Image Format...")
		parsed = []
		for tag in tag_data:
			tag = tag.replace("_", " ")
			parsed.append(tag)
		#print("Parsed tags: " + str(parsed))
		parsed = (", ").join(parsed)
		#print()
		print(parsed)
		#print()
		return(parsed)
	else:
		return("No image found with that hash...")

class BooruPromptsScript(scripts.Script):
	def __init__(self) -> None:
		super().__init__()
	def title(self):
		return("Gelbooru Prompt")
	def show(self, is_img2img):
		return scripts.AlwaysVisible

	def ui(self, is_img2img):
		with gr.Group():
			with gr.Accordion("Gelbooru Prompt", open=False):
				fetch_tags = gr.Button(value='Get Tags', variant='primary')
				#image = gr.Image(source="upload", type="file", label="Image with MD5 Hash")
				image = gr.File(type="file", label="Image with MD5 Hash")
				tags = gr.Textbox(value = "", label="Tags", lines=5)

		fetch_tags.click(fn=fetch, inputs=[image], outputs=[tags])
		return [image, tags, fetch_tags]


script_callbacks.on_ui_settings(on_ui_settings)