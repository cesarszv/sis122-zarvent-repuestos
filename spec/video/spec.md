# Plan: Video Remotion Aislado en `video/`

## Summary

Crear todo el proyecto de video exclusivamente dentro de `/home/cszv/cesarszv/ucb-lia/sis122/assignments/final_project/video`. La app académica queda intacta: nada de Remotion, assets, dependencias, renders o configs debe escribirse en `src/`, `docs/`, `database/`, `spec/`, `presentation/` ni en la raíz del proyecto.

El entregable será un video principal de **2:30 exactos**: `150s * 30fps = 4500 frames`, formato **1920x1080**, con voz en español, música, subtítulos y estética premium.

## Key Changes

- Usar `video/` como raíz única del subproyecto Remotion.
- Scaffold directo dentro de `video/` porque está vacío:
  - `cd /home/cszv/cesarszv/ucb-lia/sis122/assignments/final_project/video`
  - `npx create-video@latest --yes --blank --no-tailwind .`
- Mantener dentro de `video/`:
  - `package.json`, `src/`, `public/`, configs Remotion/Vite/TS.
  - assets copiados o generados para el video.
  - capturas, audio, subtítulos, stills y renders.
  - salida final en `video/out/zarvent-presentation.mp4`.
- Leer el proyecto principal solo como fuente de contenido: `README.md`, `docs/analysis`, `docs/database`, `database/schema.sql`, templates Flask, logo/banner y mockups existentes.
- No modificar archivos fuera de `video/`.

## Composition

- Crear composición:
  - `id="ZarventPresentation"`
  - `fps={30}`
  - `width={1920}`
  - `height={1080}`
  - `durationInFrames={4500}`
- Usar `src/data/videoScript.ts` para escenas, textos, narración y tiempos.
- Usar `staticFile()` para assets en `video/public/`.
- Animar solo con `useCurrentFrame()`, `interpolate()`, `Easing.bezier()` y `<Sequence>`.
- Prohibido usar CSS animations, CSS transitions o Tailwind animation classes.

## Timeline Exacto

- `0-10s` / `0-300f`: apertura cinematográfica con logo y título “Zarvent Repuestos”.
- `10-25s` / `300-750f`: problema manual: papel, Excel, WhatsApp, stock dudoso, clientes duplicados.
- `25-42s` / `750-1260f`: actores y flujo del negocio.
- `42-65s` / `1260-1950f`: ERD y entidades centrales.
- `65-90s` / `1950-2700f`: MySQL, PK, FK, integridad, precio histórico y stock.
- `90-118s` / `2700-3540f`: demo visual: login, dashboard, inventario, clientes, venta, recibo.
- `118-137s` / `3540-4110f`: alcance honesto: demo actual vs ERD completo.
- `137-150s` / `4110-4500f`: cierre académico.

## Visual And Audio Direction

- Look: oscuro técnico, metal, vidrio, acentos azul-verde, profundidad 2.5D y movimiento de cámara suave.
- Usar capturas reales de Flask si el entorno MySQL está disponible; si no, usar mockups copiados a `video/public/`.
- Usar Three.js solo dentro de Remotion y solo si aporta: nodos relacionales, líneas FK, piezas flotantes o red de datos.
- Voz en español Latam, frases cortas y defendibles.
- Música instrumental baja, SFX sutiles y subtítulos legibles.

## Test Plan

- Verificar que `git status --short` solo muestre cambios bajo `video/` para este trabajo.
- Render stills:
  - `npx remotion still ZarventPresentation --scale=0.25 --frame=0`
  - `--frame=300`, `1260`, `2700`, `3540`, `4499`
- Render final:
  - `npx remotion render ZarventPresentation out/zarvent-presentation.mp4`
- Validar duración con `ffprobe`: exactamente `150.000s` o 4500 frames a 30fps.
- Revisar que subtítulos, pantallas, ERD, audio y claims sean correctos y legibles.
- Confirmar que no se tocó nada fuera de `video/`.

## Assumptions

- `video/` está vacío y es el único lugar permitido para crear el subproyecto.
- La carpeta `presentation/` existente queda fuera de alcance.
- `spec/video/` queda fuera de alcance.
- El video puede copiar assets desde el proyecto principal hacia `video/public/`, pero no debe mover ni editar los originales.
- El video debe verse muy producido, pero sin exagerar funcionalidades que el prototipo Flask no demuestra.
