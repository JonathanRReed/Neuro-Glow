# Placeholder for imgui-based UI controls (to be implemented)
# This file will contain logic for neurotransmitter sliders and SSRI mode toggle.

import dearpygui.dearpygui as dpg
from neuroglow import config

# Default neurotransmitter values
defaults = {
    "Serotonin": 0.5,
    "Dopamine": 0.5,
    "GABA": 0.5,
    "Acetylcholine": 0.5,
    "Endorphins": 0.5,
    "SSRI Mode": False,
    "Network Size": 8,
    "UI Scale": 1.0,
}

# Neon color palette
neon_colors = {
    "purple": (162, 73, 157, 255),   # #A2499D
    "blue": (62, 106, 187, 255),     # #3E6ABB
    "cyan": (99, 181, 192, 255),     # #63B5C0
    "orange": (218, 153, 93, 255),   # #DA995D
}


def add_neuroglow_controls(network_size_callback=None, ui_scale_callback=None, as_child=False):
    # Neon/frosted glass sidebar theme
    with dpg.theme() as frosted_theme:
        with dpg.theme_component(dpg.mvAll):
            # Simulate frosted glass: semi-transparent, dark, neon border
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 20, 30, 180), category=dpg.mvThemeCat_Core)  # Frosted glass bg
            dpg.add_theme_color(dpg.mvThemeCol_Border, neon_colors["cyan"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 18, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 12, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, neon_colors["cyan"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 40, 180), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, neon_colors["purple"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, neon_colors["blue"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, neon_colors["orange"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, neon_colors["cyan"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, neon_colors["purple"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (30, 30, 40, 200), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, neon_colors["blue"], category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, neon_colors["orange"], category=dpg.mvThemeCat_Core)
    # Controls sidebar, fixed width, no move/resize/titlebar
    parent_args = {'parent': dpg.last_item()} if as_child else {}
    with dpg.group(**parent_args):
        with dpg.collapsing_header(label="Presets & Neurotransmitters", default_open=True):
            dpg.add_text("Presets", color=neon_colors["orange"])
            dpg.add_combo(items=list(config.PRESETS.keys()), label="Preset", tag="PresetCombo", default_value=list(config.PRESETS.keys())[0], callback=lambda s,a,u: apply_preset(a))
            def apply_preset(preset_name):
                vals = config.PRESETS.get(preset_name, {})
                for tag, value in vals.items():
                    if dpg.does_item_exist(tag):
                        dpg.set_value(tag, value)
                if network_size_callback:
                    # Trigger network update with current size
                    current_size = dpg.get_value("Network Size")
                    network_size_callback("Network Size", current_size, None)
            dpg.add_spacer(height=12)
            dpg.add_text("Neurotransmitter Levels", color=neon_colors["purple"])
            dpg.add_slider_float(label="Serotonin", tag="Serotonin", default_value=defaults["Serotonin"], min_value=0.0, max_value=1.0, format="%.2f")
            with dpg.tooltip(parent="Serotonin"):
                dpg.add_text("Glow decay duration (↑ serotonin → longer glow)")
            dpg.add_slider_float(label="Dopamine", tag="Dopamine", default_value=defaults["Dopamine"], min_value=0.0, max_value=1.0, format="%.2f")
            with dpg.tooltip(parent="Dopamine"):
                dpg.add_text("Firing threshold (↑ dopamine → lower threshold → more firing)")
            dpg.add_slider_float(label="GABA", tag="GABA", default_value=defaults["GABA"], min_value=0.0, max_value=1.0, format="%.2f")
            with dpg.tooltip(parent="GABA"):
                dpg.add_text("Refractory period duration (↑ GABA → longer refractory)")
            dpg.add_slider_float(label="Acetylcholine", tag="Acetylcholine", default_value=defaults["Acetylcholine"], min_value=0.0, max_value=1.0, format="%.2f")
            with dpg.tooltip(parent="Acetylcholine"):
                dpg.add_text("AP speed (↑ acetylcholine → faster propagation)")
            dpg.add_slider_float(label="Endorphins", tag="Endorphins", default_value=defaults["Endorphins"], min_value=0.0, max_value=1.0, format="%.2f")
            with dpg.tooltip(parent="Endorphins"):
                dpg.add_text("Glow decay damping (↑ endorphins → slower decay)")
            dpg.add_checkbox(label="SSRI Mode", tag="SSRI Mode", default_value=defaults["SSRI Mode"])
            with dpg.tooltip(parent="SSRI Mode"):
                dpg.add_text("Toggle SSRI effect on serotonin decay")
            dpg.add_spacer(height=8)
            dpg.add_text("SSRI Mode increases serotonin effect.", wrap=250, color=neon_colors["cyan"])
        with dpg.collapsing_header(label="Network & Display", default_open=False):
            dpg.add_text("Network Size", color=neon_colors["blue"])
            dpg.add_slider_int(label="# Neurons", tag="Network Size", default_value=defaults["Network Size"], min_value=3, max_value=20, callback=network_size_callback)
            dpg.add_spacer(height=8)
            dpg.add_text("UI Scale", color=neon_colors["orange"])
            dpg.add_slider_float(label="Scale", tag="UI Scale", default_value=defaults["UI Scale"], min_value=0.6, max_value=2.0, format="%.2fx", callback=ui_scale_callback)
    dpg.bind_theme(frosted_theme)


def get_neurotransmitter_values():
    """Return the current neurotransmitter slider values and SSRI mode, with safe defaults and types."""
    try:
        ssri_raw = dpg.get_value("SSRI Mode")
        # Accept bool, int, or None
        ssri = bool(ssri_raw) if ssri_raw is not None else False
        return {
            "Serotonin": float(dpg.get_value("Serotonin") or 0.5),
            "Dopamine": float(dpg.get_value("Dopamine") or 0.5),
            "GABA": float(dpg.get_value("GABA") or 0.5),
            "Acetylcholine": float(dpg.get_value("Acetylcholine") or 0.5),
            "Endorphins": float(dpg.get_value("Endorphins") or 0.5),
            "SSRI Mode": ssri,
            "Network Size": int(dpg.get_value("Network Size") or 8),
            "UI Scale": float(dpg.get_value("UI Scale") or 1.0),
        }
    except Exception as e:
        return {
            "Serotonin": 0.5,
            "Dopamine": 0.5,
            "GABA": 0.5,
            "Acetylcholine": 0.5,
            "Endorphins": 0.5,
            "SSRI Mode": False,
            "Network Size": 8,
            "UI Scale": 1.0,
        }
