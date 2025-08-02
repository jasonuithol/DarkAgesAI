from enum import Enum

def result(value):
    if value is Enum:
        return result(value.value)

    return {"result": str(value)}

