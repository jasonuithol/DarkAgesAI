'''
requirements:

pip install huggingface_hub
pip install Pillow
pip install pydantic

Create a "Read" token at the HuggingFace website (free)

'''

import base64
import random
import json
import httpx
import asyncio
import aiofiles
import aiofiles.ospath
import os

from domain.classes import Location, World, Item, Player
from services.display import display

from io import BytesIO
from pydantic import TypeAdapter
from huggingface_hub import InferenceClient
from huggingface_hub.errors import BadRequestError, HfHubHTTPError

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
        
class AiEngine:
    def __init__(self, text_model, image_model, token):
        self.text_model = text_model
        self.image_model = image_model
        self.token = token
        self.client = InferenceClient(token=token)

    def chat_completion(self, context):
        
        response = self.client.chat_completion(context.messages, model=self.text_model)
        
        if len(response.choices) > 1:
            print("ERROR: Multiple response blocks.")
            exit()
            
        # Obtain the response message
        # Ideally set n=1 - do it if there is missing reply content
        reply = response.choices[0].message["content"]
        
        return reply

    async def chat_completion_async(self, context):
        return await asyncio.get_running_loop().run_in_executor(None, lambda: self.chat_completion(context))

    def text_to_image(self, prompt, size = None):
        if size:
            image = self.client.text_to_image(
                prompt, 
                width=size[0],
                height=size[1],
                model=self.image_model
            )
        else:
            image = self.client.text_to_image(
                prompt, 
                model=self.image_model
            )
        buffer = BytesIO()
        image.save(buffer, format='PNG')  # PIL compatible.
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    async def text_to_image_async(self, prompt, size = None):
        return await asyncio.get_running_loop().run_in_executor(None, lambda: self.text_to_image(prompt))

class AiObjectFactory:
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine

    async def create_backstory(self):
        context = AiChatContext()
        context.add_system_message("You are playing a fantasy rogue-like game.")
        context.add_user_message("Come up with a backstory for the game that will allow cohesive generation of locations and items.  The tone should be of a narrator to a player, so avoid meta talk.  Do not mention inventory, or ask what to do next.  Just describe the backstory itself.")

        return await self.ai_engine.chat_completion_async(context)

    async def create_location(self, position, exits, backstory, locations):
        
#        exits = self.build_exits_message(position, include_description=True)
        
        context = AiChatContext()
        context.add_system_messages([
            "You are playing a fantasy rogue-like game.",
            f"Backstory: {backstory}",
            "You are looking about a new location you have discovered.",
            f"These are the surrounding locations in a dictionary.  Please make the new location consistent with it's known (charted) surrounds: \n{exits}",
            f"Come up with a short, unique name for this location, and say ONLY the name, no other guff please. The following names are already taken: {list(map(lambda x: x.name ,locations.values()))}",
            "Also describe what you see in this location only (do not describe exits, or other locations).  Do not describe items."
        ])
        context.add_user_message('Give the response in this JSON format: {"name": "<the name of the location>", "description": "<the description of the location>"}')
        
        responseJsonStr = await self.ai_engine.chat_completion_async(context)
        responseJson = json.loads(responseJsonStr)
        responseJson["image"] = await self.ai_engine.text_to_image_async(responseJson["description"])

        return Location(**responseJson)

    async def create_item(self, backstory):
        
        item_type = random.choice("weapon,spellbook,money,gem,armour,relic".split(','))
        
        context = AiChatContext()
        context.add_system_messages([
            "You are playing a fantasy rogue-like game.",
            f"Backstory: {backstory}",
            f"You have found a new {item_type} at the current game location.",
            f"Come up with a short, unique name for this item, and say ONLY the name, no other guff please. Example: 'Ebony Sword'",
            f"Also describe the {item_type} you have just found.  Describe ONLY the {item_type}, and not anything else e.g. it's surrounds, stats, some sort of random sidequest associated with it.  Keep it focussed."
        ])
        context.add_user_message('Give the response in this JSON format: {"name": "<the name of the item>", "description": "<the description of the item>"}')

        responseJsonStr = await self.ai_engine.chat_completion_async(context)
        responseJson = json.loads(responseJsonStr)
        responseJson["item_type"] = item_type
        responseJson["image"] = ""
       
        return Item(**responseJson)
    
    async def imagify_item(self, item): 
        item.image = await self.ai_engine.text_to_image_async(item.description, size=(128,128))
    
class WorldFactory:
    def __init__(self, ai_object_factory):
        self.ai_object_factory = ai_object_factory
        self.WORLD_FILENAME = "save/world.json"
        self.world = None

    async def save_world(self, world): 
        async with aiofiles.open(self.WORLD_FILENAME, "w") as file: 
            json_str = world.model_dump_json(indent=4)
            await file.write(json_str)

    async def load_world(self):
        async with aiofiles.open(self.WORLD_FILENAME, "r") as file:
            json_str = await file.read()
            raw = json.loads(json_str)

        # Convert "0,0" → (0, 0)
        raw["locations"] = {
            tuple(map(int, k.split(","))): v
            for k, v in raw.get("locations", {}).items()
        }

        adapter = TypeAdapter(World)
        world = adapter.validate_python(raw)
        return world

    async def get_world(self):
        if not self.world:
            if await aiofiles.ospath.exists(self.WORLD_FILENAME):
                display("Loading world from disk")
                self.world = await self.load_world()
            else:
                display("Generating new world")
                backstory = await self.ai_object_factory.create_backstory()
                self.world = World(
                    backstory = backstory
                )
                for item in self.world.player.items:
                    await self.ai_object_factory.imagify_item(item)
                    
                await self.save_world(self.world)
        return self.world

    async def add_new_location(self, position):
        exits = self.world.build_exits_message(position, include_description=True)
        new_location = await self.ai_object_factory.create_location(position, exits, self.world.backstory, self.world.locations)

        make_item = random.choice([True, False]) 
        if make_item == True:
            
            # might make an I/O call to an AI model.
            item = await self.ai_object_factory.create_item(self.world.backstory)
            await self.ai_object_factory.imagify_item(item)
            new_location.items.append(item)
            
        self.world.locations[position] = new_location
        
        return new_location

    async def get_location(self, position):
        location = self.world.locations.get(position)
        
        if location is None:
            location = await self.add_new_location(position)

        return location
