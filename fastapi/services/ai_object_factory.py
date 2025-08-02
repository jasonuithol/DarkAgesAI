"""
requirements:
"""

import random
import json

from domain.classes import Location, Item, Player, Enemy
from services.aiengines import AiChatContext, AiEngine

class AiObjectFactory:
    def __init__(self, ai_engine: AiEngine):
        self.ai_engine = ai_engine

    async def create_backstory(self) -> str:
        context = AiChatContext()
        context.add_system_message(
            "You are playing a fantasy rogue-like game."
        )
        context.add_user_message(
            "Come up with a backstory for the game that will allow cohesive generation of locations and items.  The tone should be of a narrator to a player, so avoid meta talk.  Do not mention inventory, or ask what to do next.  Just describe the backstory itself."
        )

        return await self.ai_engine.chat_completion_async(context)

    async def create_location(self, exits: dict[str, str], backstory: str, locations: dict[str, Location]) -> Location:

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

    async def create_item_image(self, description: str) -> str:
        return await self.ai_engine.text_to_image_async(
            description, 
            size="128x128"  # TODO: Actually make this work.
        )

    async def create_item(self, backstory: str) -> Item:
        item_type = random.choice(
            "Weapon,Spellbook,Money,Gem,Armour,Relic,Potion".split(",")
        )
        return await self.create_item_of_type(backstory=backstory, item_type=item_type)

    async def create_item_of_type(self, backstory: str, item_type: str) -> Item:

        context = AiChatContext()
        context.add_system_messages(
            [
                "You are playing a fantasy rogue-like game.",
                f"Backstory: {backstory}",
                f"You have found a new {item_type} at the current game location.",
                f"Come up with a short, unique name for this item, and say ONLY the name, no other guff please. Example: 'Ebony Sword'",
                f"Also describe the {item_type} you have just found.  Describe ONLY the {item_type}, and not anything else e.g. it's surrounds, stats, nor any sort of random sidequest associated with it.  Keep it focussed.",
            ]
        )
        context.add_user_message(
            'Give the response in this JSON format: {"name": "<the name of the item>", "description": "<the description of the item>"}'
        )

        responseJsonStr = await self.ai_engine.chat_completion_async(context)
        responseJson = json.loads(responseJsonStr)
        responseJson["item_type"] = item_type

        # Create an image for the item.
        responseJson["image"] = await self.create_item_image(responseJson["description"])

        return Item(**responseJson)
    '''
    async def create_player(self) -> Player:
        items = [
            Item(item_type="Weapon", name="rusty dagger", description="Nature has found a way to cause a dagger to exist that is more rust than iron.", image=""),
            Item(item_type="Armour", name="tattered rags", description="It's possible that being nude would provide more damage protection than these rags.", image=""),
            Item(item_type="Money", name="filthy copper piece", description="It's some sort of amorphous copper blob covered in grime.", image=""),
            Item(item_type="Spellbook", name="novice illusions", description="Contains the following spells: ['dim light', 'pick a card']", image="")
        ]
        for item in items:
            item.image = await self.create_item_image(item.description)
    
        return Player(x=0, y=0, items=items)
    '''
    async def create_enemy(self, backstory: str, surroundings: str) -> Item:
        context = AiChatContext()
        context.add_system_messages(
            [
                "You are playing a fantasy rogue-like game.",
                f"Backstory: {backstory}",
                f"You have just encountered an enemy. Location: {surroundings}",
                f"Come up with a short, unique name for this enemy, and say ONLY the name, no other guff please. Example: 'Flesh Reaping Worm'",
                f"Also describe the enemy you have just found.  Describe ONLY the enemy, and not anything else e.g. it's surrounds, stats, nor any sort of random sidequest associated with it.  Keep it focussed.",
            ]
        )
        context.add_user_message(
            'Give the response in this JSON format: {"name": "<the name of the item>", "description": "<the description of the item>"}'
        )

        responseJsonStr = await self.ai_engine.chat_completion_async(context)
        responseJson = json.loads(responseJsonStr)

        # Create an image for the item.
        responseJson["image"] = await self.create_item_image(responseJson["description"])

        return Enemy(**responseJson)
    


