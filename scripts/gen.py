from playwright.sync_api import sync_playwright
from PIL import Image
import os

HTML_FILE = "../transaction-fail-update-template/transaction-fail-update-template.html"
FULL_IMG = "../transaction-fail-update-template/email_full.png"
THUMB_IMG = "../transaction-fail-update-template/email_thumb.png"
THUMB_HEIGHT = 600  # fixed height for thumbnail

def take_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 2000})  # larger viewport to prevent clipping

        # Load local HTML file
        path = f"file://{os.path.abspath(HTML_FILE)}"
        page.goto(path)

        # Wait for full body render
        page.wait_for_selector("body")

        # Get body dimensions
        body_element = page.query_selector("body")
        body_box = body_element.bounding_box()

        if not body_box:
            print("❌ Could not determine body bounding box.")
            browser.close()
            return

        # Calculate centered 600px-wide box
        center_x = body_box['x'] + (body_box['width'] - 600) / 2
        crop_box = {
            'x': center_x,
            'y': body_box['y'],
            'width': 600,
            'height': body_box['height']
        }

        # Screenshot full page
        temp_img = "temp_full.png"
        page.screenshot(path=temp_img, full_page=True)
        browser.close()

        # Open, crop, save
        with Image.open(temp_img) as img:
            cropped = img.crop((
                int(crop_box['x']),
                int(crop_box['y']),
                int(crop_box['x'] + crop_box['width']),
                int(crop_box['y'] + crop_box['height'])
            ))
            cropped.save(FULL_IMG, optimize=True)

            # ✅ Crop top 400px for thumbnail
            thumb = cropped.crop((0, 0, cropped.width, min(THUMB_HEIGHT, cropped.height)))
            thumb.save(THUMB_IMG, optimize=True)

        os.remove(temp_img)

        print(f"✅ Full image saved to: {FULL_IMG}")
        print(f"✅ Thumbnail saved to: {THUMB_IMG}")

if __name__ == "__main__":
    take_screenshot()
