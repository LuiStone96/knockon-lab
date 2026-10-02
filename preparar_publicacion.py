"""
preparar_publicacion.py — valida la carpeta de Knock-on Lab y genera el .zip para itch.io.

Uso (desde la carpeta del juego):
    python preparar_publicacion.py                                   # solo valida
    python preparar_publicacion.py --url https://knockonlab.netlify.app   # sustituye TU-SITIO y valida
    python preparar_publicacion.py --zip                             # valida y crea dist/knockon-lab-itch.zip
"""
import argparse, re, sys, zipfile
from pathlib import Path

PLACEHOLDER = "https://TU-SITIO.netlify.app"
TEXT_FILES = ["index.html", "robots.txt", "sitemap.xml", "CITATION.cff"]
# Archivos que NO deben ir dentro del zip de itch.io
EXCLUDE = {"preparar_publicacion.py", "PUBLICAR.md", "ITCHIO.md",
           "README.md", "CITATION.cff", "netlify.toml", ".DS_Store", "Thumbs.db"}
EXCLUDE_DIRS = {"dist", ".git", "__pycache__", "node_modules"}

def ok(msg):   print(f"  [OK]    {msg}")
def warn(msg): print(f"  [AVISO] {msg}")
def err(msg):  print(f"  [ERROR] {msg}")

def substitute_url(root: Path, url: str):
    url = url.rstrip("/")
    for name in TEXT_FILES:
        p = root / name
        if p.exists():
            t = p.read_text(encoding="utf-8")
            if PLACEHOLDER in t:
                p.write_text(t.replace(PLACEHOLDER, url), encoding="utf-8")
                print(f"  URL sustituida en {name}")

def validate(root: Path) -> int:
    n_err = 0
    print(f"\nValidando {root.resolve()}\n")
    index = root / "index.html"
    if not index.exists():
        err("No hay index.html en la raíz de la carpeta (itch.io y Netlify lo necesitan ahí).")
        return 1
    ok("index.html en la raíz")
    html = index.read_text(encoding="utf-8", errors="replace")

    checks = {
        "viewport (móvil)": r'<meta[^>]+name=["\']viewport',
        "<title>": r"<title>[^<]{5,}</title>",
        "meta description": r'<meta[^>]+name=["\']description',
        "og:image": r'<meta[^>]+property=["\']og:image["\']',
        "favicon": r'<link[^>]+rel=["\']icon',
        "lang en <html>": r"<html[^>]+lang=",
    }
    for label, pat in checks.items():
        if re.search(pat, html, re.I): ok(label)
        else: warn(f"Falta {label} en el <head>")

    m = re.search(r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)', html, re.I)
    if m and not m.group(1).startswith("http"):
        err(f"og:image debe ser URL absoluta (https://...), ahora es: {m.group(1)}"); n_err += 1

    for name in TEXT_FILES:
        p = root / name
        if p.exists() and "TU-SITIO" in p.read_text(encoding="utf-8"):
            warn(f"{name} aún contiene TU-SITIO → ejecuta con --url <tu URL>")

    # Referencias locales (src/href) que no existen o usan rutas que se rompen en itch.io
    scan = re.sub(r'<link[^>]+rel=["\'](?:canonical|preconnect)["\'][^>]*>', '', html, flags=re.I)
    refs = re.findall(r'(?:src|href)=["\']([^"\'#?]+)', scan, re.I)
    external = sorted({r for r in refs if r.startswith(("http://", "https://", "//"))})
    for r in refs:
        if r.startswith(("http://", "https://", "//", "data:", "mailto:", "javascript:")):
            continue
        if re.match(r"^(file:|[A-Za-z]:\\|/Users/|/home/)", r):
            err(f"Ruta de tu ordenador en el HTML: {r}"); n_err += 1
        elif r.startswith("/"):
            warn(f"Ruta absoluta '{r}': funciona en Netlify pero suele romperse en itch.io. Usa '{r.lstrip('/')}'")
        elif not (root / r).exists():
            err(f"Archivo referenciado no encontrado: {r}"); n_err += 1
    if external:
        warn("Recursos externos (el juego necesitará internet):")
        for r in external: print(f"            {r}")

    # Mayúsculas/minúsculas: Netlify (Linux) distingue, Windows/macOS no
    names = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    lower = {n.lower(): n for n in names}
    for r in refs:
        if not r.startswith(("http", "//", "data:", "/")) and r not in names and r.lower() in lower:
            err(f"'{r}' existe como '{lower[r.lower()]}' — en el servidor fallará por mayúsculas"); n_err += 1

    size = sum(p.stat().st_size for p in root.rglob("*") if p.is_file()
               and not any(d in p.parts for d in EXCLUDE_DIRS))
    ok(f"Tamaño total: {size/1e6:.2f} MB")
    for f in ["og-image.jpg", "favicon.svg", "robots.txt", "sitemap.xml"]:
        (ok if (root / f).exists() else warn)(f"{f} {'presente' if (root/f).exists() else 'no encontrado'}")

    print(f"\nResultado: {n_err} error(es).\n")
    return n_err

def make_zip(root: Path):
    out = root / "dist" / "knockon-lab-itch.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            rel = p.relative_to(root)
            if p.is_file() and p.name not in EXCLUDE and not any(d in rel.parts for d in EXCLUDE_DIRS):
                z.write(p, rel.as_posix())   # index.html queda en la raíz del zip
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    print(f"Zip creado: {out}  ({out.stat().st_size/1e6:.2f} MB, {len(names)} archivos)")
    for n in names: print(f"    {n}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".", help="carpeta del juego")
    ap.add_argument("--url", help="URL pública final, p. ej. https://knockonlab.netlify.app")
    ap.add_argument("--zip", action="store_true", help="crear dist/knockon-lab-itch.zip")
    a = ap.parse_args()
    root = Path(a.dir)
    if a.url: substitute_url(root, a.url)
    n = validate(root)
    if a.zip:
        if n: print("No creo el zip hasta corregir los errores."); sys.exit(1)
        make_zip(root)
