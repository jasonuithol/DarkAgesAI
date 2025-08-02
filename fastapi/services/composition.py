import aiofiles
import importlib

from domain.config import Config

from services.aiengines import AiEngine
from services.ai_object_factory import AiObjectFactory
from services.world_factory import WorldFactory
from services.location_factory import LocationFactory
from services.combatant_factory import CombatantFactory
from services.item_factory import ItemFactory

_config: Config = None
_ai_engine: AiEngine = None
_ai_object_factory: AiObjectFactory = None
_world_factory: WorldFactory = None
_location_factory: LocationFactory = None
_combatant_factory: CombatantFactory = None
_item_factory: ItemFactory = None

async def get_config() -> Config:
    global _config
    if not _config:
        async with aiofiles.open("config.json", "r") as file:
            config_data = await file.read()
            _config = Config.model_validate_json(config_data)
    return _config

async def get_ai_engine() -> AiEngine:
    global _ai_engine
    if not _ai_engine:
        # get dependencies
        config = await get_config()

        # Get the constructor for the AiEngine provider.
        engine_config = config.aiengines[config.chosen_aiengine]
        aiengines_module = importlib.import_module("services.aiengines")
        constructor = getattr(aiengines_module, engine_config.engine_class)

        if engine_config.token_file:
            # Read the token from the file specified in the config, and add the token value to the parameters.
            async with aiofiles.open(engine_config.token_file, "r") as file:
                token_value = await file.read()
            parameters = engine_config.properties | {"token": token_value}
        else:
            parameters = engine_config.properties | {}
        _ai_engine = constructor(**parameters)
    return _ai_engine

async def get_ai_object_factory() -> AiObjectFactory:
    global _ai_object_factory
    if not _ai_object_factory:
        # get dependencies
        ai_engine = await get_ai_engine()

        _ai_object_factory = AiObjectFactory(
            ai_engine=ai_engine
        )
    return _ai_object_factory

async def get_world_factory() -> WorldFactory:
    global _world_factory
    if not _world_factory:
        # get dependencies
        config = await get_config()
        ai_object_factory = await get_ai_object_factory()
        combatant_factory = await get_combatant_factory()
        item_factory = await get_item_factory()

        _world_factory =  WorldFactory(
            ai_object_factory=ai_object_factory,
            combatant_factory=combatant_factory,
            item_factory=item_factory,
            config=config
        )
    return _world_factory
    
async def get_location_factory() -> LocationFactory:
    global _location_factory
    if not _location_factory:
        # get dependencies
        ai_object_factory = await get_ai_object_factory()
        item_factory = await get_item_factory()

        _location_factory = LocationFactory(
            ai_object_factory=ai_object_factory,
            item_factory=item_factory
        )
    return _location_factory

async def get_combatant_factory() -> CombatantFactory:
    global _combatant_factory
    if not _combatant_factory:
        #get dependencies
        ai_object_factory = await get_ai_object_factory()
        item_factory = await get_item_factory()

        _combatant_factory = CombatantFactory(
            ai_object_factory=ai_object_factory,
            item_factory=item_factory
        )
    return _combatant_factory

async def get_item_factory() -> ItemFactory:
    global _item_factory
    if not _item_factory:
        #get dependencies
        ai_object_factory = await get_ai_object_factory()

        _item_factory = ItemFactory(
            ai_object_factory=ai_object_factory
        )
    return _item_factory