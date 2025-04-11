# layout_panel.py

import os
import sys
import importlib.util
import inspect
from PIL import Image, ImageDraw, ImageFont

##############################################################################
# NUCLEAR APPROACH TO IMPORTS:
# Force-add the project root (or whichever directory you want) to sys.path
# so that absolute imports “just work” no matter how we run this file.
##############################################################################
CURRENT_FILE = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
# Adjust the number of levels up if needed:
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now we do absolute imports:
from display.display_panel_types.panel import Panel
from display.display_panel_types.placeholder_panel import PlaceholderPanel

##############################################################################
# LAYOUTPANEL CLASS
##############################################################################

class LayoutPanel(Panel):
    def __init__(self, width: int, height: int, weight: int = 1):
        """
        Initialize a LayoutPanel with explicit dimensions.
        
        :param width: Overall allocated width for this LayoutPanel.
        :param height: Overall allocated height for this LayoutPanel.
        :param weight: Relative weight.
        """
        super().__init__(weight)
        self.width = width
        self.height = height
        self.orientation = None
        self.num_panels = None
        self.panels = []

        # Preliminary configuration loop
        layout_confirmed = False
        while not layout_confirmed:
            orient = input("Divide screen horizontally (H) or vertically (V)? ").strip().lower()
            # "Horizontal" means slicing the height (stacked top to bottom).
            # "Vertical" means slicing the width (side by side).
            self.orientation = "horizontal" if orient in ("h", "horizontal") else "vertical"

            try:
                self.num_panels = int(input("Enter number of panels: "))
            except ValueError:
                print("Invalid number, redoing config.")
                continue

            # Populate with placeholders using the separate PlaceholderPanel.
            self.panels = [PlaceholderPanel(i+1) for i in range(self.num_panels)]
            
            # Calculate allocated dimensions based on chosen orientation.
            if self.orientation == "horizontal":
                # In a horizontal division, each panel gets the full width and a share of the height.
                allocated_w = self.width
                allocated_h = self.height // self.num_panels
            else:
                # In a vertical division, each panel gets the full height and a share of the width.
                allocated_w = self.width // self.num_panels
                allocated_h = self.height

            print(f"Preliminary: Each sub-panel will be rendered at {allocated_w}x{allocated_h}.")
            prelim_img = self._render_preliminary(allocated_w, allocated_h)
            prelim_img.show()

            confirm = input("Are you happy with this layout? (y/n): ").strip().lower()
            if confirm in ("y", "yes"):
                layout_confirmed = True
            else:
                option = input("Enter 'redo' to reconfigure layout, or 'change' to abort LayoutPanel configuration: ").strip().lower()
                if option == "redo":
                    continue
                elif option == "change":
                    print("Aborting LayoutPanel config. Please choose another panel type.")
                    self.panels = []
                    return

        # Load available sub-panel types.
        self.available_panel_types = self._load_panel_types()

        print("\nNow let's configure each sub-panel:")
        for i in range(self.num_panels):
            print(f"  Panel {i+1}: (unconfigured)")

        final_panels = [None] * self.num_panels
        # Re-calculate allocated dims for sub-panels.
        if self.orientation == "horizontal":
            allocated_w = self.width
            allocated_h = self.height // self.num_panels
        else:
            allocated_w = self.width // self.num_panels
            allocated_h = self.height

        for i in range(self.num_panels):
            print(f"\nConfiguring sub-panel {i+1}:")
            keys = list(self.available_panel_types.keys())
            for idx, type_name in enumerate(keys, 1):
                print(f"  {idx}: {type_name}")
            while True:
                try:
                    choice = int(input("Choose a panel type by number: "))
                    if 1 <= choice <= len(keys):
                        break
                    else:
                        print("Invalid selection, try again.")
                except ValueError:
                    print("Invalid input. Try again.")
            chosen_key = keys[choice - 1]
            panel_cls = self.available_panel_types[chosen_key]
            # Use inspect to check __init__ signature. If the constructor requires width and height (after 'self'),
            # we pass the allocated dimensions.
            sig = inspect.signature(panel_cls.__init__)
            # Count parameters excluding 'self'
            param_count = len(sig.parameters) - 1
            if param_count >= 2:
                sub_panel = panel_cls(allocated_w, allocated_h)
            else:
                sub_panel = panel_cls()
            if hasattr(sub_panel, "configure"):
                sub_panel.configure()
            final_panels[i] = sub_panel
        self.panels = final_panels

    def _render_preliminary(self, sub_w: int, sub_h: int) -> Image.Image:
        """
        Renders a preliminary composite image using the placeholder panels.
        The overall final image is at (self.width x self.height).
        Each sub-panel is rendered at (sub_w x sub_h) and placed according to orientation.
        """
        final_img = Image.new("RGB", (self.width, self.height), "white")
        if self.orientation == "horizontal":
            for i, panel in enumerate(self.panels):
                y_offset = i * sub_h
                sub_img = panel.render(sub_w, sub_h)
                final_img.paste(sub_img, (0, y_offset))
        else:
            for i, panel in enumerate(self.panels):
                x_offset = i * sub_w
                sub_img = panel.render(sub_w, sub_h)
                final_img.paste(sub_img, (x_offset, 0))
        return final_img

    def _load_panel_types(self):
        """
        Scans the current directory for Python modules that define a subclass of Panel.
        Each module must define:
          - PANEL_NAME: a string name for the panel type.
          - PANEL_CLASS: the class (subclass of Panel).
        Returns a dictionary mapping PANEL_NAME to PANEL_CLASS.
        """
        panel_types = {}
        folder = os.path.dirname(os.path.abspath(__file__))
        for filename in os.listdir(folder):
            if filename.endswith(".py") and not filename.startswith("__") and filename != "panel.py":
                module_path = os.path.join(folder, filename)
                module_name = filename[:-3]
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "PANEL_NAME") and hasattr(mod, "PANEL_CLASS"):
                    panel_types[mod.PANEL_NAME] = mod.PANEL_CLASS
        return panel_types

    def render(self, width: int, height: int) -> Image.Image:
        """
        Composites the configured sub-panels into a final image.
        If orientation is horizontal, sub-panels are stacked top-to-bottom.
        If vertical, they are arranged side-by-side.
        """
        final_img = Image.new("RGB", (width, height), "white")
        if self.orientation == "horizontal":
            sub_h = height // self.num_panels
            for i, panel in enumerate(self.panels):
                y_offset = i * sub_h
                sub_img = panel.render(width, sub_h)
                final_img.paste(sub_img, (0, y_offset))
        else:
            sub_w = width // self.num_panels
            for i, panel in enumerate(self.panels):
                x_offset = i * sub_w
                sub_img = panel.render(sub_w, height)
                final_img.paste(sub_img, (x_offset, 0))
        return final_img

    def configure(self) -> None:
        """
        LayoutPanel's own configuration method.
        """
        print("No additional configuration required for Layout Panel.")

    def display(self):
        final_img = self.render(self.width, self.height)
        final_img.show()
        final_img.save("layout_panel_final.png")
        print("Saved layout_panel_final.png")

# Export module-level attributes for dynamic discovery.
PANEL_NAME = "Layout Panel"
PANEL_CLASS = LayoutPanel

if __name__ == "__main__":
    try:
        w = int(input("Overall width? "))
        h = int(input("Overall height? "))
    except ValueError:
        print("Invalid input. Exiting.")
        sys.exit(1)
    lp = LayoutPanel(w, h)
    lp.display()