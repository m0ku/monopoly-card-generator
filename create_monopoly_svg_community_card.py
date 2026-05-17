import csv
import os
from jinja2 import Environment, FileSystemLoader

# local functions
import read
import convert

# card parameters
DPI = 300
# card dimension in mm
card_width = 86.5
card_height = 56
activity_card_color = "#f5da0f"
 
def create_community_card_frontside(width, height, text):
    # 1. Setup Jinja2 (sucht im Ordner 'templates')
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('community_card_front.svg.j2')

    # 2. Text-Logik (Berechnung bleibt in Python)
    max_chars = 30
    words = text.upper().split()
    lines, current_line = [], []
    for word in words:
        if len(" ".join(current_line + [word])) <= max_chars:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))

    # 3. Daten an das Template übergeben
    return template.render(
        width=convert.millimeter_to_pixel(width, DPI),
        height=convert.millimeter_to_pixel(height, DPI),
        color=activity_card_color,
        title_size=40,
        font_size=24,
        font_b64=read.as_base64("font/MONOPOLY_INLINE.woff2"),
        img_b64=read.as_base64("img/figure1.svg"),
        lines=lines
    )


def create_community_card_backside(width, height):
    # 1. Setup Jinja2 (sucht im Ordner 'templates')
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('community_card_back.svg.j2')

    # 3. Daten an das Template übergeben
    return template.render(
        width=convert.millimeter_to_pixel(width, DPI),
        height=convert.millimeter_to_pixel(height, DPI),
        color=activity_card_color,
        title_size=40,
        font_size=24,
        font_b64=read.as_base64("font/MONOPOLY_INLINE.woff2"),
        img_b64=read.as_base64("img/treasure_chest.svg")
    )

def generate_from_csv(csv_filename):
    if not os.path.exists("output/community"):
        os.makedirs("output/community")

    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file,  delimiter=';')
        for row in reader:
            # Karte generieren (mit deiner Original-Logik)
            svg_content = create_community_card_frontside(
                width=card_width, 
                height=card_height,
                text=row['text']
            )
        
            filename = f"output/community/{row['name'].replace(' ', '_')}_front.svg"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print(f"file {filename} created")

            ## Karte generieren (mit deiner Original-Logik)
            svg_content = create_community_card_backside(
                width=card_width,
                height=card_height
            )
        
            filename = f"output/community/{row['name'].replace(' ', '_')}_back.svg"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print(f"file {filename} created")

if __name__ == "__main__":
    # Falls du die CSV noch nicht hast, erstelle sie kurz mit den Spaltennamen:
    # name,farbe,preis,miete_basis,miete_1h,miete_2h,miete_3h,miete_4h,miete_hotel
    generate_from_csv('data/community_cards.csv')