# simulation.py
"""
Core simulation engine for NeuroGlow.
Defines Neuron, Synapse, ActionPotential classes and the simulation loop.
"""
import math
import random
from enum import Enum, auto

class NeuronState(Enum):
    RESTING = auto()
    FIRING = auto()
    REFRACTORY = auto()

class ActionPotential:
    def __init__(self, synapse, progress=0.0, intensity=1.0):
        self.synapse = synapse  # Reference to Synapse
        self.progress = progress  # 0.0 (source) to 1.0 (target)
        self.intensity = intensity  # For glow/decay effects

class Synapse:
    def __init__(self, source, target):
        self.source = source  # Neuron object
        self.target = target  # Neuron object
        self.aps = []  # List of ActionPotentials currently propagating

class Neuron:
    def __init__(self, nid, position):
        self.id = nid
        self.position = position  # (x, y)
        self.state = NeuronState.RESTING
        self.activation = 0.0
        self.refractory_timer = 0.0
        self.out_synapses = []  # List of Synapse objects
        # Assign neuron type: excitatory (80%) or inhibitory (20%)
        self.neuron_type = "excitatory" if random.random() < 0.8 else "inhibitory"

class Simulation:
    def __init__(self, n_neurons=8, neurotransmitters=None):
        self.neurons = []
        self.synapses = []
        self.aps = []  # All APs in the network
        self.time = 0.0
        self.dt = 0.016  # ~60 FPS
        self.neuro_params = neurotransmitters or {
            'Serotonin': 0.5,
            'Dopamine': 0.5,
            'GABA': 0.5,
            'SSRI Mode': False,
            'Acetylcholine': 0.5,
            'Endorphins': 0.5,
        }
        self.synaptic_strength = {}  # (src_idx, tgt_idx) -> float
        self.prev_synaptic_strength = {}  # (src_idx, tgt_idx) -> float
        self._build_network(n_neurons)

    def _build_network(self, n):
        # Arrange neurons in a circle
        cx, cy = 400, 350
        radius = 250
        for i in range(n):
            angle = 2 * math.pi * i / n
            x = cx + int(radius * math.cos(angle))
            y = cy + int(radius * math.sin(angle))
            neuron = Neuron(i, (x, y))
            self.neurons.append(neuron)
        # Random synapses
        for i, neuron in enumerate(self.neurons):
            n_conn = random.randint(2, min(4, n-1))
            targets = random.sample([j for j in range(n) if j != i], n_conn)
            for j in targets:
                target = self.neurons[j]
                syn = Synapse(neuron, target)
                neuron.out_synapses.append(syn)
                self.synapses.append(syn)

    def reset(self, n_neurons=None):
        self.neurons.clear()
        self.synapses.clear()
        self.aps.clear()
        self.time = 0.0
        self.synaptic_strength.clear()
        self.prev_synaptic_strength.clear()
        self._build_network(n_neurons or len(self.neurons))

    def set_neuro_params(self, params):
        self.neuro_params.update(params)

    def _rewire_synapses(self):
        """Prune weak and grow new synapses periodically."""
        # initialize or increment step counter
        self._step_counter = getattr(self, '_step_counter', 0) + 1
        # perform rewiring every 90 steps (~1.5s)
        if self._step_counter % 90 != 0:
            return
        min_syn, max_syn = 2, 4
        for neuron in self.neurons:
            # prune weak synapses
            weak_syns = [syn for syn in neuron.out_synapses
                         if self.synaptic_strength.get((syn.source.id, syn.target.id), 0.0) < 0.03]
            if len(neuron.out_synapses) > min_syn and weak_syns:
                syn_to_remove = random.choice(weak_syns)
                neuron.out_synapses.remove(syn_to_remove)
                if syn_to_remove in self.synapses:
                    self.synapses.remove(syn_to_remove)
                key = (syn_to_remove.source.id, syn_to_remove.target.id)
                self.synaptic_strength.pop(key, None)
                self.prev_synaptic_strength.pop(key, None)
            # grow new synapses
            if len(neuron.out_synapses) < max_syn and random.random() < 0.25:
                targets = [n for n in self.neurons if n is not neuron
                           and all(s.target is not n for s in neuron.out_synapses)]
                if targets:
                    target = random.choice(targets)
                    new_syn = Synapse(neuron, target)
                    neuron.out_synapses.append(new_syn)
                    self.synapses.append(new_syn)
                    key = (neuron.id, target.id)
                    self.synaptic_strength[key] = 0.01
                    self.prev_synaptic_strength[key] = 0.01

    def step(self):
        # Parameters
        serotonin = float(self.neuro_params.get('Serotonin', 0.5))
        ssri = bool(self.neuro_params.get('SSRI Mode', False))
        dopamine = float(self.neuro_params.get('Dopamine', 0.5))
        gaba = float(self.neuro_params.get('GABA', 0.5))
        acetylcholine = float(self.neuro_params.get('Acetylcholine', 0.5))
        endorphins = float(self.neuro_params.get('Endorphins', 0.5))
        # Decay rate modulated by serotonin and endorphins
        base_decay = 0.03
        decay = base_decay * (1 - 0.8 * serotonin) * (1 - 0.5 * endorphins)
        if ssri:
            decay *= 0.3
        # dynamic rewiring logic
        self._rewire_synapses()
        # Update APs
        for ap in list(self.aps):
            # AP speed modulated by acetylcholine (higher -> faster)
            speed = 1.5 * (1 + 0.5 * acetylcholine)
            ap.progress += self.dt * speed
            ap.intensity -= decay
            if ap.progress >= 1.0 or ap.intensity <= 0.05:
                ap.synapse.aps.remove(ap)
                self.aps.remove(ap)

        # Update neurons
        for neuron in self.neurons:
            if neuron.state == NeuronState.FIRING:
                neuron.state = NeuronState.REFRACTORY
                neuron.refractory_timer = 0.3 + 2.0 * gaba    # Range: 0.3s (low GABA) to 2.3s (high)
                # Initiate APs on outgoing synapses
                for syn in neuron.out_synapses:
                    ap = ActionPotential(synapse=syn, progress=0.0, intensity=1.0)
                    syn.aps.append(ap)
                    self.aps.append(ap)
            elif neuron.state == NeuronState.REFRACTORY:
                neuron.refractory_timer -= self.dt
                if neuron.refractory_timer <= 0:
                    neuron.state = NeuronState.RESTING
            elif neuron.state == NeuronState.RESTING:
                # Passive decay
                neuron.activation *= 0.96
                # Random input for demo (replace with real input later)
                if random.random() < 0.01:
                    neuron.activation += 1.0
                if neuron.activation > 1.2 - 1.0 * dopamine:  # Range: 1.2 (low dopamine) to 0.2 (high)
                    neuron.state = NeuronState.FIRING
                    neuron.activation = 0.0

        # Hebbian plasticity: strengthen used synapses
        for ap in self.aps:
            src_idx = ap.synapse.source.id
            tgt_idx = ap.synapse.target.id
            key = (src_idx, tgt_idx)
            self.synaptic_strength[key] = min(1.0, self.synaptic_strength.get(key, 0.0) + 0.1)
        # Decay all strengths
        for key in self.synaptic_strength:
            self.synaptic_strength[key] *= 0.995
        # Track previous strengths for delta
        self.prev_synaptic_strength = self.prev_synaptic_strength if hasattr(self, 'prev_synaptic_strength') else {}
        for key in self.synaptic_strength:
            self.prev_synaptic_strength[key] = self.synaptic_strength[key]

    def get_visuals(self):
        """
        Returns:
            neurons: list of (x, y, state, neuron_type)
            aps: list of (source_pos, target_pos, progress, intensity)
        """
        neuron_visuals = [(n.position[0], n.position[1], n.state, n.neuron_type) for n in self.neurons]
        ap_visuals = []
        for ap in self.aps:
            src = ap.synapse.source.position
            tgt = ap.synapse.target.position
            ap_visuals.append((src, tgt, ap.progress, ap.intensity))
        return neuron_visuals, ap_visuals

    def get_synaptic_strength(self, src_idx, tgt_idx):
        return self.synaptic_strength.get((src_idx, tgt_idx), 0.0)

    def get_synaptic_strength_delta(self, src_idx, tgt_idx):
        prev = self.prev_synaptic_strength.get((src_idx, tgt_idx), 0.0)
        curr = self.synaptic_strength.get((src_idx, tgt_idx), 0.0)
        return curr - prev
