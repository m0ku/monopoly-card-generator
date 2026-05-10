import csv
import os
from jinja2 import Environment, FileSystemLoader
import math

# local functions
import read
import convert

# card parameters
DPI = 150 # DPI setting
card_width = 66.6
card_height = 76

def create_street_card_frontside(width, height, color, title, price, rents):
    # 1. Setup Jinja2 (sucht im Ordner 'templates')
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('street_card_front.svg.j2')

    margin = convert.millimeter_to_pixel(3, DPI) # Abstand zum Kartenrand
    padding = 8 # Lücke zwischen Rahmen und Farbfeld
    
    # Berechnungen für das schwebende Farbfeld
    width_dpi = convert.millimeter_to_pixel(width, DPI)
    height_dpi = convert.millimeter_to_pixel(height, DPI)
    header_h = height_dpi * 0.20 # Etwas kleiner für den schwebenden Look
    rect_x = margin + padding
    rect_y = margin + padding
    rect_w = width_dpi - 2 * (margin + padding)
    # Titel-Position anpassen (Mitte des schwebenden Feldes)
    title_y = rect_y + (header_h / 2) + 6

    # 3. Daten an das Template übergeben
    return template.render(
        width=width_dpi,
        height=height_dpi,
        color=color,
        title_size=22,
        font_size=12,
        font_b64=read.as_base64("font/MONOPOLY_INLINE.woff2"),
        img_b64=read.as_base64("img/figure1.svg"),
        title=title,
        price=price,
        rents=rents,
        margin=margin,
        title_y=title_y,
        rect_x=rect_x,
        rect_y=rect_y,
        rect_w=rect_w,
        header_h=header_h,
        inner_width = (width_dpi - 2*margin),
        inner_height = (height_dpi - 2*margin),
    )

def create_street_card_backside(width, height, title, price, rents):
    # 1. Setup Jinja2 (sucht im Ordner 'templates')
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('street_card_back.svg.j2')

    margin = convert.millimeter_to_pixel(3, DPI) # Abstand zum Kartenrand
    padding = 8 # Lücke zwischen Rahmen und Farbfeld
    
    # Berechnungen für das schwebende Farbfeld
    width_dpi = convert.millimeter_to_pixel(width, DPI)
    height_dpi = convert.millimeter_to_pixel(height, DPI)
    header_h = height_dpi - 2 * (margin + padding)
    rect_x = margin + padding
    rect_y = margin + padding
    rect_w = width_dpi - 2 * (margin + padding)
    # Titel-Position anpassen (Mitte des schwebenden Feldes)
    title_y = rect_y + (header_h / 2) + 6


    # 3. Daten an das Template übergeben
    return template.render(
        width=width_dpi,
        height=height_dpi,
        title_size=22,
        font_size=14,
        font_b64=read.as_base64("font/MONOPOLY_INLINE.woff2"),
        img_b64=read.as_base64("img/figure1.svg"),
        title=title,
        price=price,
        rents=rents,
        margin=margin,
        title_y=title_y,
        rect_x=rect_x,
        rect_y=rect_y,
        rect_w=rect_w,
        header_h=header_h,
        inner_width = (width_dpi - 2*margin),
        inner_height = (height_dpi - 2*margin),
        math=math
    )

def create_street_card_backside_bak(width, height, title, price, rents):
    margin = 12              # Abstand zum Kartenrand
    padding = 0          # Lücke zwischen Rahmen und Farbfeld
    color = "#FF0000"
    
    # Berechnungen für das schwebende Farbfeld
    rect_x = margin + padding
    rect_y = margin + padding
    header_h = height - 2 * (margin + padding)
    rect_w = width - 2 * (margin + padding)
    
    # Titel-Position anpassen (Mitte des schwebenden Feldes)
    title_y = rect_y + height * 0.23

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    
    <!-- Monopoly font embedded -->
    <style type="text/css">
        @font-face {{
        font-family: 'Monopoly';
        src: url(data:font/woff2;charset=utf-8;base64,{read.as_base64("font/MONOPOLY_INLINE.woff2")}) format('woff2');
        }}
        
        .monopoly-text-title {{
            font-family: 'Monopoly', sans-serif;
            font-weight: bold;
            font-size: 20px;
        }}
        .monopoly-text-bold {{
            font-family: 'Monopoly', sans-serif;
            font-weight: bold;
            font-size: 15px;
        }}
        .monopoly-text-normal {{
            font-family: 'Monopoly', sans-serif;
            font-weight: normal;
            font-size: 15px;
        }}
    </style> height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    
    
    <!-- 1. Äußerer Kartenrand -->
    <rect width="100%" height="100%" fill="white" stroke="black" stroke-width="2"/>
    
    <!-- 2. Schwebendes rotes Farbfeld (mit Abstand zum Rahmen) -->
    <rect x="{rect_x}" y="{rect_y}" width="{rect_w}" height="{header_h}" fill="{color}" stroke="white" stroke-width="1.5"/>
    
    <!-- Hypothekenbrief -->
    <text x="50%" y="{title_y}" text-anchor="middle" class="monopoly-text-bold" fill="white" style="text-transform: uppercase;">
        Hypothekenbrief
    </text>

    <!-- Titel -->
    <text x="50%" y="50%" text-anchor="middle" class="monopoly-text-title" fill="white" style="text-transform: uppercase;">
        {title}
    </text>

    <!-- Titel -->
    <text x="50%" y="{height //2 + 15}" text-anchor="middle" class="monopoly-text-normal" fill="white" style="text-transform: uppercase;">
        BELASTET MIT {int(price) // 2}€
    </text>
</svg>'''
    return svg

def generate_from_csv(csv_filename):
    if not os.path.exists("output/streets"):
        os.makedirs("output/streets")

    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Mieten aus CSV sammeln
            mieten = [
                row['miete_basis'], row['miete_1h'], row['miete_2h'], 
                row['miete_3h'], row['miete_4h'], row['miete_hotel'],
                row['kosten_haus'], row['kosten_hotel'], row['hypothek']
            ]
            
            # Karte generieren (mit deiner Original-Logik)
            svg_content = create_street_card_frontside(
                width=card_width, 
                height=card_height,
                color=row['farbe'], 
                title=row['name'], 
                price=int(row['preis']), 
                rents=mieten
            )
        
            filename = f"output/streets/{row['name'].replace(' ', '_')}_front.svg"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print(f"file {filename} created")

            # Karte generieren (mit deiner Original-Logik)
            svg_content = create_street_card_backside(
                width=card_width,
                height=card_height,
                title=row['name'], 
                price=int(row['preis']), 
                rents=mieten
            )

            filename = f"output/streets/{row['name'].replace(' ', '_')}_back.svg"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print(f"file {filename} created")

if __name__ == "__main__":
    # Falls du die CSV noch nicht hast, erstelle sie kurz mit den Spaltennamen:
    # name,farbe,preis,miete_basis,miete_1h,miete_2h,miete_3h,miete_4h,miete_hotel
    generate_from_csv('data/streets_present.csv')