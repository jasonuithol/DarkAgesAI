"""
requirements:
"""

from domain.classes import Location, Enemy, Player
from services.ai_object_factory import AiObjectFactory
from services.item_factory import ItemFactory

class CombatantFactory:
    
    def __init__(self, ai_object_factory: AiObjectFactory, item_factory: ItemFactory):
        self.ai_object_factory = ai_object_factory
        self.item_factory = item_factory

    #
    # PUBLIC METHODS
    #

    async def create_enemy(self, backstory: str, location: Location) -> Enemy:
        enemy = await self.ai_object_factory.create_enemy(
            backstory=backstory,
            surroundings=location.description
        )
        enemy_weapon = await self.item_factory.create_item_of_type(backstory=backstory, item_type="Weapon")
        enemy.items.append(enemy_weapon)
        return enemy

    async def create_player(self, backstory: str) -> Player:
        player = Player()
        player_weapon = await self.item_factory.create_item_of_type(backstory=backstory, item_type="Weapon")
        player.items.append(player_weapon)
        return player 
