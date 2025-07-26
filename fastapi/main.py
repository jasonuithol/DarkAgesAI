'''
requirements

pip install "uvicorn[standard]"
pip install fastapi
pip install aiofiles

'''

import base64
import random
import asyncio
import aiofiles
import logging

from domain.classes import Location, World, Item, Player
from services.factories import AiEngine, AiChatContext, AiObjectFactory, WorldFactory
from services.display import display

from io import BytesIO
from fastapi import FastAPI, Body
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)  # for httpx
logging.getLogger("urllib3").setLevel(logging.DEBUG)  # for requests

@asynccontextmanager
async def lifespan(app: FastAPI):

    # I/O call to disk
    async with aiofiles.open("token.txt", "r") as file:
        ai_engine = AiEngine(
            text_model="meta-llama/Meta-Llama-3-8B-Instruct", # 8,962 token limit
            image_model="black-forest-labs/FLUX.1-dev",
            token=await file.read()
        )

    app.state.world_factory = WorldFactory(
        ai_object_factory = AiObjectFactory(
            ai_engine=ai_engine
        )
    )
    
    # Ensure the world exists.
    app.state.world = await app.state.world_factory.get_world()

    yield

    # teardown logic here
    await app.state.world_factory.save_world(app.state.world)
    display("Game state saved.")

app = FastAPI(
    root_path="/api",
    lifespan=lifespan
)

# Helper functions

def get_player():
    return app.state.world.player

def get_position():
    return get_player().get_position()

async def get_player_location():
    return await app.state.world_factory.get_location(get_position())

# HANDLERS

@app.get("/")
async def read_root():
    return app.state.world.backstory 

@app.get("/location")
async def get_locationX(): 
    # might make an I/O call to an AI model.
    location = await get_player_location()
    
    return {
        "name": location.name,
        "description": location.description,
        "image": location.image
    }

# not used
@app.get("/locations")
async def get_locations():
    return [{"key": key, "location_name": value.name} for key, value in app.state.world.locations.items()]

@app.get("/location/items")
async def get_location_items():
    # might make an I/O call to an AI model.
    location = await get_player_location()
    return [x.dict() for x in location.items]

# not actually async
@app.get("/location/exits")
async def get_location_exits():
    return app.state.world.build_exits_message(get_position(), include_description=False)

@app.post("/move")
async def move(player_choice: str = Body()): 
    player = get_player()
    old_position = player.get_position() 
    
    if player_choice == "n":
        player.move(dir_y = +1)
    elif player_choice == "s":
        player.move(dir_y = -1)
    elif player_choice == "e":
        player.move(dir_x = +1)
    elif player_choice == "w":
        player.move(dir_x = -1)
    else:
        return {"result": "unknown command"}
        
    display(f"You have moved position from {old_position} to {player.get_position()}")
    return {"result": "OK"}

@app.get("/inventory")
async def get_inventory():    
    return [
        x.dict()
        for x in get_player().items
    ]

@app.post("/take")
async def choice(item_name: str = Body()):
    location = await get_player_location()
    get_player().take_item(item_name, location)
    return {"result": "OK"}

@app.post("/drop")
async def choice(item_name: str = Body()):
    location = await get_player_location()
    get_player().drop_item(item_name, location)
    return {"result": "OK"}
