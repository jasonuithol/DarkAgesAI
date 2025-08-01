# 🛠️ Requirements

- **Operating System**: Windows
- **Accounts Needed**: [Hugging Face](https://huggingface.co/join) OR [OpenAI](https://auth.openai.com/create-account)


# 📦 Installation

Download and install the following:

- [Python](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/)
- [Nginx](https://nginx.org/en/download.html)

Add Python to your System Path (Environment Variable).
Add NGINX to your System Path (Environment Variable).

Download and unzip the following into a new directory:

- [DarkAgesAI](https://github.com/jasonuithol/DarkAgesAI/archive/refs/heads/master.zip)


# 🔐 Hugging Face Setup (NOTE: YOU'LL GET TWO FREE LOCATIONS - IT's $9AUD/month FOR PROPER ACCESS)

To access models or datasets:

1. Create a Hugging Face account [here](https://huggingface.co/join).
2. Go to [Access Tokens](https://huggingface.co/settings/tokens).
3. Create a token with **read** permissions.
4. Save your token in a new file at `/fastapi/token-hf.txt`


# 🔐 OpenAI Setup (EXPERIMENTAL - NO FREE ACCESS SO UNTESTED)

To access models or datasets:

1. Create an OpenAI account [here](https://auth.openai.com/create-account).
2. Go to [Access Tokens](https://huggingface.co/settings/tokens).
3. Create a token with **read** permissions.
4. Save your token in a new file at `/fastapi/token-hf.txt`


📁 **Token Storage Notes**

Make sure:
- The file contains only the token (no extra characters or line breaks).


# ▶️ Starting the Game

To launch the game, simply double-click the `dev.cmd` file located in the project root folder. This script will start all required services in development mode (the only mode so far supported.)

The game should automatically launch in your browser, but if it doesn't, click here: [START GAME](http://localhost)

