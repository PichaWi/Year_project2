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

## Obstacle Types

The game features various obstacles distinguished by color, material, and health. Each obstacle type affects gameplay differently:

| Material   | Color       | Approximate Health | Description                          |
|------------|-------------|--------------------|------------------------------------|
| Glass      | Light Blue  | Low (e.g., 1 hit)  | Fragile, breaks easily              |
| Wood       | Brown       | Medium (e.g., 3 hits) | Moderate durability                |
| Iron       | Gray        | High (e.g., 5 hits) | Strong, requires multiple hits     |
| Diamond    | Cyan        | Very High (e.g., 7 hits) | Very tough, hard to destroy      |
| Gold       | Yellow      | High (e.g., 6 hits) | Valuable and durable                |
| Bomb       | Red         | Explodes on hit    | Causes area damage when destroyed   |
| Vibranium  | Dark Blue   | Very High (e.g., 8 hits) | Extremely durable, rare           |

*Black borders* are drawn around all obstacles to improve visibility against the background.

## Weapon Types

The player can use multiple weapons, each with unique skills, ammo capacity, and UI color coding:

| Weapon Name | Skill Type   | Ammo Capacity | UI Color  | Description                                  |
|-------------|--------------|---------------|-----------|----------------------------------------------|
| Normal      | Single Shot  | Moderate      | Gray      | Standard weapon with balanced performance    |
| Spread      | spread Shot   | Moderate      | Green     | Fires multiple bullets in a spread pattern   |
| Explosive   | Area Damage  | Low           | Red       | Bullets explode causing area damage          |
| Sniper      | High single shot     | Low           | White     | Bullets firing high damage      |
| Shotgun     | Triple shot  | Low           | Orange    | Bullets shooting three bullet in vertical line       |

Players can switch weapons during gameplay to adapt to different challenges

--------------

## Youtube link
-pass
