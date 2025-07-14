import os
import fitz  # PyMuPDF
from PIL import Image
from collections import Counter
import argparse


def parse_offset_list(offset_list):
    """Analysiert die Offset-Listen-Zeichenkette in ein Set von zu überspringenden Seitenzahlen."""
    offsets = set()
    if offset_list:
        for part in offset_list.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                offsets.update(range(start, end + 1))
            else:
                offsets.add(int(part))
    return offsets


def get_background_color_from_page(page, rect_coords, dpi=150):
    """Ermittelt die dominante Hintergrundfarbe, indem die Ecken des Logo-Bereichs abgetastet werden."""
    # Erstelle ein Pixmap nur vom relevanten Bereich, um die Eckenfarbe zu bestimmen
    # Dies ist ein Kompromiss, um nicht die ganze Seite rendern zu müssen.
    # Wir nehmen an, dass die Farbe in den Ecken des Dokuments die Hintergrundfarbe ist.
    clip_rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)

    # Temporäres Pixmap mit höherer Auflösung für bessere Farbgenauigkeit
    pix = page.get_pixmap(dpi=dpi, clip=clip_rect)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Proben von den vier Ecken der Seite nehmen
    width, height = img.size
    corners = [
        img.getpixel((0, 0)),
        img.getpixel((width - 1, 0)),
        img.getpixel((0, height - 1)),
        img.getpixel((width - 1, height - 1)),
    ]
    # Finde die häufigste Farbe unter den Ecken
    dominant_color = Counter(corners).most_common(1)[0][0]

    # Konvertiere die Farbe für fitz (Werte von 0-1 statt 0-255)
    return tuple(c / 255.0 for c in dominant_color)


def remove_branding_high_res(source_path, destination_folder, offset_list, rect_coords):
    """
    Entfernt das Branding aus einer PDF-Datei, erhält die Textmarkierung
    und speichert das Ergebnis in hoher Qualität.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    offsets = parse_offset_list(offset_list)

    # rect_coords ist (x1, y1, x2, y2)
    rect_to_cover = fitz.Rect(rect_coords)

    try:
        pdf_document = fitz.open(source_path)
    except fitz.fitz.FitzError as e:
        print(f"Fehler beim Öffnen der PDF-Datei: {e}")
        return

    # Erstelle ein neues, leeres PDF-Dokument für die Ausgabe
    new_pdf = fitz.open()

    for page_num in range(len(pdf_document)):
        if page_num + 1 in offsets:
            print(f"Überspringe Seite {page_num + 1}.")
            continue

        page = pdf_document.load_page(page_num)

        # Ermittle die Hintergrundfarbe der Seite
        try:
            bg_color_normalized = get_background_color_from_page(page, rect_coords)
        except Exception as e:
            print(
                f"Warnung: Konnte Hintergrundfarbe für Seite {page_num + 1} nicht ermitteln. Verwende Weiß. Fehler: {e}"
            )
            bg_color_normalized = (1.0, 1.0, 1.0)  # Standardmäßig Weiß

        # Zeichne ein Rechteck über den zu verdeckenden Bereich
        # Das Rechteck wird mit der ermittelten Hintergrundfarbe gefüllt
        # 'fill_opacity=1' sorgt für eine vollständige Abdeckung
        page.draw_rect(
            rect_to_cover,
            fill=bg_color_normalized,
            color=bg_color_normalized,  # Randfarbe gleich Füllfarbe
            fill_opacity=1,
            overlay=True,  # Stellt sicher, dass es über dem vorhandenen Inhalt gezeichnet wird
        )

        # Füge die bearbeitete Seite dem neuen PDF hinzu
        new_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)

    if new_pdf.page_count > 0:
        # Speichere das neue PDF
        output_filename = "output_high_res_text.pdf"
        pdf_path = os.path.join(destination_folder, output_filename)

        # 'garbage=4' bereinigt ungenutzte Objekte, 'deflate=True' komprimiert den Inhalt
        new_pdf.save(pdf_path, garbage=4, deflate=True)
        print(f"Neues PDF mit markierbarem Text erstellt unter: {pdf_path}")
    else:
        print(
            "Keine Seiten zum Speichern vorhanden. Das neue PDF wurde nicht erstellt."
        )

    new_pdf.close()
    pdf_document.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Entfernt Branding aus PDF-Dateien und erhält die Textmarkierbarkeit."
    )
    parser.add_argument("source_path", type=str, help="Pfad zur Quell-PDF-Datei")
    parser.add_argument(
        "destination_path", type=str, help="Pfad zum Speicherort für die neue PDF-Datei"
    )
    parser.add_argument(
        "--offset_list",
        type=str,
        default="",
        help="Optionale Liste von zu überspringenden Seiten (z.B., '1-3,9')",
    )
    parser.add_argument(
        "--rect_coords",
        type=int,
        nargs=4,
        required=True,
        help="Koordinaten des Rechtecks zum Abdecken des Brandings (x1 y1 x2 y2)",
    )

    args = parser.parse_args()

    remove_branding_high_res(
        args.source_path, args.destination_path, args.offset_list, args.rect_coords
    )
