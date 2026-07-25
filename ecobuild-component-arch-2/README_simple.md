ā# EcoBuild

EcoBuild is a simple 2D predator--prey simulation built using Python and
Pygame.

The program creates a grid-based world where predators, prey, and
vegetation exist together. Each creature moves around the map, looks for
food or water, and reacts to other creatures.

------------------------------------------------------------------------

## What the Project Does

-   Generates a random terrain map
-   Spawns predators and prey on land tiles
-   Spawns vegetation as a food source
-   Runs a continuous simulation loop where all creatures act every
    frame

The simulation continues until all creatures die or the window is
closed.

------------------------------------------------------------------------

## How It Works

Each creature has:

-   A position on the grid
-   Hunger and thirst values
-   An "alive" status
-   A current state (like wandering, hungry, hunting, fleeing, or
    thirsty)

Every frame:

1.  Hunger and thirst decrease.
2.  The creature decides what state it should be in.
3.  Based on its state, it chooses a target tile.
4.  It moves toward that tile using pathfinding.

------------------------------------------------------------------------

## Predator Behavior

-   Becomes hungry when hunger drops below a certain level.
-   Looks for the closest prey within its visible area.
-   Chases the prey.
-   If it reaches the prey, it kills it and restores hunger.
-   If it fails to catch prey in time, it may starve.

------------------------------------------------------------------------

## Prey Behavior

-   Wanders randomly when safe.
-   If targeted by a predator, it switches to fleeing.
-   Chooses a tile that moves it away from the predator.
-   Can eat vegetation when hungry.
-   Can still starve if it does not reach food in time.

------------------------------------------------------------------------

## Vegetation

-   Spawns randomly on land tiles.
-   Can be eaten by prey.
-   Once eaten, it is removed from the map.

------------------------------------------------------------------------

## Known Limitations

-   Predators may struggle to successfully catch moving prey.
-   Creatures can starve while hunting or fleeing.
-   There is no reproduction.
-   There is no long-term population balancing.
-   The ecosystem can collapse depending on parameter settings.

------------------------------------------------------------------------

## Dependencies

-   Python 3.x
-   pygame

Install pygame with:

pip install pygame

------------------------------------------------------------------------

## Running the Project

Run:

python ecobuild.py

A window will open showing the simulation.
