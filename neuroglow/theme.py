import os
import dearpygui.dearpygui as dpg

# Neon color palette (RGBA)
WINDOW_BG = (0, 0, 0, 255)  # Pure OLED black background
NEON_PURPLE = (162, 73, 157, 255)
NEON_BLUE = (62, 106, 187, 255)
NEON_CYAN = (99, 181, 192, 255)
NEON_ORANGE = (218, 153, 93, 255)

# Spacing grid (pixels)
SPACING_SMALL = 8
SPACING_MEDIUM = 12
SPACING_LARGE = 16

# Font paths (put font files in neuroglow/fonts/)
BASE_DIR = os.path.dirname(__file__)
FONTS_DIR = os.path.join(BASE_DIR, 'fonts')
FONT_FILES = {
    'JetBrainsMono': os.path.join(FONTS_DIR, 'JetBrainsMono-Regular.ttf'),
}


def load_fonts():
    """
    Load and bind custom fonts for the application.
    """
    # Attempt to load custom fonts
    try:
        # Create font registry and assign fonts to it
        with dpg.font_registry() as fr_id:
            for tag, path in FONT_FILES.items():
                if os.path.exists(path):
                    try:
                        # Parent each font item to the registry
                        font_item = dpg.add_font(path, 20, parent=fr_id)
                        if tag == 'Orbitron':
                            dpg.bind_font(font_item)
                    except Exception as fe:
                        print(f"Warning: Failed to load font '{tag}': {fe}")
                else:
                    print(f"Warning: Font file for '{tag}' not found at {path}")
    except Exception as re:
        print(f"Warning: Font registry error: {re}")


def create_theme():
    """
    Create and return a DearPyGui theme using the neon palette.
    """
    with dpg.theme() as custom_theme:
        with dpg.theme_component(dpg.mvAll):
            # OLED-inspired backgrounds & colors
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, WINDOW_BG, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, WINDOW_BG, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (20, 20, 20, 180), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, NEON_CYAN, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, WINDOW_BG, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, NEON_PURPLE, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (230, 230, 230, 255), category=dpg.mvThemeCat_Core)
            # Border rounding & padding for sleek look
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, SPACING_MEDIUM, SPACING_MEDIUM, category=dpg.mvThemeCat_Core)
            # Slider styles
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, NEON_CYAN, category=dpg.mvThemeCat_Core)
            try:
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, NEON_BLUE, category=dpg.mvThemeCat_Core)
            except AttributeError:
                pass
            try:
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrabHovered, NEON_PURPLE, category=dpg.mvThemeCat_Core)
            except AttributeError:
                pass
            # Button styles
            dpg.add_theme_color(dpg.mvThemeCol_Button, NEON_PURPLE, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, NEON_ORANGE, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, NEON_CYAN, category=dpg.mvThemeCat_Core)
            # Tooltip background
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (20, 20, 20, 230), category=dpg.mvThemeCat_Core)
    return custom_theme
