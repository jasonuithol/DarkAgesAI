"""
requirements:
"""

import random

from typing import Tuple
from domain.classes import Location, World
from services.ai_object_factory import AiObjectFactory
from services.item_factory import ItemFactory

class LocationFactory:
    def __init__(self, ai_object_factory: AiObjectFactory, item_factory: ItemFactory):
        self.ai_object_factory = ai_object_factory
        self.item_factory = item_factory

    async def _add_new_location(self, world: World, position: Tuple[int, int]) -> Location:
        exits = world.build_exits_message(
            position, include_description=True
        )
        new_location = await self.ai_object_factory.create_location(
            exits,
            world.backstory,
            world.locations
        )

        make_item = random.choice([True, False])
        if make_item == True:

            # might make an I/O call to an AI model.
            item = await self.item_factory.create_item(world.backstory)
            new_location.items.append(item)

        world.locations[position] = new_location

        return new_location
    
    #
    # PUBLIC METHODS
    #

    async def get_location(self, world: World, position: Tuple[int, int]) -> Location:
        location = world.locations.get(position)

        if location is None:
            location = await self._add_new_location( 
                world=world, 
                position=position
            )

        return location
    

