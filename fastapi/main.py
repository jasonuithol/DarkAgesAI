'''
requirements

pip install "uvicorn[standard]"
pip install fastapi
pip install aiofiles

'''
import logging

from typing import Tuple, Any
from random import randint
from enum import Enum, auto

from fastapi import FastAPI, Body
from contextlib import asynccontextmanager

from domain.classes import Player, Enemy, Location, Item
from services.composition import get_world_factory, get_location_factory, get_combatant_factory, get_item_factory
from services.display import display
from services.util import result

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)  # for httpx
logging.getLogger("urllib3").setLevel(logging.DEBUG)  # for requests


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.world_factory = await get_world_factory()
    app.state.location_factory = await get_location_factory()
    app.state.combatant_factory = await get_combatant_factory()
    app.state.item_factory = await get_item_factory()

    # Ensure the world exists.
    app.state.world = await app.state.world_factory.get_world()

    yield

    # teardown logic here
    if app.state.world:
        await app.state.world_factory.save_world(app.state.world)
        display("Game state saved.")
    else:
        app.state.world_factory.delete_world()
        display("Game state deleted, starting new game on restart.")

app = FastAPI(
    root_path="/api",
    lifespan=lifespan
)

#
# Helper functions for INFORMATION HANDLERS
#

def obtain_player() -> Player:
    return app.state.world.player

def obtain_position() -> Tuple[int, int]:
    return obtain_player().get_position()

async def obtain_player_location() -> Location:
    return await app.state.location_factory.get_location(
        world=app.state.world,
        position=obtain_position()
    )

def obtain_enemies() -> list[Enemy]:
    if app.state.world.enemy:
        return [app.state.world.enemy]
    else:
        return []

# TODO: Make a class in utils.py called ActionResponse
async def obtain_allowed_buttons(result_value: str = "OK") -> dict[str, Any]:
    movement_allowed = not app.state.world.enemy
    allowed_buttons = {
        "n": movement_allowed,
        "e": movement_allowed,
        "w": movement_allowed,
        "s": movement_allowed,
        "local_items": any((await obtain_player_location()).items),
        "inventory": any(obtain_player().items),
        "combat": len(obtain_enemies()) > 0
    }
    return result(result_value) | {"allowed_buttons": allowed_buttons}

#
# INFORMATION HANDLERS
#

@app.get("/")
async def read_root():
    return app.state.world.backstory

@app.get("/location")
async def get_location() -> Location:
    return await obtain_player_location()

@app.get("/location/items")
async def get_location_items() -> list[Item]:
    location = await obtain_player_location()
    return location.items

'''
# not actually async, not actually used either.
@app.get("/location/exits")
async def get_location_exits() -> str:
    return app.state.world.build_exits_message(get_position(), include_description=False)
'''

@app.get("/inventory")
async def get_inventory() -> list[Item]:
    return obtain_player().items

@app.get("/enemies")
async def get_enemies() -> list[dict[str, str]]:
    return [{
        "item_type": "Enemy",
        "name": x.name,
        "description": x.description,
        "image": x.image
    } for x in obtain_enemies()] 

#
# Helper functions for ACTION HANDLERS
#

async def start_new_game():
    display("Starting new game...")
    app.state.world = await app.state.world_factory.create_world()

#
# ACTION HANDLERS
#

@app.post("/move")
async def move(player_choice: str = Body()) -> dict[str, Any]:

    class MoveResult(Enum):
        UNKNOWN_COMMAND = auto(),
        ENEMY_PRESENT = auto()

    player = obtain_player()
    old_position = player.get_position()

    if player_choice == "n":
        player.move(dir_y=+1)
    elif player_choice == "s":
        player.move(dir_y=-1)
    elif player_choice == "e":
        player.move(dir_x=+1)
    elif player_choice == "w":
        player.move(dir_x=-1)
    else:
        return await obtain_allowed_buttons(MoveResult.UNKNOWN_COMMAND)

    display(f"You have moved position from {old_position} to {player.get_position()}")

    # random encounter ?
    if randint(0, 100) < 10:  # 10% chance
        app.state.world.enemy = await app.state.combatant_factory.create_enemy(
            backstory=app.state.world.backstory,
            location=await obtain_player_location()
        )

        display(f"You have encountered an enemy: {app.state.world.enemy.name}!")
        return await obtain_allowed_buttons(MoveResult.ENEMY_PRESENT)

    return await obtain_allowed_buttons()

@app.post("/attack")
async def attack() -> dict[str, Any]:

    class AttackResult(Enum):
        NO_ENEMY = auto(),
        NO_PLAYER_WEAPON = auto(),
        NO_ENEMY_WEAPON = auto(),
        VICTORY = auto(),
        DEFEAT = auto()

    player = obtain_player()
    enemy = app.state.world.enemy
    if not enemy:
        return await obtain_allowed_buttons(AttackResult.NO_ENEMY)

    player_weapon = next(
        filter(lambda x: x.item_type == "Weapon", player.items),
        None
    )
    if player_weapon is None:
        return await obtain_allowed_buttons(AttackResult.NO_PLAYER_WEAPON)

    player.attack(opponent=enemy, weapon=player_weapon)
    if enemy.health <= 0:
        app.state.world.enemy = None
        return await obtain_allowed_buttons(AttackResult.VICTORY)

    enemy_weapon = next(
        filter(lambda x: x.item_type == "Weapon", enemy.items),
        None
    )
    if enemy_weapon is None:
        return await obtain_allowed_buttons(AttackResult.NO_ENEMY_WEAPON)

    enemy.attack(opponent=player, weapon=enemy_weapon)
    if player.health <= 0:
        await start_new_game()
        return await obtain_allowed_buttons(AttackResult.DEFEAT)

    else:
        return await obtain_allowed_buttons()

@app.post("/take")
async def take(item_name: str = Body()) -> dict[str, Any]:
    location = await obtain_player_location()
    obtain_player().take_item(item_name, location)
    return await obtain_allowed_buttons()

@app.post("/drop")
async def drop(item_name: str = Body()) -> dict[str, Any]:
    location = await obtain_player_location()
    obtain_player().drop_item(item_name, location)
    return await obtain_allowed_buttons()
