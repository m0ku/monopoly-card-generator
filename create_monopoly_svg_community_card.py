import csv
import os

# local functions
import read
import convert

# card parameters
DPI = 150 # DPI setting
card_width = 86.5
card_height = 56

# community card - yellow #d3c70d
# activity card - organge #d2932d

def create_community_card_frontside(width, height, text):
    header_h = height * 0.20 # Etwas kleiner für den schwebenden Look
    margin = 12              # Abstand zum Kartenrand
    padding = 8              # Lücke zwischen Rahmen und Farbfeld
    color = "#d3c70d"        # yellow #d3c70d

    # Berechnungen für das schwebende Farbfeld
    rect_x = margin + padding
    rect_y = margin + padding
    rect_w = width - 2 * (margin + padding)
    
    # Titel-Position anpassen (Mitte des schwebenden Feldes)
    title_y = rect_y + (header_h / 2) + 6

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    
    <!-- Monopoly font embedded -->
    <style type="text/css">
        @font-face {{
        font-family: 'Monopoly';
        src: url(data:font/woff2;charset=utf-8;base64,{read.as_base64("font/MONOPOLY_INLINE.woff2")}) format('woff2');
        }}
        
        .monopoly-text-title {{
            font-family: 'Monopoly', sans-serif;
            font-weight: bold;
            font-size: {convert.millimeter_to_pixel(5, DPI)};
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
        .monopoly-text-small {{
            font-family: 'Monopoly', sans-serif;
            font-weight: normal;
            font-size: 11px;
        }}
    </style>
    
    <!-- 1. Äußerer Kartenrand -->
        <rect width="100%" height="100%" fill="{color}" stroke="black" stroke-width="2"/>
        <!-- 2. Innerer Rahmen -->
        <!-- rect x="{margin}" y="{margin}" width="{width - 2*margin}" height="{height - 2*margin}" fill="none" stroke="black" stroke-width="2"/ -->
        <image x="60%" y="0" width="100%" height="100%" xlink:href="data:image/svg+xml;base64,{read.as_base64("img/figure1.svg")}" />

        <!-- Text Bereich -->
        <foreignObject x="{margin}" y="40%" width="{width - 2*margin}" height="50%">
            <div xmlns="http://w3.org" 
                style="font-family: 'Monopoly'; font-size: 11px; text-align: center; padding: 5px;">
                {text}
            </div>
        </foreignObject>
</svg>'''
    return svg

def create_community_card_backside(width, height):
    margin = 12         # Abstand zum Kartenrand
    padding = 0         # Lücke zwischen Rahmen und Farbfeld
    color = "#877805"   # yellow #877805
    
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
    </style>
    
    
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
    if not os.path.exists("output/community"):
        os.makedirs("output/community")

    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file,  delimiter=';')
        for row in reader:
            # Karte generieren (mit deiner Original-Logik)
            svg_content = create_community_card_frontside(
                width=convert.millimeter_to_pixel(card_width, DPI), 
                height=convert.millimeter_to_pixel(card_height, DPI), 
                text=row['text']
            )
        
            filename = f"output/community/{row['name'].replace(' ', '_')}_front.svg"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print(f"file {filename} created")

            ## Karte generieren (mit deiner Original-Logik)
            #svg_content = create_community_card_backside(
            #    width=convert.millimeter_to_pixel(card_width, DPI), 
            #    height=convert.millimeter_to_pixel(card_height, DPI), 
            #)
        
            filename = f"output/community/{row['name'].replace(' ', '_')}_back.svg"
            #with open(filename, "w", encoding="utf-8") as f:
            #    f.write(svg_content)
            print(f"file {filename} created")

if __name__ == "__main__":
    # Falls du die CSV noch nicht hast, erstelle sie kurz mit den Spaltennamen:
    # name,farbe,preis,miete_basis,miete_1h,miete_2h,miete_3h,miete_4h,miete_hotel
    generate_from_csv('data/community_cards.csv')