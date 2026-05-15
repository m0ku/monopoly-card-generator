import os
import re
import io
import logging  # 1. Logging importieren

# 2. Den Root-Logger zwingend als ALLERERSTES konfigurieren!
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 3. Den spezifischen CairoSVG-Logger scharf schalten
logger = logging.getLogger('cairosvg')
logger.setLevel(logging.DEBUG)

# Erst danach die restlichen Bibliotheken importieren
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import cairosvg
import xml.etree.ElementTree as ET


def generate_duplex_cards_pdf(svg_folder, output_pdf, columns=3, rows=3, spacing_x_mm=0, spacing_y_mm=0, input_dpi=150):
    # Zielordner prüfen und ggf. erstellen
    output_dir = os.path.dirname(output_pdf)
    if output_dir and not os.path.exists(output_dir):
        print(f"Erstelle Ausgabeordner: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    page_width, page_height = A4  # Maße in Punkten (72 DPI)
    c = canvas.Canvas(output_pdf, pagesize=A4)
    
    # 1 mm = 72 / 25.4 Punkte
    mm_to_points = 72 / 25.4
    # Rechnet Ihre 150 DPI Quell-Pixel präzise in 72 DPI PDF-Punkte um
    pixel_to_points = 72 / input_dpi

    spacing_x = spacing_x_mm * mm_to_points
    spacing_y = spacing_y_mm * mm_to_points

    # Alle Dateien einlesen und Paare gruppieren
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

    # ERSTE KARTE LESEN: Verwendet Cairo, um die exakten Pixeldimensionen zu ermitteln
    with open(card_pairs[sorted_card_keys[0]]['front'], 'rb') as f:
        png_data = cairosvg.svg2png(file_obj=f)
        img = ImageReader(io.BytesIO(png_data))
        orig_w, orig_h = img.getSize()

    # Zielmaße im PDF (in Punkten)
    card_w = float(orig_w) * pixel_to_points
    card_h = float(orig_h) * pixel_to_points

    print(f"Erkannte Kartengröße im Druck: {card_w / mm_to_points:.1f}mm x {card_h / mm_to_points:.1f}mm")

    # Symmetrische Ränder mathematisch ermitteln
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
            render_duplex_page(c, current_page_fronts, current_page_backs, columns, rows, page_height, margin_x, margin_y, spacing_x, spacing_y, card_w, card_h)
            current_page_fronts = []
            current_page_backs = []

    if current_page_fronts:
        render_duplex_page(c, current_page_fronts, current_page_backs, columns, rows, page_height, margin_x, margin_y, spacing_x, spacing_y, card_w, card_h)

    c.save()
    print(f"PDF erfolgreich und ohne Artefakte gespeichert unter: {output_pdf}")


def draw_clean_svg(canvas_obj, svg_path, x, y, width, height):
    """ 
    Rendert das SVG via Cairo. 
    Betten eingebettete Base64-SVGs direkt als echte XML-Gruppen ein,
    damit Filter, Masken und IDs (Wasser/Strom) nicht verloren gehen.
    """
    abs_svg_path = os.path.abspath(svg_path)
    base_dir = os.path.dirname(abs_svg_path)
    file_name = os.path.basename(abs_svg_path)
    current_cwd = os.getcwd()
    
    try:
        os.chdir(base_dir)
        
        # Namensräume für den XML-Parser registrieren
        ET.register_namespace('', "http://w3.org")
        ET.register_namespace('xlink', "http://w3.org")
        
        tree = ET.parse(file_name)
        root = tree.getroot()
        
        # Suchen und Ersetzen von <image>-Tags, die SVG-Base64 enthalten
        elements_to_replace = []
        
        for parent in root.iter():
            # Wir suchen nach Kindern, die 'image' sind
            for child in list(parent):
                if child.tag.endswith('image'):
                    href = child.get('href') or child.get('{http://w3.org}href')
                    if href and "data:image/svg+xml;base64," in href:
                        elements_to_replace.append((parent, child, href))
        
        for parent, img_elem, href in elements_to_replace:
            try:
                # 1. Base64-Vektor-Daten extrahieren und dekodieren
                base64_data = href.split(',', 1)[1].strip()
                # Bereinigen von eventuellen Whitespaces aus dem SVG-Export
                base64_data = re.sub(r'\s+', '', base64_data)
                decoded_svg_bytes = base64.b64decode(base64_data)
                
                # 2. Das eingebettete SVG parsen
                sub_tree = ET.fromstring(decoded_svg_bytes)
                
                # 3. Umwandeln in eine Gruppe <g>, um Koordinaten (x, y) und Größe zu erhalten
                group_elem = ET.Element('{http://w3.org}g')
                
                # Kopiere Positionierungs-Attribute des alten Bild-Tags auf die neue Gruppe
                img_x = img_elem.get('x', '0')
                img_y = img_elem.get('y', '0')
                group_elem.set('transform', f'translate({img_x}, {img_y})')
                
                # Alle Kindelemente des inneren SVGs in die neue Gruppe übertragen
                for sub_child in list(sub_tree):
                    group_elem.append(sub_child)
                    
                # 4. Altes <image>-Tag durch die neue, native Grafikgruppe ersetzen
                idx = list(parent).index(img_elem)
                parent.remove(img_elem)
                parent.insert(idx, group_elem)
                
            except Exception as inner_e:
                print(f"  ⚠️ Fehler beim Inlinen eines Bildes in {file_name}: {inner_e}")
        
        # Das modifizierte, nun vollständig native SVG im RAM speichern
        svg_io = io.BytesIO()
        tree.write(svg_io, encoding='utf-8', xml_declaration=True)
        repaired_svg_bytes = svg_io.getvalue()
        
        # Render-Vorgang mit der vollständig verschmolzenen Vektordatei
        png_bytes = cairosvg.svg2png(
            bytestring=repaired_svg_bytes,
            unsafe=True
        )
        img_reader = ImageReader(io.BytesIO(png_bytes))
        canvas_obj.drawImage(img_reader, x, y, width=width, height=height)
            
    except Exception as e:
        print(f"  ❌ Schwerer Render-Fehler bei Datei {file_name}: {e}")
    finally:
        os.chdir(current_cwd)

def render_duplex_page(canvas_obj, fronts, backs, columns, rows, page_height, margin_x, margin_y, spacing_x, spacing_y, card_w, card_h):
    # --- SEITE A: VORDERSEITEN ---
    for index, svg_path in enumerate(fronts):
        col = index % columns
        row = index // columns
        x = margin_x + (col * (card_w + spacing_x))
        y = page_height - margin_y - ((row + 1) * card_h) - (row * spacing_y)
        
        draw_clean_svg(canvas_obj, svg_path, x, y, card_w, card_h)
    
    canvas_obj.showPage()

    # --- SEITE B: RÜCKSEITEN (Gespiegelt) ---
    for index, svg_path in enumerate(backs):
        col = index % columns
        row = index // columns
        mirrored_col = columns - 1 - col
        x = margin_x + (mirrored_col * (card_w + spacing_x))
        y = page_height - margin_y - ((row + 1) * card_h) - (row * spacing_y)
        
        draw_clean_svg(canvas_obj, svg_path, x, y, card_w, card_h)
        
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