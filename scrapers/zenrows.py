import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

ZENROWS_APIKEY = "2dda1a3e01e2abf037d5a84dc9813ffe06fb4251"
URL = "https://beganesha.com/collections/new-collection"

async def main():
    async with async_playwright() as p:
        # 🔹 Conexión remota al navegador ZenRows
        browser = await p.chromium.connect_over_cdp(
            f"wss://browser.zenrows.com?apikey={ZENROWS_APIKEY}&proxy_country=uy"
        )

        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()
        await page.goto(URL, wait_until="networkidle")

        # 🔹 Hacer scroll para cargar todos los productos
        for _ in range(4):
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

        html = await page.content()
        await browser.close()

        # 🔹 Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        productos = []

        for item in soup.select("div.product-item, div.grid__item, div.card"):
            nombre = item.select_one(".card__heading, .product__title, .product-title")
            precio = item.select_one(".price-item, .product__price, .money")
            imagen = item.select_one("img")
            link = item.select_one("a[href]")

            if nombre and precio and imagen and link:
                # Normalizar URL de imagen y link
                img_url = imagen.get("src") or imagen.get("data-src")
                if img_url and img_url.startswith("//"):
                    img_url = "https:" + img_url
                link_url = link["href"]
                if not link_url.startswith("http"):
                    link_url = "https://beganesha.com" + link_url

                productos.append({
                    "nombre": nombre.get_text(strip=True),
                    "precio": precio.get_text(strip=True),
                    "imagen": img_url,
                    "link": link_url
                })

        # 🔹 Guardar en archivo JSON
        with open("productos-beganesha.json", "w", encoding="utf-8") as f:
            json.dump(productos, f, ensure_ascii=False, indent=2)

        print(f"✅ {len(productos)} productos guardados en productos-beganesha.json")

asyncio.run(main())


