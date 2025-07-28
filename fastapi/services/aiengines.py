"""
requirements:

pip install huggingface_hub
pip install Pillow # for HuggingFace image processing
pip install wonderwords

Create a "Read" token at the HuggingFace website (free)

"""
import aiofiles
import asyncio
import base64
import json
import random

#import time

from io import BytesIO
from PIL import Image
from typing import Protocol, Tuple
#from threading import Lock

# AI providers (and test provider)
#from openai import OpenAI

from wonderwords import RandomSentence, RandomWord
from huggingface_hub import InferenceClient 

from domain.config import Config

class AiChatContext:
    def __init__(self):
        self.messages = []

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def add_system_message(self, content: str):
        self.add_message("system", content)

    def add_system_messages(self, contents: list[str]):
        for content in contents:
            self.add_system_message(content)

    def add_user_message(self, content: str):
        self.add_message("user", content)

    def add_assistant_message(self, content: str):
        self.add_message("assistant", content)

# Abstract base class for AI engines.
class AiEngine(Protocol):
    def chat_completion(self, context: AiChatContext) -> str:
        ...

    async def chat_completion_async(self, context: AiChatContext) -> str:
        ...

    def text_to_image(self, prompt: str, size: Tuple[int,int] = None) -> str:
        ...

    async def text_to_image_async(self, prompt: str, size: Tuple[int,int] = None) -> str:
        ...

# A fake AI engine for testing the rest of the application without using an actual AI service.
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

    def text_to_image(self, prompt: str, size: Tuple[int,int]=None) -> str:
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

    async def text_to_image_async(self, prompt, size: Tuple[int,int]=None):
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.text_to_image(prompt)
        )

class AiEngineHuggingFace(AiEngine):
    def __init__(self, text_model: str, image_model: str, token: str): 
        self.text_model = text_model
        self.image_model = image_model
        self.token = token
        self.client = InferenceClient(token=token)

    def chat_completion(self, context: AiChatContext) -> str:

        response = self.client.chat_completion(
            context.messages, model=self.text_model)

        if len(response.choices) > 1:
            print("ERROR: Multiple response blocks.")
            exit()

        # Obtain the response message
        # Ideally set n=1 - do it if there is missing reply content
        reply = response.choices[0].message["content"]

        return reply

    async def chat_completion_async(self, context: AiChatContext) -> str:
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.chat_completion(context)
        )

    def text_to_image(self, prompt: str, size: Tuple[int,int]=None) -> str:
        if size:
            image = self.client.text_to_image(
                prompt, width=size[0], height=size[1], model=self.image_model
            )
        else:
            image = self.client.text_to_image(prompt, model=self.image_model)
        buffer = BytesIO()
        image.save(buffer, format="PNG")  # PIL compatible.
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    async def text_to_image_async(self, prompt: str, size: Tuple[int,int]=None) -> str:
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.text_to_image(prompt)
        )
'''
class AiEngineOpenAI(AiEngine):
    def __init__(self, text_model: str, image_model: str, token: str, cooldown_seconds:int):

        self.client = OpenAI(api_key=token)
        self.text_model = text_model
        self.image_model = image_model

        self.cooldown_seconds = cooldown_seconds
        self.last_request_made = 0.0 # seconds since UNIX epoch (float)
        self.lock = Lock() # parent class is a singleton so this is allowed (I allow it for now anyways)

    # NGL OpenAI is not great.
    def wait_for_cooldown(self):
        with self.lock:
            time_left_to_wait =  time.time() - (self.cooldown_seconds + self.last_request_made)
            time.sleep(max(0, time_left_to_wait))  # wait until cooldown is over.
            self.last_request_made = time.time()

    def chat_completion(self, context: AiChatContext) -> str:
        self.wait_for_cooldown()
        response = self.client.chat.completions.create(
            model=self.text_model,
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in context.messages]
        )
        return response.choices[0].message.content

    async def chat_completion_async(self, context: AiChatContext) -> str:
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.chat_completion(context)
        )

    def text_to_image(self, prompt: str, size: Tuple[int,int]=None) -> str:
        self.wait_for_cooldown()
        response = self.client.images.generate(
            prompt=prompt,
            n=1,
            size=f"{size[0]}x{size[1]}" if size else "512x512",
            model=self.image_model
        )
        return response.data[0].url

    async def text_to_image_async(self, prompt: str, size: Tuple[int,int]=None) -> str:
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.text_to_image(prompt, size)
        )
'''
#
# Module level functions
#

async def get_engine(config: Config) -> AiEngine:
    engine_config = config.aiengines[config.chosen_aiengine]
    constructor = globals()[engine_config.engine_class]
    if engine_config.token_file:
        # Read the token from the file specified in the config, and add the token value to the parameters.
        async with aiofiles.open(engine_config.token_file, "r") as file:
            token_value = await file.read()
        parameters = engine_config.properties | {"token": token_value}
    else:
        parameters = engine_config.properties | {}
    return constructor(**parameters)

