# layout_builder.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from display.display_panel_types.layout_panel import LayoutPanel
from display.display_panel_types.placeholder_panel import PlaceholderPanel

def main():
    print("Welcome to the E-Ink Calendar Layout Builder")
    
    # Instantiate a LayoutPanel, which will:
    #   - Ask the user whether to divide the screen horizontally or vertically.
    #   - Ask for the number of panels.
    #   - Dynamically load all available panel types from display_panel_types.
    #   - Display an initial layout with each panel labeled.
    #   - For each panel, prompt the user to select a panel type and configure it.
    layout = LayoutPanel(800,480)
    
    # Render the final layout image at a fixed resolution (e.g., 800 x 480)
    final_img = layout.render(800, 480)

    # Display the final image
    final_img.show()


    # Display the final image
    final_img.show()

    # Prompt the user to set a unique name for the final layout.
    user_filename = input("Enter a name to save the final layout (without extension): ").strip()
    if not user_filename:
        user_filename = "final_layout"

    # Construct the filename with a .png extension.
    file_to_save = f"{user_filename}.png"
    final_img.save(file_to_save)
    print(f"Final layout saved as {file_to_save}")

if __name__ == "__main__":
    main()