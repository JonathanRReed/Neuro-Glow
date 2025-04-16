# Configuration constants for NeuroGlow

# Probability that a newly created neuron is excitatory
NEURON_EXCITATORY_PROB = 0.8

# Preset slider configurations (neurotransmitter levels)
PRESETS = {
    "Default": {"Serotonin": 0.5, "Dopamine": 0.5, "GABA": 0.5, "Acetylcholine": 0.5, "Endorphins": 0.5},
    "High Serotonin": {"Serotonin": 1.0, "Dopamine": 0.5, "GABA": 0.5, "Acetylcholine": 0.5, "Endorphins": 0.5},
    "Fast ACh": {"Serotonin": 0.5, "Dopamine": 0.5, "GABA": 0.5, "Acetylcholine": 1.0, "Endorphins": 0.5},
    "Slow Decay": {"Serotonin": 0.5, "Dopamine": 0.5, "GABA": 0.5, "Acetylcholine": 0.5, "Endorphins": 1.0},
    "Inhibitory Bias": {"Serotonin": 0.5, "Dopamine": 0.5, "GABA": 1.0, "Acetylcholine": 0.5, "Endorphins": 0.5},
    # New dynamic presets
    "Excitatory Surge":   {"Serotonin": 0.3, "Dopamine": 0.9, "GABA": 0.2, "Acetylcholine": 0.7, "Endorphins": 0.4},
    "Burst Mode":         {"Serotonin": 0.6, "Dopamine": 0.8, "GABA": 0.3, "Acetylcholine": 0.9, "Endorphins": 0.5},
    "Calm Inhibition":    {"Serotonin": 0.7, "Dopamine": 0.3, "GABA": 0.9, "Acetylcholine": 0.4, "Endorphins": 0.6},
    "Balanced Excitation":{"Serotonin": 0.5, "Dopamine": 0.7, "GABA": 0.7, "Acetylcholine": 0.6, "Endorphins": 0.5},
}
