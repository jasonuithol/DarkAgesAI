'''
requirements:

pip install pydantic

Create a "Read" token at the HuggingFace website (free)

'''

from services.display import display, CYAN

from typing import Optional, Dict, Tuple
from pydantic import BaseModel, Field

class Item(BaseModel):
    item_type: str
    name: str
    description: Optional[str]
    image: str # a base64 encoded PNG
        
class Location(BaseModel):
    name: str
    description: str
    image: Optional[str] # a base64 encoded PNG
    items: list[Item] = Field(default_factory=list)

class Player(BaseModel):
    x: int = 0
    y: int = 0
    items: list[Item] = Field(default_factory=list)
        
    def get_position(self):
        return self.x, self.y
       
    def move(self, dir_x = 0, dir_y = 0):
        self.x += dir_x
        self.y += dir_y
 
    def find_item(self, item_name, items):
        return next(filter(lambda x: x.name == item_name, items), None)
 
    def take_item(self, item_name, location):
        item = self.find_item(item_name, location.items)
        if item:
            self.items.append(item)
            location.items.remove(item)
            display(f"{CYAN}You have taken {item_name}")
            return True
        else:
            display(f"Could not find item: {item_name}")
            return False
        
    def drop_item(self, item_name, location):
        item = self.find_item(item_name, self.items)
        if item:
            self.items.remove(item)
            location.items.append(item)
            display(f"{CYAN}You have dropped {item_name}")
            return True
        else:
            display(f"Do not have item: {item_name}")
            return False
            
class World(BaseModel):
    backstory: str
    player: Player
    locations: Dict[Tuple[int, int], Location] = Field(default_factory=dict)

    # a special location that is the nowhere location.
    uncharted: Location = Field(
        default_factory=lambda: Location(
            name="uncharted", 
            description="this location has not been discovered yet", 
            image=None
        ),
        exclude=True
    )
           
    def get_exit_locations(self, position):
        x, y = position
        return {
            "n": self.locations.get((x, y + 1), self.uncharted),
            "s": self.locations.get((x, y - 1), self.uncharted),
            "e": self.locations.get((x + 1, y), self.uncharted),
            "w": self.locations.get((x - 1, y), self.uncharted)
        }
 
    def build_exits_message(self, position, include_description=False):
        exits = self.get_exit_locations(position)
        return (
            f"To the north is {exits['n'].name} {exits['n'].description if include_description else ''}\n"
             f"To the east is {exits['e'].name} {exits['e'].description if include_description else ''}\n"
             f"To the west is {exits['w'].name} {exits['w'].description if include_description else ''}\n"
            f"To the south is {exits['s'].name} {exits['s'].description if include_description else ''}\n"
        )


   
