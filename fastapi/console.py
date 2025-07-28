import random

from domain.classes import Location, World, Item, Player
from services.factories import AiEngine, AiChatContext, AiObjectFactory, WorldFactory 
from services.display import display, BOLD, CYAN, RED, GREEN, RESET, YELLOW

#
# CONSOLE ONLY
#
    
def look(self):
    position = self.get_position()
    location = self.get_location() 
    if location.image:
        location.image.show()
    self.display(location.description)
    self.display(BOLD + world.build_exits_message(position, include_description=False))
    if location.items:
        self.display(f"{RED}You see the following items: {BOLD}{list(map(lambda x: x.name, location.items))}")        
    if location.sound:
        location.sound.play()

def examine(self, item_name):
    item = self.find_item(item_name, location.items + self.items)
    if item:
        self.display(f"{CYAN}[{item.item_type}] {item.description}")
    
def inventory(self):
    self.display(f"{CYAN}You have the following items: {BOLD}{list(map(lambda x: x.name, self.items))}")
    
# ===============================================
# GLOBAL CONTEXT STARTS HERE
# ===============================================

with open("token.txt", "r") as file:

    ai = AiEngine(
        text_model="meta-llama/Meta-Llama-3-8B-Instruct", # 8,962 token limit
        image_model="black-forest-labs/FLUX.1-dev", 
        sound_model="suno/bark-small", # not currently used
        token=file.read()
    )

world = World(ai)
print(YELLOW + world.backstory)

player = Player(world=world)

# creates and starts off at the initial location
location = player.get_location()

while True:
        
    player.display(f"{BOLD}You are at {location.name} {player.get_position()}")

    if location.is_new == True:
        make_item = random.choice([True, False])
        if make_item == True:
            item = world.create_item()
            location.add_item(item)
        player.look()
        location.is_new = False

    player_choice = input(f"{RESET}{BOLD}{GREEN}\n Your choice: ")

    # TODO: Make all of these methods on a Player class.

    if player_choice == "n":
        player.move(dir_y = +1)
    if player_choice == "s":
        player.move(dir_y = -1)
    if player_choice == "e":
        player.move(dir_x = +1)
    if player_choice == "w":
        player.move(dir_x = -1)
    if player_choice == "quit":
        exit()
    if player_choice == "look":
        player.look()
    if player_choice.startswith("examine "):
        item_name = player_choice[8:]
        player.examine(item_name)
    if player_choice.startswith("take "):
        item_name = player_choice[5:]
        player.take_item(item_name)
    if player_choice.startswith("drop "):
        item_name = player_choice[5:]
        player.drop_item(item_name)
    if player_choice == "i":
        player.inventory()

    # If there is no location here, one will be built by AI for us.
    location = player.get_location() 
