"""
requirements:

pip install pydantic

"""

import random
import json
import aiofiles
import aiofiles.ospath

from pydantic import TypeAdapter

from domain.classes import Location, World, Item, Player
from services.aiengines import AiChatContext
from services.display import display

class AiObjectFactory:
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine

    async def create_backstory(self):
        context = AiChatContext()
        context.add_system_message(
            "You are playing a fantasy rogue-like game.")
        context.add_user_message(
            "Come up with a backstory for the game that will allow cohesive generation of locations and items.  The tone should be of a narrator to a player, so avoid meta talk.  Do not mention inventory, or ask what to do next.  Just describe the backstory itself."
        )

        return await self.ai_engine.chat_completion_async(context)

    async def create_location(self, exits, backstory, locations):

        context = AiChatContext()
        context.add_system_messages(
            [
                "You are playing a fantasy rogue-like game.",
                f"Backstory: {backstory}"
                "You are looking about a new location you have discovered.",
                f"These are the surrounding locations in a dictionary.  Please make the new location consistent with it's known (charted) surrounds: \n{exits}",
                f"Come up with a short, unique name for this location, and say ONLY the name, no other guff please. The following names are already taken: {list(map(lambda x: x.name, locations.values()))}",
                "Also describe what you see in this location only (do not describe exits, or other locations).  Do not describe items.",
            ]
        )
        context.add_user_message(
            'Give the response in this JSON format: {"name": "<the name of the location>", "description": "<the description of the location>"}'
        )

        responseJsonStr = await self.ai_engine.chat_completion_async(context)
        responseJson = json.loads(responseJsonStr)
        responseJson["image"] = await self.ai_engine.text_to_image_async(
            responseJson["description"]
        )

        return Location(**responseJson)

    async def create_item_image(self, description):
        return await self.ai_engine.text_to_image_async(
            description, 
            size=(128, 128)
        )
    
    async def create_item(self, backstory):

        item_type = random.choice(
            "weapon,spellbook,money,gem,armour,relic".split(","))

        context = AiChatContext()
        context.add_system_messages(
            [
                "You are playing a fantasy rogue-like game.",
                f"Backstory: {backstory}",
                f"You have found a new {item_type} at the current game location.",
                f"Come up with a short, unique name for this item, and say ONLY the name, no other guff please. Example: 'Ebony Sword'",
                f"Also describe the {item_type} you have just found.  Describe ONLY the {item_type}, and not anything else e.g. it's surrounds, stats, some sort of random sidequest associated with it.  Keep it focussed.",
            ]
        )
        context.add_user_message(
            'Give the response in this JSON format: {"name": "<the name of the item>", "description": "<the description of the item>"}'
        )

        responseJsonStr = await self.ai_engine.chat_completion_async(context)
        responseJson = json.loads(responseJsonStr)
        responseJson["item_type"] = item_type
        responseJson["image"] = await self.create_item_image(responseJson["description"])

        return Item(**responseJson)

    async def create_player(self):
        items = [
            Item(item_type="weapon", name="rusty dagger", description="Nature has found a way to cause a dagger to exist that is more rust than iron.", image=""),
            Item(item_type="armour", name="tattered rags", description="It's possible that being nude would provide more damage protection than these rags.", image=""),
            Item(item_type="money", name="filthy copper piece", description="It's some sort of amorphous copper blob covered in grime.", image=""),
            Item(item_type="spellbook", name="novice illusions", description="Contains the following spells: ['dim light', 'pick a card']", image="")
        ]
        for item in items:
            item.image = await self.create_item_image(item.description)
    
        return Player(x=0, y=0, items=items)

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
            if json_str.strip() == "":
                return await self.create_world()
            
            raw = json.loads(json_str)

        # Convert "0,0" → (0, 0)
        raw["locations"] = {
            tuple(map(int, k.split(","))): v
            for k, v in raw.get("locations", {}).items()
        } 

        adapter = TypeAdapter(World)
        world = adapter.validate_python(raw)
        return world

    async def create_world(self):
        backstory = await self.ai_object_factory.create_backstory()
        player = await self.ai_object_factory.create_player()
        return World(backstory=backstory, player=player)

    async def get_world(self):
        if not self.world:
            if await aiofiles.ospath.exists(self.WORLD_FILENAME):
                display("Loading world from disk")
                self.world = await self.load_world()
            else:
                display("Generating new world")
                self.world = await self.create_world()
                await self.save_world(self.world)
        return self.world

    async def add_new_location(self, position):
        exits = self.world.build_exits_message(
            position, include_description=True
        )
        new_location = await self.ai_object_factory.create_location(
            exits, self.world.backstory, self.world.locations
        )

        make_item = random.choice([True, False])
        if make_item == True:

            # might make an I/O call to an AI model.
            item = await self.ai_object_factory.create_item(self.world.backstory)
            new_location.items.append(item)

        self.world.locations[position] = new_location

        return new_location

    async def get_location(self, position):
        location = self.world.locations.get(position)

        if location is None:
            location = await self.add_new_location(position)

        return location
