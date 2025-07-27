# 🛠️ Requirements

- **Operating System**: Windows
- **Accounts Needed**: [Hugging Face](https://huggingface.co/join)

# 📦 Installation

Download and install the following:

- [Python](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/)
- [Nginx](https://nginx.org/en/download.html)

# 🔐 Hugging Face Setup

To access models or datasets:

1. Create a Hugging Face account [here](https://huggingface.co/join).
2. Go to [Access Tokens](https://huggingface.co/settings/tokens).
3. Create a token with **read** permissions.
4. Save your token securely — you'll need it for authentication.

📁 **Token Storage**

Place your token in the following file path:

`/fastapi/token.txt`

Make sure:
- The `token.txt` file contains only the token (no extra characters or line breaks).
- The file is readable by your FastAPI app.

# ▶️ Starting the Game

To launch the game, simply double-click the `dev.cmd` file located in the project root folder. This script will start all required services in development mode (the only mode so far supported.)
