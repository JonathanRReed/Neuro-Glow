import dearpygui.dearpygui as dpg
import math
from neuroglow.simulation import Simulation, NeuronState

CANVAS_TAG = "neuro_canvas"

# Neon palette for neurons/synapses
NEON_COLORS = [
    (162, 73, 157, 255),   # Neon Purple/Magenta
    (62, 106, 187, 255),   # Neon Blue
    (99, 181, 192, 255),   # Neon Cyan/Teal
    (218, 153, 93, 255),   # Neon Orange/Gold
]

# Color mapping for neuron types
TYPE_COLORS = {
    "excitatory": NEON_COLORS[0],  # Purple
    "inhibitory": NEON_COLORS[2],  # Cyan
}

sim = None

# --- Enhanced Neon/Glow Visualization ---
def draw_network_sim():
    dpg.delete_item(CANVAS_TAG, children_only=True)
    neuron_visuals, ap_visuals = sim.get_visuals()

    # --- Fix: Get mouse position relative to canvas ---
    mouse_global = dpg.get_mouse_pos()
    canvas_origin = dpg.get_item_rect_min(CANVAS_TAG)
    mouse_pos = (mouse_global[0] - canvas_origin[0], mouse_global[1] - canvas_origin[1])
    hovered_node = None
    hover_radius = 26  # pixels

    # --- Get current canvas size for responsive layout ---
    canvas_size = dpg.get_item_rect_size(CANVAS_TAG)
    width, height = canvas_size

    # (Optional: Use width/height for dynamic layout)

    # --- Draw Synapses (Neon Glass, All Synapses, Plasticity) ---
    def clamp_point_to_arc(center, edge, ctrl, radius, margin=8):
        # Clamp the control point to a max distance from center
        dx, dy = ctrl[0]-center[0], ctrl[1]-center[1]
        dist = math.hypot(dx, dy)
        max_dist = radius + margin
        if dist > max_dist:
            scale = max_dist / dist
            return (center[0] + dx*scale, center[1] + dy*scale)
        return ctrl

    def curve_intersects_node(p1, p2, p3, p4, exclude_idxs):
        for t in [i/20.0 for i in range(21)]:
            x = (1-t)**3*p1[0] + 3*(1-t)**2*t*p2[0] + 3*(1-t)*t**2*p3[0] + t**3*p4[0]
            y = (1-t)**3*p1[1] + 3*(1-t)**2*t*p2[1] + 3*(1-t)*t**2*p3[1] + t**3*p4[1]
            for idx, (nx, ny, _, _) in enumerate(neuron_visuals):
                if idx in exclude_idxs:
                    continue
                base_radius = 18
                pulse = 8 * abs(math.sin(sim.time*5 + idx)) if neuron_visuals[idx][2] == NeuronState.FIRING else 0
                r = base_radius + pulse + 6
                if math.hypot(x-nx, y-ny) < r:
                    return True
        return False

    for syn in sim.synapses:
        src_idx = syn.source.id
        tgt_idx = syn.target.id
        x0, y0, state0, _ = neuron_visuals[src_idx]
        x1, y1, state1, _ = neuron_visuals[tgt_idx]
        base_radius = 18
        pulse0 = 8 * abs(math.sin(sim.time*5 + src_idx)) if state0 == NeuronState.FIRING else 0
        pulse1 = 8 * abs(math.sin(sim.time*5 + tgt_idx)) if state1 == NeuronState.FIRING else 0
        r0 = base_radius + pulse0
        r1 = base_radius + pulse1
        dx, dy = x1-x0, y1-y0
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        ux, uy = dx/dist, dy/dist
        src_edge = (x0 + ux*r0, y0 + uy*r0)
        tgt_edge = (x1 - ux*r1, y1 - uy*r1)
        # Adaptive curve: bow out if curve intersects another node
        bow = 30
        max_bow = 120
        for bow_try in range(5):
            mx = (src_edge[0] + tgt_edge[0]) / 2 + bow * ((src_edge[1]-tgt_edge[1])/200)
            my = (src_edge[1] + tgt_edge[1]) / 2 + bow * ((tgt_edge[0]-src_edge[0])/200)
            ctrl1 = clamp_point_to_arc((x0, y0), src_edge, (mx, my), r0)
            ctrl2 = clamp_point_to_arc((x1, y1), tgt_edge, (mx, my), r1)
            if not curve_intersects_node(src_edge, ctrl1, ctrl2, tgt_edge, [src_idx, tgt_idx]):
                break
            bow += (max_bow - bow) // 2
        # --- Neon glass synapse effect with plasticity cues ---
        strength = 0.0
        delta = 0.0
        if hasattr(sim, 'get_synaptic_strength'):
            strength = sim.get_synaptic_strength(src_idx, tgt_idx)
        if hasattr(sim, 'get_synaptic_strength_delta'):
            delta = sim.get_synaptic_strength_delta(src_idx, tgt_idx)
        neon_blue = (80, 200, 255)
        neon_purple = (180, 80, 255)
        interp = lambda a, b: int(a + (b-a)*strength)
        color_main = (
            interp(neon_blue[0], neon_purple[0]),
            interp(neon_blue[1], neon_purple[1]),
            interp(neon_blue[2], neon_purple[2])
        )
        glow_thick = 8 + 4 * strength
        neon_thick = 3 + 2 * strength
        core_thick = 1.5
        glow_alpha = int(40 + 70 * strength + 40 * abs(math.sin(sim.time*2 + src_idx + tgt_idx)))
        neon_alpha = int(60 + 160 * strength)
        core_color = (210, 240, 255, int(120 + 80 * strength))
        if delta > 0.01:
            pulse_alpha = int(120 * min(1, delta*10))
            pulse_color = (255, 60, 255, pulse_alpha)
        elif delta < -0.01:
            pulse_alpha = int(120 * min(1, -delta*10))
            pulse_color = (60, 255, 255, pulse_alpha)
        else:
            pulse_color = None
        dpg.draw_bezier_cubic(p1=src_edge, p2=ctrl1, p3=ctrl2, p4=tgt_edge, color=(color_main[0], color_main[1], color_main[2], glow_alpha), thickness=glow_thick, parent=CANVAS_TAG)
        dpg.draw_bezier_cubic(p1=src_edge, p2=ctrl1, p3=ctrl2, p4=tgt_edge, color=(color_main[0], color_main[1], color_main[2], neon_alpha), thickness=neon_thick, parent=CANVAS_TAG)
        dpg.draw_bezier_cubic(p1=src_edge, p2=ctrl1, p3=ctrl2, p4=tgt_edge, color=core_color, thickness=core_thick, parent=CANVAS_TAG)
        highlight_offset = 0.18
        hx0 = src_edge[0] + highlight_offset*(ctrl1[0]-src_edge[0])
        hy0 = src_edge[1] + highlight_offset*(ctrl1[1]-src_edge[1]) - 2
        hx1 = tgt_edge[0] + highlight_offset*(ctrl2[0]-tgt_edge[0])
        hy1 = tgt_edge[1] + highlight_offset*(ctrl2[1]-tgt_edge[1]) - 2
        dpg.draw_line((hx0, hy0), (hx1, hy1), color=(255,255,255,60), thickness=1, parent=CANVAS_TAG)
        if pulse_color:
            dpg.draw_bezier_cubic(p1=src_edge, p2=ctrl1, p3=ctrl2, p4=tgt_edge, color=pulse_color, thickness=neon_thick+2, parent=CANVAS_TAG)
        # AP pulse (if any)
        # Find if there is a current AP on this synapse
        ap_found = None
        for ap in getattr(sim, 'aps', []):
            if ap.synapse.source.id == src_idx and ap.synapse.target.id == tgt_idx:
                ap_found = ap
                break
        if ap_found:
            progress = ap_found.progress
            intensity = ap_found.intensity
            def bezier_interp(t, p1, p2, p3, p4):
                return (
                    (1-t)**3*p1[0] + 3*(1-t)**2*t*p2[0] + 3*(1-t)*t**2*p3[0] + t**3*p4[0],
                    (1-t)**3*p1[1] + 3*(1-t)**2*t*p2[1] + 3*(1-t)*t**2*p3[1] + t**3*p4[1],
                )
            px, py = bezier_interp(progress, src_edge, ctrl1, ctrl2, tgt_edge)
            dpg.draw_circle(center=(px, py), radius=7+3*intensity, color=color_main, fill=(color_main[0], color_main[1], color_main[2], int(100*intensity)), thickness=2, parent=CANVAS_TAG)

    # --- Draw Neurons (Nodes) with Neon Glow, Gradient, Pulse, and Hover ---
    for idx, (x, y, state, ntype) in enumerate(neuron_visuals):
        # Node size: pulse for firing, base for resting/refractory
        base_radius = 18
        pulse = 0
        if state == NeuronState.FIRING:
            pulse = 8 * abs(math.sin(sim.time*5 + idx))  # Animate pulse
        elif state == NeuronState.REFRACTORY:
            pulse = 0
        radius = base_radius + pulse
        # Hover detection (now using canvas-local coordinates)
        dist = math.hypot(mouse_pos[0] - x, mouse_pos[1] - y)
        is_hovered = dist < hover_radius + pulse
        if is_hovered:
            hovered_node = (idx, x, y, state, ntype)
        # Glow color by state
        if state == NeuronState.FIRING:
            glow_color = (255, 40, 200, 160 if is_hovered else 140)  # Magenta glow
            outline = (255, 255, 255, 255 if is_hovered else 220)
        elif state == NeuronState.REFRACTORY:
            glow_color = (120, 120, 120, 90 if is_hovered else 60)  # Dim gray
            outline = (180, 180, 180, 180 if is_hovered else 120)
        else:
            glow_color = (40, 255, 255, 140 if is_hovered else 100)  # Cyan glow
            # Outline color by neuron type
            outline = TYPE_COLORS.get(ntype, NEON_COLORS[idx % len(NEON_COLORS)])
        # Outer glow
        dpg.draw_circle(center=(x, y), radius=int(radius)+14, color=glow_color, fill=(glow_color[0], glow_color[1], glow_color[2], 28), thickness=8, parent=CANVAS_TAG)
        # Main node with gradient (simulate by layered circles)
        for r in range(int(radius), int(radius)-6, -2):
            alpha = int(110 if is_hovered else 80 + 40*(r-radius+6)/6)
            dpg.draw_circle(center=(x, y), radius=r, color=outline, fill=(outline[0], outline[1], outline[2], alpha), thickness=3, parent=CANVAS_TAG)
        # Inner core (brighter if firing)
        fill = (255, 255, 255, 220 if is_hovered else 180) if state == NeuronState.FIRING else (outline[0], outline[1], outline[2], 140 if is_hovered else 120)
        dpg.draw_circle(center=(x, y), radius=int(radius)-7, color=outline, fill=fill, thickness=2, parent=CANVAS_TAG)
        # If hovered, draw a slightly larger outline
        if is_hovered:
            dpg.draw_circle(center=(x, y), radius=int(radius)+18, color=(255,255,255,90), thickness=4, parent=CANVAS_TAG)

    # --- Legend (OLED neon, anchored bottom-right, no overlap) ---
    legend_pad_x, legend_pad_y = 32, 32
    legend_width, legend_height = 220, 240
    legend_x, legend_y = width - legend_width - legend_pad_x, height - legend_height - legend_pad_y
    # Background rectangle for readability
    dpg.draw_rectangle((legend_x, legend_y), (legend_x+legend_width, legend_y+legend_height), color=(40,40,80,80), fill=(20,20,40,180), rounding=15, parent=CANVAS_TAG)
    dpg.draw_text((legend_x+18, legend_y+18), "Legend:", color=(220,220,255,220), size=18, parent=CANVAS_TAG)
    # Increased vertical spacing for each item
    dpg.draw_circle(center=(legend_x+56, legend_y+48), radius=11, color=(255,40,200,200), fill=(255,40,200,110), thickness=3, parent=CANVAS_TAG)
    dpg.draw_text((legend_x+78, legend_y+40), "Firing", color=(255,40,200,220), size=15, parent=CANVAS_TAG)
    dpg.draw_circle(center=(legend_x+56, legend_y+78), radius=11, color=(40,255,255,180), fill=(40,255,255,90), thickness=3, parent=CANVAS_TAG)
    dpg.draw_text((legend_x+78, legend_y+70), "Resting", color=(40,255,255,180), size=15, parent=CANVAS_TAG)
    dpg.draw_circle(center=(legend_x+56, legend_y+108), radius=11, color=(180,180,180,140), fill=(180,180,180,70), thickness=3, parent=CANVAS_TAG)
    dpg.draw_text((legend_x+78, legend_y+100), "Refractory", color=(180,180,180,170), size=15, parent=CANVAS_TAG)
    # Active AP line and label (well below last item)
    dpg.draw_line((legend_x+36, legend_y+138), (legend_x+106, legend_y+138), color=(255,40,200,170), thickness=5, parent=CANVAS_TAG)
    dpg.draw_text((legend_x+116, legend_y+130), "Active AP", color=(255,40,200,170), size=15, parent=CANVAS_TAG)
    # Neuron types legend
    dpg.draw_circle(center=(legend_x+56, legend_y+168), radius=11, color=TYPE_COLORS["excitatory"], fill=(TYPE_COLORS["excitatory"][0], TYPE_COLORS["excitatory"][1], TYPE_COLORS["excitatory"][2], 110), thickness=3, parent=CANVAS_TAG)
    dpg.draw_text((legend_x+78, legend_y+160), "Excitatory", color=TYPE_COLORS["excitatory"], size=15, parent=CANVAS_TAG)
    dpg.draw_circle(center=(legend_x+56, legend_y+198), radius=11, color=TYPE_COLORS["inhibitory"], fill=(TYPE_COLORS["inhibitory"][0], TYPE_COLORS["inhibitory"][1], TYPE_COLORS["inhibitory"][2], 110), thickness=3, parent=CANVAS_TAG)
    dpg.draw_text((legend_x+78, legend_y+190), "Inhibitory", color=TYPE_COLORS["inhibitory"], size=15, parent=CANVAS_TAG)

    # --- Overlay: FPS and neuron count ---
    fps_text = f"FPS: {dpg.get_frame_rate():.1f} | Neurons: {len(sim.neurons)}"
    dpg.draw_text((10, 10), fps_text, color=(200,200,255,200), size=14, parent=CANVAS_TAG)

    # --- Tooltip on hover with stats ---
    if hovered_node:
        idx, x, y, state, ntype = hovered_node
        # gather neuron stats
        neuron = sim.neurons[idx]
        out_count = len(neuron.out_synapses)
        strengths = []
        for syn in neuron.out_synapses:
            strengths.append(sim.get_synaptic_strength(idx, syn.target.id))
        avg_strength = sum(strengths)/len(strengths) if strengths else 0.0
        label = (
            f"Neuron {idx}\n"
            f"Type: {ntype}\n"
            f"State: {state.name}\n"
            f"Out Synapses: {out_count}\n"
            f"Avg Strength: {avg_strength:.2f}"
        )
        dpg.draw_text((x+28, y-12), label, color=(255,255,180,220), size=15, parent=CANVAS_TAG)


def setup_canvas(canvas_width=800, canvas_height=700, as_child=False):
    parent_args = {'parent': dpg.last_item()} if as_child else {}
    if not dpg.does_item_exist(CANVAS_TAG):
        dpg.add_drawlist(width=canvas_width, height=canvas_height, tag=CANVAS_TAG, **parent_args)
    else:
        dpg.configure_item(CANVAS_TAG, width=canvas_width, height=canvas_height)


def update_network(network_size, neuro_params):
    global sim
    sim = Simulation(n_neurons=network_size, neurotransmitters=neuro_params)
    draw_network_sim()


def tick_and_draw(neuro_params):
    if sim:
        sim.set_neuro_params(neuro_params)
        sim.step()
        draw_network_sim()


def main(canvas_width=800, canvas_height=700):
    dpg.create_context()
    dpg.create_viewport(title="NeuroGlow", width=1024, height=768)
    setup_canvas(canvas_width, canvas_height)
    update_network(10, {"neuro_param1": 1.0, "neuro_param2": 2.0})  # Initial network size and neuro params
    dpg.setup_dearpygui()
    dpg.show_viewport()
    while dpg.is_dearpygui_running():
        tick_and_draw({"neuro_param1": 1.0, "neuro_param2": 2.0})  # Neuro params for each frame
        dpg.render_dearpygui_frame()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
