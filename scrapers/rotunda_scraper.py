from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import re
import requests


def get_best_image_url(raw_img):
    if not raw_img:
        return None
    if raw_img.startswith("//"):
        raw_img = "https:" + raw_img

    for size in ["800x1200", "400x600"]:
        candidate = re.sub(r"/\d+x\d+/", f"/{size}/", raw_img)
        try:
            res = requests.head(candidate, timeout=1)
            if res.status_code == 200:
                return candidate
        except requests.RequestException:
            continue
    return raw_img


def scrape_rotunda_scroll():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.rotundastore.com/clothes")

    # Scroll dinámico hasta el final real
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    productos = []

    for item in soup.select("div.it"):
        nombre_tag = item.select_one("div.info a.tit h2")
        precio_tag = item.select_one("div.info strong.precio span.monto")
        link_tag = item.select_one("div.info a.tit")
        img_tag = item.get("data-im")

        if not (nombre_tag and precio_tag and link_tag):
            continue

        nombre = nombre_tag.get_text(strip=True)
        precio = precio_tag.get_text(strip=True)
        link = link_tag["href"]
        if not link.startswith("http"):
            link = "https://www.rotundastore.com" + link

        # 🔥 Usa la función inteligente para elegir la mejor imagen
        imagen_final = get_best_image_url(img_tag)

        productos.append({
            "nombre": nombre,
            "precio": precio,
            "link": link,
            "imagen": imagen_final
        })

    print(f"✅ {len(productos)} productos obtenidos")
    with open("productos_rotunda.json", "w", encoding="utf-8") as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)

    return productos


if __name__ == "__main__":
    scrape_rotunda_scroll()