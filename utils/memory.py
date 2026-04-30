import json
import os

MEMORY_PATH = "memory/memory.json"

def load_memory():
    if not os.path.exists(MEMORY_PATH):
        return []

    with open(MEMORY_PATH, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)

def add_entry(memory, entry):
    memory.append(entry)
    save_memory(memory)