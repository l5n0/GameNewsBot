import json

# Load existing game colors from JSON
def load_game_colors():
    with open('game_colors.json', 'r') as json_file:
        return json.load(json_file)

# Save updated game colors to JSON
def save_game_colors(game_colors):
    with open('game_colors.json', 'w') as json_file:
        json.dump(game_colors, json_file, indent=4)

# Function to set the color for a game
def set_game_color(game_id, color):
    game_colors = load_game_colors()
    # Check if the game already exists
    game_exists = False
    for game in game_colors["games"]:
        if game["game_id"] == game_id:
            game["color"] = color
            game_exists = True
            break
    if not game_exists:
        # Add new game entry
        game_colors["games"].append({"game_id": game_id, "color": color})
    save_game_colors(game_colors)
    return f"Color for game ID {game_id} set to {color}."
