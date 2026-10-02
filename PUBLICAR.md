# Cómo publicar Knock-on Lab

## 0. La carpeta

Tu juego ya está integrado como `index.html`, con los metadatos en inglés en el `<head>`. Contenido:

```
knockon-lab/
├── index.html          ← tu juego + metadatos SEO y vista previa social
├── favicon.svg         ← icono de la pestaña
├── og-image.jpg        ← portada al compartir el enlace (1200×630)
├── robots.txt          ← permite que Google indexe
├── sitemap.xml         ← le dice a Google qué páginas hay
├── netlify.toml        ← configuración de Netlify
├── LICENSE             ← licencia MIT (cámbiala si prefieres otra)
├── CITATION.cff        ← para el DOI de Zenodo
├── README.md           ← portada del repositorio en GitHub
├── ITCHIO.md           ← textos listos para la página de itch.io
└── preparar_publicacion.py
```

Autor, ORCID y URL ya están completados en todos los archivos.

## 1. Netlify (la web principal)

1. Entra en https://app.netlify.com/drop y arrastra la carpeta entera.
2. Crea una cuenta gratuita cuando te lo pida, para que el sitio no caduque.
3. En *Site configuration → Change site name* ponle un nombre, por ejemplo `knockonlab` → queda `https://knockonlab.netlify.app`.
4. Ya con la URL definitiva, en tu terminal:
   ```
   python preparar_publicacion.py --url https://knockonlab.netlify.app
   ```
   Esto sustituye `TU-SITIO` en todos los archivos y valida la carpeta.
5. Vuelve a arrastrar la carpeta en *Deploys* para subir la versión con la URL correcta.

Comprobaciones finales:
- Abre la URL en el móvil.
- Pega el enlace en un chat de WhatsApp contigo mismo: debe salir la imagen de portada. Si no aparece, usa https://www.opengraph.xyz para ver qué falla.

## 2. Google

1. Entra en https://search.google.com/search-console, añade la propiedad con tu URL y verifícala (Netlify permite el método de etiqueta HTML: pegas la `<meta>` que te den en el `<head>` y vuelves a subir).
2. En *Sitemaps* envía `sitemap.xml`.
3. En *Inspección de URLs* pega tu URL y pulsa *Solicitar indexación*.

La indexación tarda de días a semanas. Lo que más acelera que aparezca bien posicionado son los enlaces desde sitios con autoridad: la web del INL, la página de tu grupo, una universidad.

## 3. itch.io (el escaparate)

1. Genera el zip:
   ```
   python preparar_publicacion.py --zip
   ```
   → `dist/knockon-lab-itch.zip`, con index.html en la raíz y sin los archivos internos.
2. En itch.io: *Upload new project*.
   - **Kind of project:** HTML
   - Sube el zip y marca *This file will be played in the browser*.
   - **Viewport:** pon las dimensiones con las que se ve bien tu juego y activa *Fullscreen button*; si es adaptable, activa también *Mobile friendly*.
   - **Classification:** Games · **Genre:** Educational / Simulation
   - **Tags:** `educational`, `science`, `physics`, `simulation`, `chemistry`, `microscopy`, `atoms`
   - **Pricing:** *No payments* (o *$0 or donate*).
3. Copia los textos de `ITCHIO.md`, sube `og-image.jpg` como *Cover image* (itch.io recomienda 630×500; puedes recortarla) y añade 3–5 capturas o un GIF.
4. En la descripción, enlaza a la versión de Netlify.

## 4. GitHub + Zenodo (DOI citable, opcional)

1. Crea un repositorio público `knockon-lab` en GitHub y sube la carpeta.
2. En https://zenodo.org entra con GitHub, ve a *GitHub* y activa el repositorio.
3. En GitHub crea una *Release* (`v1.0.0`). Zenodo genera el DOI automáticamente usando `CITATION.cff`.
4. Bonus: en *Settings → Pages* del repositorio puedes activar GitHub Pages como espejo gratuito de la web.

## Antes de cada actualización

```
python preparar_publicacion.py --zip
```
Sube la carpeta a Netlify, el zip nuevo a itch.io, y si es un cambio importante haz una nueva Release en GitHub (Zenodo crea una versión nueva del DOI).
