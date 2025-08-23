"""
requirements:

pip install huggingface_hub
pip install Pillow # for HuggingFace image processing
pip install wonderwords

Create a "Read" token at the HuggingFace website (free)

"""
import asyncio
import base64
import json
import random

import importlib, os, sys

from io import BytesIO
from PIL import Image
from typing import Protocol, Tuple

# AI providers (and test provider)

from wonderwords import RandomSentence, RandomWord
from huggingface_hub import InferenceClient 

local_image_lock = asyncio.Lock()

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
        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        image_base64 = f"data:image/png;base64,{base64_str}"
        return image_base64

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
        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        image_base64 = f"data:image/png;base64,{base64_str}"
        return image_base64

    async def text_to_image_async(self, prompt: str, size: Tuple[int,int]=None) -> str:
        return await asyncio.get_running_loop().run_in_executor(
            None, lambda: self.text_to_image(prompt, size)
        )

class AiEngineHuggingFaceWithLocalImageGeneration(AiEngineHuggingFace):

    def __init__(self, text_model: str, image_library: str, token: str):
        super().__init__(text_model=text_model, image_model=None, token=token)

        module_dir = os.path.dirname(image_library)
        sys.path.insert(0, module_dir)  # Add image.py's directory to sys.path, allowing it to load it's local sublibraries.

        spec = importlib.util.spec_from_file_location(name="image_module", location=image_library)
        self.image_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.image_module)

        print(f"Dynamically loaded image model library: {image_library}")

        sys.path.pop(0)  # Clean up after import

    # DarkAgesAI:AiEngine compatible.
    def text_to_image(self, prompt: str, size: Tuple[int,int]=None) -> str:
        
        image_pil = self.image_module.generate_image(
            prompt=prompt,
            num_timesteps=28, 
            random_seed=42,
            image_size=size
        )

        buffer = BytesIO()
        image_pil.save(buffer, format="PNG")
        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        image_base64 = f"data:image/png;base64,{base64_str}"
        return image_base64
    
    async def text_to_image_async(self, prompt: str, size: Tuple[int,int]=None) -> str:

        async with local_image_lock:
            return await asyncio.get_running_loop().run_in_executor(
                None, lambda: self.text_to_image(prompt, size)
            )
