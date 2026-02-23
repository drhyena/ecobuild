# -----------------------------
# Screen
# -----------------------------
WIDTH, HEIGHT = 600, 600
TILE_SIZE = 10
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE

# -----------------------------
# Vegetation
# -----------------------------
MAX_VEG_COUNT = 1

# -----------------------------
# Noise parameters for world generation
# -----------------------------
NOISE_SCALE = 190
NOISE_OCTAVES = 4      # Not used now (OpenSimplex basic)
NOISE_PERSISTENCE = 0.45
NOISE_LACUNARITY = 2.0

WORLD_SEED = None        # None for random