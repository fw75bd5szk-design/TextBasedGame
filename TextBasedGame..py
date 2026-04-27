"""
----------Gates & Hunters---------
----------Daniel De Leon----------
"""

# ----- Direction helpers -----
OPP = {"North": "South", "South": "North", "East": "West", "West": "East"}
DIR_ALIAS = {"n": "North", "s": "South", "e": "East", "w": "West"}

# ----- World ; (one item/room; boss in Boss Chamber) -----
rooms = {
    "Start": {"West": "Training Grounds"},
    "Training Grounds": {
        "East": "Start",
        "West": "Hunters Guild Hall",
        "South": "Dungeon Entrance",
        "item": "Healing Potion",
    },
    "Hunters Guild Hall": {
        "East": "Training Grounds",
        "item": "Resurrection Stone",
    },
    "Dungeon Entrance": {
        "North": "Training Grounds",
        "East": "Orc Fortress",
        "South": "Goblin Nest",
        "West": "Boss Chamber",
        "item": "Dungeon Key",
    },
    "Orc Fortress": {
        "West": "Dungeon Entrance",
        "North": "Final Gate",
        "item": "Rank Badge",
    },
    "Final Gate": {"South": "Orc Fortress", "item": "Ancient Relic"},
    "Goblin Nest": {
        "North": "Dungeon Entrance",
        "East": "Shadow Realm",
        "item": "Mana Crystal",
    },
    "Shadow Realm": {
        "West": "Goblin Nest",
        "North": "Final Gate",  # hidden path via Shadow Orb
        "item": "Shadow Orb",
    },
    "Boss Chamber": {
        "East": "Dungeon Entrance",
        "villain": "Monarch of Destruction",
    },
}

HELP_TEXT = """
Commands:
  go North/South/East/West  (n/s/e/w)
  get 'item name'
  help
  quit
"""

STATUS_MSG = {
    "invalid_direction": (
        "Invalid direction. Use North/South/East/West (or n/s/e/w)."
    ),
    "unknown_room": "Current room is not in the map (configuration error).",
    "blocked": "You can’t go that way.",
    "off_map": "That exit points outside the map (configuration error).",
}

LOCK_MSG = {
    "need_dungeon_key": "The door is locked. You need the Dungeon Key.",
    "need_rank_badge": "A barrier blocks the way. Show your Rank Badge.",
    "need_shadow_orb": "A hidden passage hums. The Shadow Orb is required.",
}

# (room, direction) -> (required item, status key)
LOCKS = {
    ("Dungeon Entrance", "East"): ("Dungeon Key", "need_dungeon_key"),
    ("Orc Fortress", "North"): ("Rank Badge", "need_rank_badge"),
    ("Shadow Realm", "North"): ("Shadow Orb", "need_shadow_orb"),
}


def get_new_state(direction: str, current_room: str) -> tuple[str, str]:
    """
    Return (next_room, status) using the global rooms map.

    Status ∈ {"ok", "invalid_direction", "unknown_room",
              "blocked", "off_map"}.
    """
    if not isinstance(direction, str):
        return current_room, "invalid_direction"
    direction = direction.strip()
    if not direction:
        return current_room, "invalid_direction"

    d = DIR_ALIAS.get(direction.lower(), direction.capitalize())
    if d not in OPP:
        return current_room, "invalid_direction"

    room_data = rooms.get(current_room)
    if room_data is None:
        return current_room, "unknown_room"

    next_room = room_data.get(d)
    if not next_room:
        return current_room, "blocked"

    if next_room not in rooms:
        return current_room, "off_map"

    return next_room, "ok"


def show_status(current_room: str, inventory: list, rooms_dict: dict) -> None:
    """Shows room, room item, inventory, and available exits."""
    print(f"\nYou are in the {current_room}")
    item = rooms_dict[current_room].get("item")
    if item:
        print(f"You see a {item}")
    print(f"Inventory: {inventory}")
    exits = [k for k in rooms_dict[current_room] if k in OPP]
    exits.sort()
    print(f"Exits: {', '.join(exits) if exits else 'None'}")
    print("-" * 30)
    print("Enter your move:")


def main():
    # Intro & instructions :)
    print("""
    ==========================================
                 GATES & HUNTERS
    ==========================================

    Goal:
      - Find the Ancient Relic to weaken the Monarch of Destruction.
      - Some paths are locked by specific items.
      - You WIN if you face the Monarch with the Ancient Relic.
      - If you face the Monarch early, a Resurrection Stone (if held)
        will revive you once.

    Commands:
      go North/South/East/West (n/s/e/w also work)
      get 'item name'   help   quit
    ==========================================
    """)

    current_room = "Start"
    inventory: list[str] = []

    ACTION = {"help": 0, "quit": 1, "get": 2, "go": 3}

    loop = True
    while loop:
        show_status(current_room, inventory, rooms)

        try:
            raw = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nInput stream closed. Exiting.")
            loop = False
            continue

        raw = (raw or "").strip()
        if not raw:
            print("Please enter a command.")
            continue

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) == 2 else ""
        action = ACTION.get(cmd, -1)


        if action == 0:  # help
            print(HELP_TEXT)
            continue
        if action == 1:  # quit
            print("Thanks for playing. See you at the next Gate.")
            loop = False
        if action == -1:
            print("Invalid command. Try 'go North', get 'item name', "
                  "'help', or 'quit'.")
            continue

        if action == 2:  # get
            requested = arg.strip().strip("'\"")
            item_here = rooms[current_room].get("item")
            can_take = (requested and item_here and
                        requested.lower() == item_here.lower())
            if not can_take:
                print("Can’t get that.")
                continue
            inventory.append(item_here)
            rooms[current_room].pop("item", None)
            print(f"{item_here} acquired!")

            FLAVOR = {
                "Dungeon Key": "You feel deeper doors might open now...",
                "Rank Badge": "A barrier may yield to your strength.",
                "Shadow Orb": "Hidden passages whisper to you.",
                "Ancient Relic": (
                    "Power surges. The Monarch can be weakened."
                ),
                "Resurrection Stone": (
                    "A faint warmth promises a second chance."
                ),
            }
            tip = FLAVOR.get(item_here)
            if tip:
                print(tip)
            continue

        # action == 3 -> go
        # ----- SINGLE movement -----
        next_room, status = get_new_state((arg or "").strip(), current_room)

        if status != "ok":
            print(STATUS_MSG[status])
            continue

        d_norm = DIR_ALIAS.get((arg or "").lower(), (arg or "").title())
        need = LOCKS.get((current_room, d_norm))
        if need and need[0] not in inventory:
            print(LOCK_MSG[need[1]])
            continue

        current_room = next_room

        # Boss logic after landing
        if "villain" in rooms[current_room]:
            has_relic = "Ancient Relic" in inventory
            has_stone = "Resurrection Stone" in inventory
            # outcome index: 0=lose, 1=revive, 2=win
            idx = (has_stone and not has_relic) + (has_relic * 2)

            if idx == 1:  # revive
                inventory.remove("Resurrection Stone")
                print("\nThe Monarch overwhelms you...")
                print("But the Resurrection Stone burns bright!")
                print("You awaken at the Start, shaken but alive.")
                current_room = "Start"
                continue

            texts = [
                ("\nYou entered the Boss Chamber too soon...",
                 "The Monarch of Destruction overwhelms you.",
                 "NOM NOM...GAME OVER!"),
                # idx 1 handled above
                ("\nYou confront the Monarch of Destruction!",
                 "Your relics resonate in unison, defeating the foe.",
                 "Congratulations! You collected the relic and won!"),
            ]
            # pick 0 for lose, 1 for win
            t = texts[1 if idx == 2 else 0]
            print(t[0])
            print(t[1])
            print(t[2])
            print("Thanks for playing the game. Hope you enjoyed it.")
            loop = False


if __name__ == "__main__":
    main()
