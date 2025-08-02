"""
requirements:

pip install pydantic

"""

import json
import aiofiles
import aiofiles.ospath
import os

from pydantic import TypeAdapter

from domain.classes import World
from domain.config import Config

from services.ai_object_factory import AiObjectFactory
from services.combatant_factory import CombatantFactory
from services.item_factory import ItemFactory
from services.display import display

class WorldFactory:
    def __init__(self, ai_object_factory: AiObjectFactory, combatant_factory: CombatantFactory, item_factory: ItemFactory, config: Config):
        self.ai_object_factory = ai_object_factory
        self.combatant_factory = combatant_factory
        self.item_factory = item_factory
        self.save_file = config.save_file

    async def _load_world(self) -> World:
        async with aiofiles.open(self.save_file, "r") as file:
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

        for location in world.locations.values():
            location.items = [self.item_factory.subtypify_item(item) for item in location.items]

        world.player.items = [self.item_factory.subtypify_item(item) for item in world.player.items]
        
        if world.enemy:
            world.enemy.items = [self.item_factory.subtypify_item(item) for item in world.enemy.items]

        display("Loaded world from disk.")
        return world
    
    #
    # PUBLIC METHODS
    #

    async def save_world(self, world: World):
        async with aiofiles.open(self.save_file, "w") as file:
            json_str = world.model_dump_json(indent=4)
            await file.write(json_str)
            display("Saved world to disk.")

    def delete_world(self):
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
            print("Save file deleted successfully.")
        else:
            print(f"Save file not found: {self.save_file}")

    async def create_world(self) -> World:
        backstory = await self.ai_object_factory.create_backstory()
        player = await self.combatant_factory.create_player(backstory)
        world = World(backstory=backstory, player=player)
        display("Generated new world.")
        return world

    async def get_world(self) -> World:
        if await aiofiles.ospath.exists(self.save_file):
            world = await self._load_world()
        else:
            world = await self.create_world()
            await self.save_world(world)
        return world

