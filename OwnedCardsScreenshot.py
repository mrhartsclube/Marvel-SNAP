import os
import json
import io
import subprocess

# Check if requests package is installed, install it if not
try:
    import requests
except ImportError:
    subprocess.check_call(["pip", "install", "requests"])
    import requests

# Check if Pillow package is installed, install it if not
try:
    from PIL import Image
except ImportError:
    subprocess.check_call(["pip", "install", "pillow"])
    from PIL import Image


card_width = 210    # In pixels
num_columns = 10    # Number of columns for final grid
json_path = ""

# Search for the card collection file
base_path = r"C:\Users"
for folder in os.listdir(base_path):
    folder_path = os.path.join(base_path, folder)
    json_path_s = os.path.join(folder_path, r"AppData\LocalLow\Second Dinner\SNAP\Standalone\States\nvprod\CollectionState.json")
    if os.path.isfile(json_path_s):
        json_path = json_path_s

# Read the JSON file as binary and remove BOM characters
with open(json_path, "rb") as file:
    json_bytes = file.read()

# Remove BOM characters from JSON bytes
if json_bytes.startswith(b'\xef\xbb\xbf'):
    json_bytes = json_bytes[3:]

# Convert the JSON bytes to a string
json_text = json_bytes.decode("utf-8")

# Convert the JSON text to a JSON object
try:
    data = json.loads(json_text)
except json.JSONDecodeError as e:
    print("Error: Failed to parse JSON file:", e)
    exit(1)

# Extracting the array of objects
cards = data["ServerState"]["Cards"]

# Filter out cards without a valid TimeCreated field
valid_cards = [card for card in cards if "TimeCreated" in card]

# Create a set to store encountered CardDefId values
encountered_card_ids = set()

# Sort the cards by CardDefId (alphabetically)
valid_cards = sorted(valid_cards, key=lambda x: x.get("CardDefId", ""))

# Sort the cards by CardDefId (alphabetically) and remove duplicates
sorted_cards = []
for card in valid_cards:
    card_def_id = card.get("CardDefId")
    if card_def_id not in encountered_card_ids:
        sorted_cards.append(card)
        encountered_card_ids.add(card_def_id)

# Calculate the number of columns and rows
num_rows = (len(sorted_cards) + num_columns - 1) // num_columns

# Calculate the grid size
grid_width = num_columns * card_width
grid_height = num_rows * card_width

# Create a blank grid image with the desired size and background color
background_color = "#13171b"
grid_image = Image.new("RGB", (grid_width, grid_height), background_color)

# Resize and paste the images onto the grid
for i, card in enumerate(sorted_cards):
    card_def_id = card.get("CardDefId")
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{i+1}/{len(sorted_cards)}: {card_def_id}", end="", flush=True)
    image_url = f"https://static.marvelsnap.pro/cards/{card_def_id}.webp"

    # Download the image
    response = requests.get(image_url)
    if response.status_code == 200:
        image_bytes = response.content

        # Create PIL Image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Resize the image
        img = img.resize((card_width, card_width),Image.Resampling.LANCZOS)

        # Calculate the position to paste the image on the grid
        column = i % num_columns
        row = i // num_columns
        position = (column * card_width, row * card_width)

        # Paste the image onto the grid
        grid_image.paste(img, position)

# Save the grid image
grid_image.save("image_grid.png")