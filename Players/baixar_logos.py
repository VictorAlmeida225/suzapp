"""
CLI para baixar PNGs com fundo transparente dos clubes listados.
Uso:
    python baixar_logos.py --out /caminho/da/pasta

Requisitos:
    pip install requests pillow
Opcional (para converter SVGs): pip install cairosvg
"""

import os
import argparse
import requests
from urllib.parse import quote
from PIL import Image

# lista de clubes
CLUBS = [
    "Arsenal Football Club",
    "Paris Saint-Germain",
    "Real Madrid Club de Futbol",
    "Barcelona",
    "Manchester City",
    "Manchester United",
    "Tottenham Hotspur",
    "Liverpool",
    "AC Milan",
    "Inter Milan",
    "Juventus",
    "Napoli",
    "AS Roma",
    "Chelsea",
    "Atlético Madrid",
    "AS Monaco",
    "Newcastle United",
]

USER_AGENT = "LogoDownloaderCLI/1.0 (https://example.com)"
session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def search_commons_file(query):
    api = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,
        "srlimit": 5,
    }
    try:
        r = session.get(api, params=params, timeout=15)
        r.raise_for_status()
        hits = r.json().get("query", {}).get("search", [])
        if hits:
            return hits[0]["title"]
    except Exception:
        pass
    return None


def get_image_url(file_title):
    api = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "titles": file_title,
        "iiprop": "url|mime|size",
    }
    r = session.get(api, params=params, timeout=15)
    r.raise_for_status()
    j = r.json()
    pages = j.get("query", {}).get("pages", {})
    for p in pages.values():
        iinfo = p.get("imageinfo")
        if iinfo:
            return iinfo[0]
    return None


def download_file(url, dest_path):
    r = session.get(url, stream=True, timeout=30)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(1024 * 32):
            if chunk:
                f.write(chunk)


def has_transparency(pil_image):
    if pil_image.mode in ("RGBA", "LA"):
        alpha = pil_image.split()[-1]
        return alpha.getextrema()[0] < 255
    if "transparency" in pil_image.info:
        return True
    return False


def convert_svg_to_png(svg_path, png_path, width=512):
    try:
        import cairosvg
    except ImportError:
        raise RuntimeError("cairosvg não instalado (pip install cairosvg)")
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=width)


def baixar_clubes(out_folder, clubs):
    os.makedirs(out_folder, exist_ok=True)
    for club in clubs:
        print(f"\n=== {club} ===")
        try:
            queries = [
                f"{club} logo png",
                f"{club} crest png",
                f"{club} badge png",
                f"{club} logo",
            ]
            file_title = None
            for q in queries:
                file_title = search_commons_file(q)
                if file_title:
                    break
            if not file_title:
                print("  Nenhum arquivo encontrado no Wikimedia Commons.")
                continue

            info = get_image_url(file_title)
            if not info:
                print("  Não foi possível obter informação do arquivo.")
                continue

            url = info.get("url")
            mime = info.get("mime", "")
            print(f"  Achado: {file_title} ({mime})")

            ext = os.path.splitext(url)[1].lower()
            safe_name = club.replace(" ", "_") + ".png"
            tmp_path = os.path.join(out_folder, "__tmp__" + safe_name)
            final_path = os.path.join(out_folder, safe_name)

            if ext == ".svg" or mime == "image/svg+xml":
                print("  Baixando SVG e convertendo...")
                download_file(url, tmp_path + ".svg")
                try:
                    convert_svg_to_png(tmp_path + ".svg", tmp_path)
                except Exception as e:
                    print("  Erro ao converter SVG:", e)
                    os.rename(tmp_path + ".svg", final_path.replace(".png", ".svg"))
                    continue
            else:
                print("  Baixando imagem...")
                download_file(url, tmp_path)

            try:
                img = Image.open(tmp_path)
            except Exception as e:
                print("  Erro abrindo imagem:", e)
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                continue

            if not has_transparency(img):
                print("  Atenção: imagem sem transparência detectada.")
            else:
                print("  Transparência OK.")

            img = img.convert("RGBA")
            img.save(final_path, "PNG")
            print(f"  Salvo em: {final_path}")

            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if os.path.exists(tmp_path + ".svg"):
                os.remove(tmp_path + ".svg")

        except Exception as e:
            print("  Erro:", e)
    print("\nDownload finalizado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Baixar PNGs dos clubes")
    parser.add_argument(
        "--out", type=str, default=".", help="Pasta de destino (default: atual)"
    )
    args = parser.parse_args()
    baixar_clubes(args.out, CLUBS)
