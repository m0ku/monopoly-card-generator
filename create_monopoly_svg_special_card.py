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

def create_special_card_frontside(width, height, title, image_path):
    # 1. Setup Jinja2 (sucht im Ordner 'templates')
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('special_card_front.svg.j2')

    margin = convert.millimeter_to_pixel(3, DPI) # Abstand zum Kartenrand
    padding = 8 # Lücke zwischen Rahmen und Farbfeld
    
    # Berechnungen für das schwebende Farbfeld
    width_dpi = convert.millimeter_to_pixel(width, DPI)
    height_dpi = convert.millimeter_to_pixel(height, DPI)
    header_h = height_dpi * 0.5 # Etwas kleiner für den schwebenden Look
    rect_x = margin + padding
    rect_y = margin + padding
    rect_w = width_dpi - 2 * (margin + padding)
    # Titel-Position anpassen (Mitte des schwebenden Feldes)
    title_y = header_h - 20

    # 3. Daten an das Template übergeben
    return template.render(
        width=width_dpi,
        height=height_dpi,
        title_size=22,
        font_size=12,
        font_b64=read.as_base64("font/MONOPOLY_INLINE.woff2"),
        img_b64=read.as_base64(image_path),
        title=title,
        margin=margin,
        title_y=title_y,
        rect_x=rect_x,
        rect_y=rect_y,
        rect_w=rect_w,
        header_h=header_h,
        inner_width = (width_dpi - 2*margin),
        inner_height = (height_dpi - 2*margin),
    )

def create_special_card_backside(width, height, title, rents):
    # 1. Setup Jinja2 (sucht im Ordner 'templates')
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('special_card_back.svg.j2')

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

def generate():
    if not os.path.exists("output/streets"):
        os.makedirs("output/streets")

    for name in ['Weingut Hemberger', 'Ulis Mühle']:        
        # Karte generieren (mit deiner Original-Logik)
        svg_content = create_special_card_frontside(
            width=card_width, 
            height=card_height,
            title=name, 
            image_path=f"img/{name}.svg", 
        )
    
        filename = f"output/streets/{name}_front.svg"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"file {filename} created")

        # Karte generieren (mit deiner Original-Logik)
        svg_content = create_special_card_backside(
            width=card_width,
            height=card_height,
            title=name,
            rents=[0, 75] 
        )

        filename = f"output/streets/{name}_back.svg"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"file {filename} created")

if __name__ == "__main__":
    # name,preis,hypothek
    generate()