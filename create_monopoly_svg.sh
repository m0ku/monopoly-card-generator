#!/bin/sh
# under nixos run inside nix-shell for python to find cairosvg
. ./.venv/bin/activate
python create_monopoly_svg_chance_card.py 
python create_monopoly_svg_community_card.py 
python create_monopoly_svg_special_card.py 
python create_monopoly_svg_street_card.py 
python create_monopoly_svg_train_station.py
deactivate