import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import streamlit as st
import streamlit.components.v1 as components
import tempfile, os, base64, io

st.set_page_config(page_title="Comparación del vector derivada", layout="wide")

st.title("Comparación del vector derivada")
st.markdown(
    "**Izquierda:** la curva es cerrada y el vector tangente nunca es nulo. "
    "**Derecha:** existe un punto donde el vector derivada es exactamente cero."
)

N        = 301
t_circle = np.linspace(0, 2 * np.pi, N)
t_cusp   = np.linspace(-1.2, 1.2, N)
theta    = np.linspace(0, 2 * np.pi, 600)
circle_x = np.cos(theta);  circle_y = np.sin(theta)
s        = np.linspace(-1.2, 1.2, 600)
cusp_x   = s ** 3;          cusp_y   = s ** 2

def build_ani():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    fig.subplots_adjust(bottom=0.28, top=0.82, wspace=0.25)
    fig.suptitle("Comparación del vector derivada", fontsize=16, y=0.96)

    ax1.plot(circle_x, circle_y, linewidth=2.5)
    point1,        = ax1.plot([], [], "o", markersize=9)
    tangent_line1, = ax1.plot([], [], "--", linewidth=2)
    vector1 = ax1.quiver([], [], [], [], angles="xy", scale_units="xy", scale=1, width=0.008)
    ax1.set_title(r"Contraejemplo: $f(t)=(\cos t,\sin t)$", fontsize=13)
    ax1.set_xlim(-1.7, 1.7); ax1.set_ylim(-1.7, 1.7); ax1.set_aspect("equal")
    ax1.grid(True, alpha=0.4); ax1.axhline(0, linewidth=0.8); ax1.axvline(0, linewidth=0.8)
    info1 = ax1.text(0.5, -0.18, "", transform=ax1.transAxes, fontsize=11,
                     ha="center", va="top", bbox=dict(boxstyle="round", alpha=0.85))

    ax2.plot(cusp_x, cusp_y, linewidth=2.5)
    point2,        = ax2.plot([], [], "o", markersize=9)
    tangent_line2, = ax2.plot([], [], "--", linewidth=2)
    vector2 = ax2.quiver([], [], [], [], angles="xy", scale_units="xy", scale=1, width=0.008)
    ax2.set_title(r"Ejemplo: $g(t)=(t^3,t^2)$", fontsize=13)
    ax2.set_xlim(-2.0, 2.0); ax2.set_ylim(-0.3, 1.8); ax2.set_aspect("equal")
    ax2.grid(True, alpha=0.4); ax2.axhline(0, linewidth=0.8); ax2.axvline(0, linewidth=0.8)
    info2 = ax2.text(0.5, -0.18, "", transform=ax2.transAxes, fontsize=11,
                     ha="center", va="top", bbox=dict(boxstyle="round", alpha=0.85))

    fig.text(0.5, 0.04,
             "Izquierda: la curva es cerrada y el vector tangente nunca es nulo. "
             "Derecha: existe un punto donde el vector derivada es exactamente cero.",
             ha="center", fontsize=11)

    def update(i):
        t  = t_circle[i]; x = np.cos(t); y = np.sin(t)
        dx = -np.sin(t);  dy = np.cos(t)
        point1.set_data([x], [y])
        vector1.set_offsets([[x, y]]); vector1.set_UVC([0.45*dx], [0.45*dy])
        r = np.linspace(-0.7, 0.7, 100)
        tangent_line1.set_data(x + r*dx, y + r*dy)
        info1.set_text(r"$f'(t)=(-\sin t,\cos t)$" + "\n" +
                       r"$\|f'(t)\|=1$" + "\n" + r"$f'(t)\neq(0,0)$")
        u  = t_cusp[i]; X = u**3; Y = u**2
        dX = 3*u**2;    dY = 2*u
        norm = np.sqrt(dX**2 + dY**2)
        point2.set_data([X], [Y])
        if abs(u) < 1e-10:
            vector2.set_offsets([[X, Y]]); vector2.set_UVC([0], [0])
            tangent_line2.set_data([], [])
            info2.set_text(r"$g'(0)=(0,0)$" + "\n" + r"$\|g'(0)\|=0$")
        else:
            vector2.set_offsets([[X, Y]]); vector2.set_UVC([0.35*dX], [0.35*dY])
            r2 = np.linspace(-0.5, 0.5, 100)
            ux = dX/norm; uy = dY/norm
            tangent_line2.set_data(X + r2*ux, Y + r2*uy)
            info2.set_text(rf"$g'(t)=(3t^2,2t)$" + "\n" + rf"$\|g'(t)\|={norm:.2f}$")
        return point1, tangent_line1, vector1, point2, tangent_line2, vector2, info1, info2

    ani = FuncAnimation(fig, update, frames=N, interval=40, blit=False)
    return fig, ani

@st.cache_resource(show_spinner=False)
def generar_frames_b64():
    fig, ani = build_ani()
    frames_b64 = []
    for i in range(N):
        ani._draw_next_frame(i, blit=False)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=90, bbox_inches="tight")
        buf.seek(0)
        frames_b64.append(base64.b64encode(buf.read()).decode("utf-8"))
        buf.close()
    plt.close(fig)
    return frames_b64

@st.cache_resource(show_spinner=False)
def generar_gif():
    fig, ani = build_ani()
    tmp = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    ani.save(tmp.name, writer=PillowWriter(fps=25))
    plt.close(fig)
    with open(tmp.name, "rb") as f:
        data = f.read()
    os.unlink(tmp.name)
    return data

# ============================================================
# SECCIÓN 1 — REPRODUCTOR CUSTOM
# ============================================================

st.subheader("▶ Animación interactiva con controles")
st.caption("Usa la barra de progreso para ir a cualquier punto, o los botones para saltar frames.")

with st.spinner("Generando frames… (solo la primera vez, puede tardar ~30 s)"):
    frames = generar_frames_b64()

frames_json = "[" + ",".join(f'"{f}"' for f in frames) + "]"

player_html = f"""
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #fff; font-family: sans-serif; }}
  #wrap {{ text-align: center; padding: 10px 14px 14px; }}
  #anim {{
    max-width: 100%;
    border: 1px solid #ddd;
    border-radius: 6px;
    display: block;
    margin: 0 auto;
  }}

  /* scrubber */
  #scrubRow {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 10px auto 6px;
    max-width: 98%;
  }}
  #scrubber {{
    flex: 1;
    height: 5px;
    accent-color: #1976d2;
    cursor: pointer;
  }}
  #timeLabel {{
    font-size: 12px;
    color: #555;
    white-space: nowrap;
    min-width: 90px;
    text-align: right;
  }}

  /* botones */
  .ctrl {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    flex-wrap: wrap;
    margin-top: 6px;
  }}
  button {{
    padding: 6px 11px;
    font-size: 14px;
    cursor: pointer;
    border: 1px solid #bbb;
    border-radius: 5px;
    background: #f0f0f0;
    transition: background .15s;
  }}
  button:hover {{ background: #ddd; }}
  #btnPlay {{
    min-width: 120px;
    font-weight: 700;
    background: #1976d2;
    color: #fff;
    border-color: #1565c0;
  }}
  #btnPlay:hover {{ background: #1565c0; }}

  /* velocidad */
  .speed-wrap {{
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 13px;
    margin-left: 4px;
  }}
  #speed {{ width: 100px; accent-color: #1976d2; cursor: pointer; }}
  #speedLabel {{ min-width: 38px; }}
</style>

<div id="wrap">
  <img id="anim" src="" alt="frame de la animación"/>

  <!-- barra de progreso -->
  <div id="scrubRow">
    <input type="range" id="scrubber" min="0" max="{N-1}" value="0" step="1"
           title="Arrastra para ir a cualquier frame">
    <span id="timeLabel">Frame 0 / {N-1}</span>
  </div>

  <!-- controles -->
  <div class="ctrl">
    <button id="btnFirst"  title="Ir al primer frame">⏮</button>
    <button id="btnBack10" title="Retroceder 10 frames">⏪ 10</button>
    <button id="btnPrev"   title="Retroceder 1 frame">◀ 1</button>
    <button id="btnPlay">⏸ Pausar</button>
    <button id="btnNext"   title="Avanzar 1 frame">1 ▶</button>
    <button id="btnFwd10"  title="Avanzar 10 frames">10 ⏩</button>
    <button id="btnLast"   title="Ir al último frame">⏭</button>
    <div class="speed-wrap">
      <span>Velocidad:</span>
      <input type="range" id="speed" min="0.25" max="4" step="0.25" value="1"
             title="Ajusta la velocidad de reproducción">
      <span id="speedLabel">1.00×</span>
    </div>
  </div>
</div>

<script>
  const frames  = {frames_json};
  const N       = {N};
  const BASE_MS = 40;

  let idx       = 0;
  let playing   = true;
  let speed     = 1.0;
  let timer     = null;
  let scrubbing = false;

  const img       = document.getElementById('anim');
  const scrubber  = document.getElementById('scrubber');
  const timeLabel = document.getElementById('timeLabel');
  const btnPlay   = document.getElementById('btnPlay');
  const btnPrev   = document.getElementById('btnPrev');
  const btnNext   = document.getElementById('btnNext');
  const btnBack10 = document.getElementById('btnBack10');
  const btnFwd10  = document.getElementById('btnFwd10');
  const btnFirst  = document.getElementById('btnFirst');
  const btnLast   = document.getElementById('btnLast');
  const speedSldr = document.getElementById('speed');
  const speedLbl  = document.getElementById('speedLabel');

  function clamp(v, lo, hi) {{ return Math.max(lo, Math.min(hi, v)); }}

  function showFrame(i) {{
    idx = ((i % N) + N) % N;          // wrap en ambas direcciones
    img.src = 'data:image/png;base64,' + frames[idx];
    scrubber.value = idx;
    timeLabel.textContent = 'Frame ' + idx + ' / ' + (N - 1);
  }}

  function step() {{ showFrame(idx + 1); }}

  function startTimer() {{
    if (timer) clearInterval(timer);
    timer = setInterval(step, BASE_MS / speed);
  }}
  function stopTimer() {{
    if (timer) {{ clearInterval(timer); timer = null; }}
  }}

  // Play / Pausa
  btnPlay.onclick = () => {{
    playing = !playing;
    btnPlay.textContent = playing ? '⏸ Pausar' : '▶ Reanudar';
    playing ? startTimer() : stopTimer();
  }};

  // Saltos de frame
  btnPrev.onclick   = () => showFrame(idx - 1);
  btnNext.onclick   = () => showFrame(idx + 1);
  btnBack10.onclick = () => showFrame(idx - 10);
  btnFwd10.onclick  = () => showFrame(idx + 10);
  btnFirst.onclick  = () => showFrame(0);
  btnLast.onclick   = () => showFrame(N - 1);

  // Scrubber — pausa mientras se arrastra, reanuda al soltar
  scrubber.addEventListener('mousedown',  () => {{ scrubbing = true;  if (playing) stopTimer(); }});
  scrubber.addEventListener('touchstart', () => {{ scrubbing = true;  if (playing) stopTimer(); }}, {{passive:true}});
  scrubber.addEventListener('input',      () => showFrame(parseInt(scrubber.value)));
  function endScrub() {{
    if (!scrubbing) return;
    scrubbing = false;
    if (playing) startTimer();
  }}
  scrubber.addEventListener('mouseup',  endScrub);
  scrubber.addEventListener('touchend', endScrub);

  // Velocidad
  speedSldr.oninput = () => {{
    speed = parseFloat(speedSldr.value);
    speedLbl.textContent = speed.toFixed(2) + '\u00d7';
    if (playing) startTimer();
  }};

  // Arrancar
  showFrame(0);
  startTimer();
</script>
"""

components.html(player_html, height=700, scrolling=False)

st.markdown("---")

# ============================================================
# SECCIÓN 2 — GIF en bucle
# ============================================================

st.subheader("🔁 GIF en bucle continuo")
st.caption("Se reproduce automáticamente en bucle.")

with st.spinner("Generando GIF (solo la primera vez)…"):
    gif_bytes = generar_gif()

st.image(gif_bytes, use_container_width=True)

st.markdown("---")
st.caption("Curvas paramétricas · Teorema del Valor Medio vectorial")
