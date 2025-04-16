import dearpygui.dearpygui as dpg
from neuroglow.ui import add_neuroglow_controls, get_neurotransmitter_values
from neuroglow.theme import load_fonts, create_theme
from neuroglow.visualization import setup_canvas, update_network, tick_and_draw

# Layout constants
SIDEBAR_WIDTH = 320
START_HEIGHT = 800
START_WIDTH = 1200

# --- Callbacks ---
def on_ui_scale_change(sender, app_data, user_data):
    dpg.set_global_font_scale(app_data)

def on_network_size_change(sender, app_data, user_data):
    # Update network with new size and current neuro params
    update_network(app_data, get_neurotransmitter_values())

def on_viewport_resize(sender, app_data):
    width, height = dpg.get_viewport_width(), dpg.get_viewport_height()
    dpg.configure_item("sidebar", width=SIDEBAR_WIDTH, height=height)
    dpg.configure_item("canvas_child", width=width-SIDEBAR_WIDTH, height=height)
    dpg.configure_item("neuro_canvas", width=width-SIDEBAR_WIDTH-40, height=height-40)
    # Redraw network to fit new canvas size
    update_network(dpg.get_value("Network Size"), get_neurotransmitter_values())

# --- Animation Callback ---
def simulation_timer_callback():
    # Defensive: Only schedule next frame if viewport is running
    if dpg.is_dearpygui_running():
        tick_and_draw(get_neurotransmitter_values())
        # Schedule next frame (~60 FPS)
        dpg.set_frame_callback(dpg.get_frame_count()+1, simulation_timer_callback)

# --- Main Entry ---
def main():
    dpg.create_context()
    # Load custom fonts and apply neon theme
    load_fonts()
    custom_theme = create_theme()
    with dpg.window(label="NeuroGlow", tag="main_window", width=START_WIDTH, height=START_HEIGHT, pos=(0,0), no_move=True, no_resize=True, no_title_bar=True):
        dpg.bind_theme(custom_theme)
        with dpg.group(horizontal=True):
            with dpg.child_window(tag="sidebar", width=SIDEBAR_WIDTH, height=START_HEIGHT, border=False):
                dpg.add_text("Settings Sidebar", color=(255,255,0,255))  # Debug: Should always show
                add_neuroglow_controls(network_size_callback=on_network_size_change, ui_scale_callback=on_ui_scale_change)
            dpg.add_separator()
            with dpg.child_window(tag="canvas_child", width=START_WIDTH-SIDEBAR_WIDTH, height=START_HEIGHT, border=False):
                setup_canvas(canvas_width=START_WIDTH-SIDEBAR_WIDTH-40, canvas_height=START_HEIGHT-40, as_child=True)
    # Initialize simulation and network
    update_network(dpg.get_value("Network Size"), get_neurotransmitter_values())
    dpg.create_viewport(title="NeuroGlow", width=START_WIDTH, height=START_HEIGHT)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    dpg.set_viewport_resize_callback(on_viewport_resize)
    # Start simulation animation loop
    dpg.set_frame_callback(dpg.get_frame_count()+1, simulation_timer_callback)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
