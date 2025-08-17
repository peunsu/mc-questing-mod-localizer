# Minecraft Questing Mod Localizer

![GitHub Release](https://img.shields.io/github/v/release/peunsu/mc-questing-mod-localizer?style=for-the-badge)

Minecraft Questing Mod Localizer is a web application that helps you to localize quest files of Minecraft questing mods.
You can convert quest files to localizable format, translate quest files to other languages, and apply the translated quest files to the modpack.
This application supports [FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests-forge) and [Better Questing](https://www.curseforge.com/minecraft/mc-mods/better-questing).

* Web App: https://mc-questing-mod-localizer.streamlit.app

# Installation
* **Python 3.10** is required
* Clone the repo:
```bash
$ git clone https://github.com/peunsu/mc-questing-mod-localizer
```
* Create the virtual environment (optional):
```bash
$ python -m venv venv
$ source venv/bin/activate
```
* Install requirements:
```bash
$ pip install -r requirements.txt
```
* Run the application:
```bash
$ streamlit run app.py
```

# Dependencies
* [streamlit](https://github.com/streamlit/streamlit): A tool to build and share the web application with Python.
* [googletrans](https://github.com/ssut/py-googletrans): Google translate API for Python.
* [deepl-python](https://github.com/DeepLcom/deepl-python): DeepL API client for Python.
* [langchain](https://github.com/langchain-ai/langchain): A framework for developing applications powered by language models.
* [ftb-snbt-lib](https://github.com/peunsu/ftb-snbt-lib): Python library to parse, edit, and save FTB snbt tag.