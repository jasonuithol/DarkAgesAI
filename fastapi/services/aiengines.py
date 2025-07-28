"""
requirements:

pip install huggingface_hub
pip install Pillow # for HuggingFace image processing
pip install wonderwords

Create a "Read" token at the HuggingFace website (free)

"""
import base64
import asyncio
from PIL import Image
import random
import json

from io import BytesIO
from typing import Protocol
import aiofiles
from wonderwords import RandomSentence, RandomWord
from domain.config import Config

from huggingface_hub import InferenceClient
# from huggingface_hub.errors import BadRequestError, HfHubHTTPError


class AiChatContext:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def add_system_message(self, content):
        self.add_message("system", content)

    def add_system_messages(self, contents):
        for content in contents:
            self.add_system_message(content)

    def add_user_message(self, content):
        self.add_message("user", content)

    def add_assistant_message(self, content):
        self.add_message("assistant", content)

class AiEngine(Protocol):
    def chat_completion(self, context: AiChatContext) -> str:
        ...

    async def chat_completion_async(self, context: AiChatContext) -> str:
        ...

    def text_to_image(self, prompt: str, size=None) -> str:
        ...

    async def text_to_image_async(self, prompt: str, size=None) -> str:
        ...

class AiEngineTest(AiEngine):
    def chat_completion(self, context: AiChatContext) -> str:
        rnd_word = RandomWord()
        rnd_sentence = RandomSentence()
        if any("JSON" in msg["content"] for msg in context.messages):
            return json.dumps({
                "name": rnd_word.word(), 
                "description": rnd_sentence.sentence()
            })
        else:
            # Return some randomnly generated text for testing
            return rnd_sentence.sentence()

    async def chat_completion_async(self, context: AiChatContext) -> str:
            return await asyncio.get_running_loop().run_in_executor(
                None, lambda: self.chat_completion(context)
            )

    def text_to_image(self, prompt: str, size=None) -> str:
        # Use PIL to generate a 512x512 png with random scribbles.
        image = Image.new("RGB", (512, 512), color=(255, 255, 255))

        # Generate random scribbles
        for _ in range(1000):
            x = random.randint(0, 511)
            y = random.randint(0, 511)
            image.putpixel((x, y), (0, 0, 0))
        buffer = BytesIO()
        image.save(buffer, format="PNG")  # PIL compatible.

        # Convert the image to base64 and return
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    async def text_to_image_async(self, prompt, size=None):
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.text_to_image(prompt)
        )

class AiEngineHuggingFace(AiEngine):
    def __init__(self, text_model, image_model, token):
        self.text_model = text_model
        self.image_model = image_model
        self.token = token
        self.client = InferenceClient(token=token)

    def chat_completion(self, context):

        response = self.client.chat_completion(
            context.messages, model=self.text_model)

        if len(response.choices) > 1:
            print("ERROR: Multiple response blocks.")
            exit()

        # Obtain the response message
        # Ideally set n=1 - do it if there is missing reply content
        reply = response.choices[0].message["content"]

        return reply

    async def chat_completion_async(self, context):
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.chat_completion(context)
        )

    def text_to_image(self, prompt, size=None):
        if size:
            image = self.client.text_to_image(
                prompt, width=size[0], height=size[1], model=self.image_model
            )
        else:
            image = self.client.text_to_image(prompt, model=self.image_model)
        buffer = BytesIO()
        image.save(buffer, format="PNG")  # PIL compatible.
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    async def text_to_image_async(self, prompt, size=None):
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.text_to_image(prompt)
        )
    
#
# Module level functions
#

async def get_token(filename: str) -> str:
    async with aiofiles.open(filename, "r") as file:
        return await file.read()

async def get_engine(config: Config) -> AiEngine:
    engine_config = config.aiengines[config.chosen_aiengine]
    constructor = globals()[engine_config.engine_class]
    return constructor(**engine_config.properties)

def get_configured_aiengine(config) -> AiEngine:
    token = get_token(config)
    constructor = globals()[config.aiengine]
    
    return constructor(
        text_model=config.text_model,
        image_model=config.image_model,
        token=token
    )
