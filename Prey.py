
# -------------------------------------------------
# PREY
# -------------------------------------------------

class Prey(Creature):
    def __init__(self, x, y, interaction_manager):
        super().__init__(x, y, interaction_manager)
        self.active_predator = None
        self.iq = 0.4