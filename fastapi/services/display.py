from typing import Any

# ANSI escape codes
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"

# Foreground (text) colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Background colors
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"
        
def display(message: Any): 
    print(f"{RESET}\n\n{message}")
