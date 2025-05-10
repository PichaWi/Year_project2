from graphviz import Digraph

def generate_uml():
    dot = Digraph(comment='Game UML Diagram')

    # Adding Classes
    dot.node('Config', 'Config\n\n- game_width\n- game_height\n- piece_colors\n- game_color\n- fps')
    dot.node('Stage', 'Stage\n\n- health\n- name\n- stage_obstacles\n- enemies\n\n+ generate_obstacles()\n+ generate_enemies()\n+ check_stage_clear()')
    dot.node('Items', 'Items\n\n- name\n- skill\n- fixed_ammo\n\n+ use_skill()')
    dot.node('Character', 'Character\n\n- ammo\n- items_list\n- position\n\n+ move(dx, dy)\n+ add_item(item)')
    dot.node('Drawer', 'Drawer\n\n- screen\n\n+ draw_stage(stage)\n+ draw_character(character)\n+ draw_enemies(stage)')
    dot.node('UI', 'UI\n\n- screen\n- clock\n- font\n\n+ draw_text(text, pos)')
    dot.node('Game', 'Game\n\n- ui\n- character\n- stage\n- drawer\n- running\n\n+ game_reset()\n+ update_game()\n+ run()')

    # Adding Relations
    dot.edge('Game', 'UI', label='has')
    dot.edge('Game', 'Character', label='has')
    dot.edge('Game', 'Stage', label='has')
    dot.edge('Game', 'Drawer', label='has')
    dot.edge('Character', 'Items', label='has')

    # Render to file
    dot.render('game_uml_diagram', view=True)

if __name__ == '__main__':
    generate_uml()
