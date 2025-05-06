class Config:
    game_width = 1500
    game_height = 900

    piece_colors = [
        (255, 0, 0),     # Red
        (0, 255, 0),     # Green
        (0, 0, 255),     # Blue
        (255, 255, 0),   # Yellow
        (255, 165, 0),   # Orange
        (128, 0, 128),   # Purple
        (0, 255, 255),   # Cyan
    ]
    
    skill_properties = {
        'NORMAL': {'cooldown': 0, 'color': (169, 169, 169)},
        'SPREAD': {'cooldown': 1.5, 'color': (0, 128, 0)},
        'EXPLOSIVE': {'cooldown': 3.0, 'color': (255, 0, 0)},
        'SHATTER': {'cooldown': 2.0, 'color': (255, 255, 255)},
        'HEAT': {'cooldown': 2.5, 'color': (255, 69, 0)},
        'ICE': {'cooldown': 2.0, 'color': (0, 255, 255)}
    }

    game_color = {'W': (255, 255, 255), 'BL': (0, 0, 0), 'R': (255, 0, 0), 'G': (
        0, 255, 0), 'B': (0, 0, 255), 'LIGHTGRAY': (200, 200, 200),
                  'GLASS': (48, 207, 183), 'WOOD': (222, 88, 12), 'IRON': (191, 186, 184),
                  'DIAMOND': (12, 167, 220), 'GOLD': (248, 245, 39), 'BOMB': (0, 0, 0),
                  'VIBRANIUM': (75, 0, 130), 'NORMAL': (169, 169, 169), 'SPREAD': (0, 128, 0),
                  'EXPLOSIVE': (255, 0, 0), 'SHATTER': (255, 255, 255), 'HEAT': (255, 69, 0),
                  'ICE': (0, 255, 255), 'BORDER': (255, 0, 0)}

    fps = 60
    stage_middle_width = 700
    stage_side_width = 400
    stage_height = 700 # Adjust height for middle box
    obstacle_size = 50
    enemy_size = 30
    character_radius = 20
    bullet_radius = 10
    bullet_speed = 15