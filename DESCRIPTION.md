# Angry Tao Project Description

## Overview

Angry Tao is a 2D shooting game developed in Python using Pygame. The player controls a character that shoots enemies while avoiding civilians. The game includes various weapons, obstacles, and increasing difficulty stages.

## Features

- Multiple weapon types with unique shooting mechanics
- Explosive bullets create temporary damaging zones
- Civilians penalize the player if shot
- Teleportation portals within the stage
- Progressive difficulty with more obstacles and civilians per stage
- Game over conditions including ammo depletion and negative score

## UML Class Diagram

![Angry Tao UML Class Diagram](![alt text](image.png))

*Figure: UML class diagram showing the main classes and relationships in the Angry Tao project.*

## Explanation

- **Game**: Main controller handling game loop, events, and rendering.
- **Character**: Player-controlled sprite with weapons and shooting mechanics.
- **Items**: Weapon types with ammo and skill properties.
- **Stage**: Contains obstacles, enemies, civilians, and manages level generation.
- **Obstacle**: Static objects with health and destructibility.
- **Enemy**: Hostile sprites that the player must eliminate.
- **Civilian**: Non-hostile sprites that penalize the player if shot.

---

