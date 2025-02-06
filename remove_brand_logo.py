import os
import fitz
from PIL import Image, ImageDraw
import argparse
from collections import Counter

def parse_offset_list(offset_list):
    """Parse the offset list string into a set of page numbers to skip."""
    offsets = set()
    if offset_list:
        for part in offset_list.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                offsets.update(range(start, end + 1))
            else:
                offsets.add(int(part))
    return offsets

def get_background_color(img):
    """Get the dominant background color by sampling the corners of the image."""
    width, height = img.size
    corners = [
        img.getpixel((0, 0)),  # Top-left
        img.getpixel((width - 1, 0)),  # Top-right
        img.getpixel((0, height - 1)),  # Bottom-left
        img.getpixel((width - 1, height - 1)),  # Bottom-right
    ]
    dominant_color = Counter(corners).most_common(1)[0][0]
    return dominant_color

def remove_branding(source_path, destination_path, offset_list, rect_coords):
    offsets = parse_offset_list(offset_list)

    slide_images_dir = os.path.join(destination_path, 'slide_images')
    os.makedirs(slide_images_dir, exist_ok=True)

    pdf_document = fitz.open(source_path)

    for page_num in range(len(pdf_document)):
        if page_num + 1 in offsets:
            continue
        page = pdf_document.load_page(page_num)

        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        bg_color = get_background_color(img)

        draw = ImageDraw.Draw(img)
        draw.rectangle(rect_coords, fill=bg_color)

        img_path = os.path.join(slide_images_dir, f"{page_num + 1}.jpg")
        img.save(img_path)
        
    image_list = [os.path.join(slide_images_dir, img) for img in sorted(os.listdir(slide_images_dir), key=lambda x: int(x.split('.')[0]))]
    pdf_images = [Image.open(img).convert('RGB') for img in image_list]
    pdf_path = os.path.join(destination_path, 'output.pdf')
    pdf_images[0].save(pdf_path, save_all=True, append_images=pdf_images[1:])

    print(f"New PDF created at {pdf_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove branding from PDF files.")
    parser.add_argument("source_path", type=str, help="Path to the source PDF file")
    parser.add_argument("destination_path", type=str, help="Path to save the new PDF file")
    parser.add_argument("--offset_list", type=str, default="", help="Optional list of pages to skip (e.g., '1-3, 9')")
    parser.add_argument("--rect_coords", type=int, nargs=4, required=True, help="Coordinates of the rectangle to cover the branding (x1, y1, x2, y2)")

    args = parser.parse_args()

    remove_branding(args.source_path, args.destination_path, args.offset_list, args.rect_coords)
