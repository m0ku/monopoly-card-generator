import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

def generate_duplex_cards_pdf(svg_folder, output_pdf, columns=3, rows=3, spacing_x_mm=0, spacing_y_mm=0, input_dpi=150):
    # Ordner erstellen falls nicht vorhanden
    output_dir = os.path.dirname(output_pdf)
    if output_dir and not os.path.exists(output_dir):
        print(f"Erstelle Ausgabeordner: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    page_width, page_height = A4  # Maße in ReportLab-Punkten (72 DPI)
    c = canvas.Canvas(output_pdf, pagesize=A4)
    
    # Konvertierungsfaktoren
    # 1 mm = 72 / 25.4 Punkte
    mm_to_points = 72 / 25.4
    # Pixel (aus 150 DPI SVG) in ReportLab-Punkte (72 DPI) umrechnen
    pixel_to_points = 72 / input_dpi

    # Abstände von mm in Punkte umrechnen
    spacing_x = spacing_x_mm * mm_to_points
    spacing_y = spacing_y_mm * mm_to_points

    all_files = os.listdir(svg_folder)
    card_pairs = {}
    for f in all_files:
        if f.endswith('_front.svg'):
            base_name = re.sub(r'_front\.svg$', '', f)
            if base_name not in card_pairs: card_pairs[base_name] = {}
            card_pairs[base_name]['front'] = os.path.join(svg_folder, f)
        elif f.endswith('_back.svg'):
            base_name = re.sub(r'_back\.svg$', '', f)
            if base_name not in card_pairs: card_pairs[base_name] = {}
            card_pairs[base_name]['back'] = os.path.join(svg_folder, f)

    sorted_card_keys = sorted([k for k, v in card_pairs.items() if 'front' in v and 'back' in v])
    if not sorted_card_keys:
        print("Keine passenden _front.svg und _back.svg Paare gefunden.")
        return

    # Erste Karte laden, um die Original-Pixelmaße zu ermitteln
    first_drawing = svg2rlg(card_pairs[sorted_card_keys[0]]['front'])
    
    # Zielmaße im PDF (in Punkten) berechnen
    card_w = float(first_drawing.width) * pixel_to_points
    card_h = float(first_drawing.height) * pixel_to_points

    # Ausgabekontrolle für Sie im Terminal
    print(f"Erkannte Kartengröße im Druck: {card_w / mm_to_points:.1f}mm x {card_h / mm_to_points:.1f}mm")

    # Automatische Berechnung der perfekt zentrierten Ränder (in Punkten)
    total_grid_w = (columns * card_w) + ((columns - 1) * spacing_x)
    total_grid_h = (rows * card_h) + ((rows - 1) * spacing_y)
    
    margin_x = (page_width - total_grid_w) / 2
    margin_y = (page_height - total_grid_h) / 2

    if margin_x < 0 or margin_y < 0:
        print("WARNUNG: Die Karten passen mit diesen Dimensionen nicht auf ein A4 Blatt!")

    current_page_fronts = []
    current_page_backs = []
    max_items_per_page = columns * rows

    for key in sorted_card_keys:
        current_page_fronts.append(card_pairs[key]['front'])
        current_page_backs.append(card_pairs[key]['back'])
        
        if len(current_page_fronts) == max_items_per_page:
            render_duplex_page(c, current_page_fronts, current_page_backs, columns, rows, page_height, margin_x, margin_y, spacing_x, spacing_y, card_w, card_h, pixel_to_points)
            current_page_fronts = []
            current_page_backs = []

    if current_page_fronts:
        render_duplex_page(c, current_page_fronts, current_page_backs, columns, rows, page_height, margin_x, margin_y, spacing_x, spacing_y, card_w, card_h, pixel_to_points)

    c.save()
    print(f"PDF erfolgreich gespeichert unter: {output_pdf}")

def render_duplex_page(canvas_obj, fronts, backs, columns, rows, page_height, margin_x, margin_y, spacing_x, spacing_y, card_w, card_h, scale_factor):
    # --- SEITE A: VORDERSEITEN ---
    for index, svg_path in enumerate(fronts):
        drawing = svg2rlg(svg_path)
        col = index % columns
        row = index // columns
        
        x = margin_x + (col * (card_w + spacing_x))
        y = page_height - margin_y - ((row + 1) * card_h) - (row * spacing_y)
        
        # SVG-Objekt intern auf die korrekte Druckgröße skalieren
        drawing.width *= scale_factor
        drawing.height *= scale_factor
        drawing.scale(scale_factor, scale_factor)
        
        drawing.drawOn(canvas_obj, x, y)
    
    canvas_obj.showPage()

    # --- SEITE B: RÜCKSEITEN (Gespiegelt) ---
    for index, svg_path in enumerate(backs):
        drawing = svg2rlg(svg_path)
        col = index % columns
        row = index // columns
        mirrored_col = columns - 1 - col
        
        x = margin_x + (mirrored_col * (card_w + spacing_x))
        y = page_height - margin_y - ((row + 1) * card_h) - (row * spacing_y)
        
        # SVG-Objekt intern auf die korrekte Druckgröße skalieren
        drawing.width *= scale_factor
        drawing.height *= scale_factor
        drawing.scale(scale_factor, scale_factor)
        
        drawing.drawOn(canvas_obj, x, y)
        
    canvas_obj.showPage()


# --- PARAMETER ANPASSEN UND STARTEN ---
generate_duplex_cards_pdf(
    svg_folder="output/streets/", 
    output_pdf="output/print/street.pdf", 
    columns=3,     
    rows=3,        
    spacing_x_mm=2,   # Abstand zwischen Karten in mm (z.B. 2mm Platz für das Schneidemesser)
    spacing_y_mm=2,   
    input_dpi=150     # Konstante Ihrer SVG-Erstellung
)