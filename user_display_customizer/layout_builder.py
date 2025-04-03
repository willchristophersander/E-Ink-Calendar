# layout_builder.py

import math
import os
import json
from PIL import Image, ImageDraw, ImageFont

def get_layout_preferences():
    """Prompt the user for layout settings."""
    while True:
        try:
            days = int(input("How many days do you want to display? "))
            if days < 1:
                print("Please enter a number greater than 0.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")
    
    display_mode = input("How should events be displayed? Enter 'list' for a long list or 'rect' for rectangular display: ").strip().lower()
    if display_mode not in ("list", "rect"):
        print("Unknown display mode. Defaulting to list mode.")
        display_mode = "list"
    
    while True:
        try:
            rows = int(input("How many rows do you want? "))
            if rows < 1:
                print("Please enter a number greater than 0.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")
    
    return days, display_mode, rows

def get_image_preferences():
    """Prompt the user for image inclusion and options."""
    include_ans = input("Would you like to include an image in the display? (y/n): ").strip().lower()
    if include_ans in ("y", "yes"):
        image_position = input("Where should the image be placed? (left, center, right): ").strip().lower()
        if image_position not in ("left", "center", "right"):
            print("Invalid position. Defaulting to center.")
            image_position = "center"
        image_size = input("What size should the image be? Options: 'half', 'third', 'auto': ").strip().lower()
        if image_size not in ("half", "third", "auto"):
            print("Invalid size option. Defaulting to 'auto'.")
            image_size = "auto"
        image_name = input("Enter the image's file name (with extension): ").strip()
        return {
            "include_image": True,
            "image_position": image_position,
            "image_size": image_size,
            "image_name": image_name
        }
    else:
        return {"include_image": False}

def generate_layout_preview(days, display_mode, rows, image_opts=None, width=800, height=480):
    """
    Generates a preview image for the display layout.
    
    For rectangular mode, divides the image into cells (rows x columns) and writes the day title on each cell.
    For list mode, writes each day and a placeholder for events in a vertical list.
    If image_opts is provided and include_image is True, opens the specified image, resizes it, and pastes it
    at the specified location.
    """
    # Create a new white image
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Use a simple default font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font = ImageFont.load_default()

    if display_mode == "rect":
        # Calculate number of columns based on days and rows
        cols = math.ceil(days / rows)
        cell_width = width // cols
        cell_height = height // rows
        
        for row in range(rows):
            for col in range(cols):
                day_index = row * cols + col
                if day_index < days:
                    # Coordinates for this cell
                    x0 = col * cell_width
                    y0 = row * cell_height
                    x1 = x0 + cell_width
                    y1 = y0 + cell_height
                    # Draw a rectangle (cell)
                    draw.rectangle([x0, y0, x1, y1], outline='black', width=2)
                    # Draw the day title at the top center of the cell
                    day_title = f"Day {day_index + 1}"
                    bbox = draw.textbbox((0, 0), day_title, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                    text_x = x0 + (cell_width - text_w) // 2
                    text_y = y0 + 5
                    draw.text((text_x, text_y), day_title, fill='black', font=font)
    else:  # list mode
        line_height = 20
        y = 10
        for day in range(days):
            text = f"Day {day + 1}: [Event 1, Event 2, ...]"
            draw.text((10, y), text, fill='black', font=font)
            y += line_height
            if y > height - line_height:
                break

    # If image options are provided and include_image is True, load and paste the image.
    if image_opts and image_opts.get("include_image"):
        try:
            image_file = image_opts["image_name"]
            # If the provided image name is not an absolute path, assume it is in data/images/
            if not os.path.isabs(image_file):
                image_file = os.path.join("data", "images", image_file)
            img_to_include = Image.open(image_file)
        except Exception as e:
            print(f"Error opening image {image_opts['image_name']}: {e}")
            img_to_include = None

        if img_to_include:
            # Determine new width based on option
            if image_opts["image_size"] == "half":
                new_width = width / 2
            elif image_opts["image_size"] == "third":
                new_width = width / 3
            else:  # auto or fallback
                new_width = width / 2

            # Maintain aspect ratio
            orig_width, orig_height = img_to_include.size
            ratio = orig_height / orig_width
            new_height = int(new_width * ratio)
            new_width = int(new_width)
            resized_img = img_to_include.resize((new_width, new_height))

            # Determine x, y based on position
            if image_opts["image_position"] == "left":
                x = 0
            elif image_opts["image_position"] == "center":
                x = (width - new_width) // 2
            elif image_opts["image_position"] == "right":
                x = width - new_width
            else:
                x = 0  # default to left

            y = (height - new_height) // 2  # center vertically

            # Paste the resized image onto the preview image
            img.paste(resized_img, (x, y))
    
    return img

def list_config_files():
    """List available configuration files in the display_configs folder."""
    folder = "display_configs"
    os.makedirs(folder, exist_ok=True)
    files = [f for f in os.listdir(folder) if f.endswith(".json")]
    return files

def load_existing_config():
    """Allow the user to select an existing configuration."""
    files = list_config_files()
    if not files:
        print("No existing configuration files found.")
        return None
    print("Existing configuration files:")
    for idx, fname in enumerate(files):
        print(f"{idx+1}: {fname}")
    while True:
        try:
            choice = int(input("Select a configuration by number: "))
            if 1 <= choice <= len(files):
                folder = "display_configs"
                filepath = os.path.join(folder, files[choice - 1])
                with open(filepath, "r") as f:
                    config = json.load(f)
                return config
            else:
                print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a valid number.")

def edit_config(existing_config):
    """Interactively edit an existing configuration."""
    def prompt_update(key, current_value):
        new_value = input(f"Enter new value for {key} (current: {current_value}) or press Enter to keep: ").strip()
        return new_value if new_value != "" else current_value

    print("Editing configuration...")
    existing_config["days"] = int(prompt_update("days", existing_config.get("days", 0)))
    existing_config["display_mode"] = prompt_update("display_mode", existing_config.get("display_mode", "list"))
    existing_config["rows"] = int(prompt_update("rows", existing_config.get("rows", 1)))
    
    # Edit image options
    image_opts = existing_config.get("image_options", {"include_image": False})
    include_img = prompt_update("include_image (True/False)", image_opts.get("include_image", False))
    if isinstance(include_img, str):
        include_img = include_img.lower() in ("true", "yes", "y")
    image_opts["include_image"] = include_img
    if include_img:
        image_opts["image_position"] = prompt_update("image_position", image_opts.get("image_position", "center"))
        image_opts["image_size"] = prompt_update("image_size", image_opts.get("image_size", "auto"))
        image_opts["image_name"] = prompt_update("image_name", image_opts.get("image_name", ""))
    existing_config["image_options"] = image_opts
    return existing_config

def save_configuration(config):
    """
    Saves the given configuration (a dict) to a JSON file in the display_configs folder.
    """
    folder = "display_configs"
    os.makedirs(folder, exist_ok=True)
    name = input("Enter a name for this configuration: ").strip()
    filepath = os.path.join(folder, f"{name}.json")
    with open(filepath, "w") as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to {filepath}")

def main():
    # At the start, ask if the user wants to create a new configuration or edit an existing one.
    choice = input("Would you like to create a new configuration or edit an existing one? (new/edit): ").strip().lower()
    if choice in ("new", "n"):
        days, display_mode, rows = get_layout_preferences()
        image_opts = get_image_preferences()
        config = {
            "days": days,
            "display_mode": display_mode,
            "rows": rows,
            "image_options": image_opts
        }
    elif choice in ("edit", "e"):
        existing_config = load_existing_config()
        if not existing_config:
            print("No existing configuration found. Creating a new configuration instead.")
            days, display_mode, rows = get_layout_preferences()
            image_opts = get_image_preferences()
            config = {
                "days": days,
                "display_mode": display_mode,
                "rows": rows,
                "image_options": image_opts
            }
        else:
            config = edit_config(existing_config)
    else:
        print("Invalid choice. Creating a new configuration by default.")
        days, display_mode, rows = get_layout_preferences()
        image_opts = get_image_preferences()
        config = {
            "days": days,
            "display_mode": display_mode,
            "rows": rows,
            "image_options": image_opts
        }
    
    # Generate preview with the configuration
    preview_img = generate_layout_preview(config["days"], config["display_mode"], config["rows"], image_opts=config.get("image_options"))
    preview_img.show()  # Opens the preview image using the default viewer
    preview_img.save("layout_preview.png")
    print("Layout preview saved as layout_preview.png")
    
    # Ask the user if they want to save the configuration.
    save_ans = input("Would you like to save this display configuration? (y/n): ").strip().lower()
    if save_ans in ("y", "yes"):
        save_configuration(config)
    else:
        print("Configuration not saved.")

if __name__ == "__main__":
    main()