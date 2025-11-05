from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

def is_valid_image(url: str) -> bool:
    """Filtra imágenes de producto válidas (no íconos, ni placeholders)."""
    if not url:
        return False
    if "fcdn.app/imgs" not in url:
        return False
    if any(bad in url.lower() for bad in ["icon", "logo", "cocarda", "tag", "label", "preventa"]):
        return False
    if any(size in url for size in ["/600x900/", "/800x1200/", "/1200x1800/"]):
        return True
    return False


def scrape_sierramora():
    """Scrapea todos los productos de Sierra Mora y guarda el JSON final."""
    options = Options()
    options.add_argument("--headless=new")  # quítalo si querés ver el navegador
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,3000")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.sierramorashop.com/shop")

    # --- Scroll dinámico hasta el final ---
    last_height = 0
    same_count = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            same_count += 1
            if same_count >= 3:
                break
        else:
            same_count = 0
        last_height = new_height

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    productos = []

    for item in soup.select("div.cnt"):
        nombre_tag = item.select_one("div.info a.tit h2")
        precio_tag = item.select_one("div.info strong.precio span.monto")
        link_tag = item.select_one("a.img")

        if not (nombre_tag and precio_tag and link_tag):
            continue

        nombre = nombre_tag.get_text(strip=True)
        precio = precio_tag.get_text(strip=True)
        link = link_tag["href"]
        if not link.startswith("http"):
            link = "https://www.sierramorashop.com" + link

        # --- Buscar imágenes (usa la primera válida) ---
        img_tags = item.select("a.img img")
        img_url = None
        for img in img_tags:
            src = img.get("src", "")
            if src.startswith("//"):
                src = "https:" + src
            if is_valid_image(src):
                img_url = src
                break

        productos.append({
            "nombre": nombre,
            "precio": precio,
            "link": link,
            "imagen": img_url,
            "marca": "Sierra Mora"
        })

    # --- Guardar productos en archivo final ---
    output_path = "productos_sierramora.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(productos)} productos guardados en {output_path}")
    return productos


if __name__ == "__main__":
    scrape_sierramora()












