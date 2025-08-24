'''
requirements:

pip install pydantic

Create a "Read" token at the HuggingFace website (free)

'''

from __future__ import annotations
from random import randint, choice
from services.display import display, CYAN

from typing import Optional, Dict, Tuple
from pydantic import BaseModel, Field

class Item(BaseModel):
    item_type: str
    name: str
    description: Optional[str]
    image_prompt: Optional[str]
    image: str # a base64 encoded PNG

    def to_typed_item(self) -> Item:
        constructor = globals().get(self.item_type.capitalize(), None)
        if constructor:
            typed = constructor(**self.dict())
            return typed
        else:
            raise ValueError(f"Unknown item type: {self.item_type}")

def generate_damage_field() -> int:
    return Field(default_factory=lambda: (randint(1, 6), randint(7, 12), choice([0, 0, 0, 0, 0, 1, 1, 2, 3])))

def generate_requirement_field() -> int:
    return Field(default_factory=lambda: max(1, randint(1, 10) - 5))

def generate_bonus_field() -> int:
    return Field(default_factory=lambda: choice([0, 0, 0, 0, 0, 1, 1, 2, 3]))

class Weapon(Item):
    damage: Tuple[int,int,int] = generate_damage_field()
    required_strength: int = generate_requirement_field()
    required_agility: int = generate_requirement_field()
    required_intelligence: int = generate_requirement_field()

class Spellbook(Item):
    damage: Tuple[int,int,int] = generate_damage_field()
    required_intelligence: int = generate_requirement_field()
    required_constitution: int = generate_requirement_field()
    required_health: int = generate_requirement_field()
    required_mana: int = generate_requirement_field()

class Armour(Item):
    defence: int = Field(default_factory=lambda: randint(1, 10))
    required_strength: int = generate_requirement_field()
    required_intelligence: int = generate_requirement_field()

class Relic(Item):
    strength_bonus: int = generate_bonus_field()
    agility_bonus: int = generate_bonus_field()
    health_bonus: int = generate_bonus_field()

class Gem(Item):
    intelligence_bonus: int = generate_bonus_field()
    constitution_bonus: int = generate_bonus_field()
    mana_bonus: int = generate_bonus_field() 

class Potion(Item):
    health_bonus: int = generate_bonus_field()
    mana_healed: int = generate_bonus_field()

class Money(Item):
    amount: int = Field(default_factory=lambda: randint(1, 100))

class Location(BaseModel):
    name: str
    description: str
    image: Optional[str] # a base64 encoded PNG
    items: list[Item] = Field(default_factory=list)

def generate_ability_field() -> int:
    return Field(default_factory=lambda: randint(1, 20))

class Combatant(BaseModel):
    strength: int = generate_ability_field()
    agility: int = generate_ability_field()
    intelligence: int = generate_ability_field()
    consitution: int = generate_ability_field()

    level: int = Field(default_factory=lambda: randint(1, 10))
    experience: int = 0
    health: float = 1.0
    mana: float = 1.0

    items: list[Item] = Field(default_factory=list)

    def max_health(self) -> int:
        return self.consitution * self.level

    def max_mana(self) -> int:
        return self.intelligence * self.level

    def attack(self, opponent: Combatant, weapon: Item):
        to_hit = self.agility - opponent.agility + randint(0, 20)
        if to_hit > 0:
            damage = randint(weapon.damage[0], weapon.damage[1]) + weapon.damage[2] + self.strength - sum(armour.defence for armour in opponent.items if isinstance(armour, Armour))
            damage_percent = damage / opponent.max_health()
            opponent.health -= damage_percent

class Enemy(Combatant):
    name: str
    description: str
    image: Optional[str] = None  # base64 encoded PNG
        
class Player(Combatant):
    x: int = 0
    y: int = 0
        
    def get_position(self) -> Tuple[int, int]:
        return self.x, self.y
       
    def move(self, dir_x = 0, dir_y = 0):
        self.x += dir_x
        self.y += dir_y

    def find_item(self, item_name: str, items: list[Item]) -> Optional[Item]:
        return next(filter(lambda x: x.name == item_name, items), None)

    def take_item(self, item_name: str, location: Location) -> bool:
        item = self.find_item(item_name, location.items)
        if item:
            self.items.append(item)
            location.items.remove(item)
            display(f"{CYAN}You have taken {item_name}")
            return True
        else:
            display(f"Could not find item: {item_name}")
            return False
        
    def drop_item(self, item_name: str, location: Location) -> bool:
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
    enemy: Optional[Enemy] = None

    # a special location that is the nowhere location.
    uncharted: Location = Field(
        default_factory=lambda: Location(
            name="uncharted", 
            description="this location has not been discovered yet", 
            image=None
        ),
        exclude=True
    )

    def get_exit_locations(self, position: Tuple[int, int]) -> Dict[str, Location]:
        x, y = position
        return {
            "n": self.locations.get((x, y + 1), self.uncharted),
            "s": self.locations.get((x, y - 1), self.uncharted),
            "e": self.locations.get((x + 1, y), self.uncharted),
            "w": self.locations.get((x - 1, y), self.uncharted)
        }

    def build_exits_message(self, position: Tuple[int, int], include_description: bool = False) -> str:
        exits = self.get_exit_locations(position)
        return (
            f"To the north is {exits['n'].name} {exits['n'].description if include_description else ''}\n"
             f"To the east is {exits['e'].name} {exits['e'].description if include_description else ''}\n"
             f"To the west is {exits['w'].name} {exits['w'].description if include_description else ''}\n"
            f"To the south is {exits['s'].name} {exits['s'].description if include_description else ''}\n"
        )

