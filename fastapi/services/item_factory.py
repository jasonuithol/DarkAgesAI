"""
requirements:
"""
import domain.classes
from domain.classes import Item
from services.ai_object_factory import AiObjectFactory

class ItemFactory:
    def __init__(self, ai_object_factory: AiObjectFactory):
        self.ai_object_factory = ai_object_factory
    
    #
    # PUBLIC METHODS
    #

    def subtypify_item(self, item: Item) -> Item:
        constructor = getattr(domain.classes, item.item_type)
        subtypified_item = constructor(**item.dict())
        return subtypified_item

    async def create_item_of_type(self, backstory: str, item_type: str) -> Item:
        item = await self.ai_object_factory.create_item_of_type(
            backstory=backstory,
            item_type=item_type
        )
        return self.subtypify_item(item)

    async def create_item(self, backstory: str) -> Item:
        item = await self.ai_object_factory.create_item(
            backstory=backstory,
        )
        return self.subtypify_item(item)



