"""Generate TurboPrivate AI deployment demo GIF."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def get_font(size=14):
    for name in ["CascadiaCode.ttf", "JetBrainsMono-Regular.ttf", "consola.ttf", "cour.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            pass
    try:
        return ImageFont.truetype("C:/Windows/Fonts/consola.ttf", size)
    except (OSError, IOError):
        return ImageFont.load_default()


PROJECT_ROOT = Path(__file__).resolve().parent.parent

WIDTH, HEIGHT = 960, 640
BG = "#0f172a"
FG = "#e2e8f0"
GREEN = "#34d399"
YELLOW = "#fbbf24"
RED = "#f87171"
CYAN = "#818cf8"
DIM = "#475569"
PROMPT_C = "#6366f1"
BORDER = "#1e293b"
PROGRESS_BG = "#1e293b"
PROGRESS_FG = "#34d399"
SECTION = "#0ea5e9"

STATUS_SERVICES = [
    ("api", GREEN, "running"),
    ("inference", GREEN, "running"),
    ("safety-gate", GREEN, "running"),
    ("memory-rag", GREEN, "running"),
    ("worker", GREEN, "running"),
    ("prometheus", GREEN, "running"),
    ("postgres", GREEN, "running"),
    ("redis", GREEN, "running"),
]


def draw_terminal(draw, font, lines, title_bar=" TurboPrivate AI  —  Deployment Demo  —  v0.1.2", show_step=True, step_txt=""):
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=BG)
    draw.rectangle([0, 0, WIDTH, 36], fill=BORDER)
    draw.text((12, 9), title_bar, font=font, fill=CYAN)
    if show_step:
        draw.text((WIDTH - 140, 9), step_txt, font=font, fill=DIM)
    y = 52
    prompt_str = "$ "
    for line in lines:
        if isinstance(line, tuple):
            txt, color = line
            draw.text((16, y), txt, font=font, fill=color)
        elif line.startswith(prompt_str):
            cmd = line[len(prompt_str):]
            draw.text((16, y), prompt_str, font=font, fill=GREEN)
            draw.text((16 + font.getlength(prompt_str), y), cmd, font=font, fill=FG)
        elif line.startswith("[OK]") or line.startswith("✓") or line.startswith("●"):
            draw.text((16, y), line, font=font, fill=GREEN)
        elif line.startswith("[!!]") or line.startswith("⚠"):
            draw.text((16, y), line, font=font, fill=YELLOW)
        elif line.startswith("[XX]") or line.startswith("✗"):
            draw.text((16, y), line, font=font, fill=RED)
        elif line.startswith("===") or line.startswith("───"):
            draw.text((16, y), line, font=font, fill=DIM)
        elif line.strip().startswith("["):
            draw.text((16, y), line, font=font, fill=SECTION)
        else:
            draw.text((16, y), line, font=font, fill=FG)
        y += font.getbbox("Ag")[3] + 4
    return y


def draw_progress_bar(draw, font, x, y, w, h, pct, label=""):
    draw.rectangle([x, y, x + w, y + h], fill=PROGRESS_BG)
    fill_w = int(w * pct / 100)
    draw.rectangle([x, y, x + fill_w, y + h], fill=PROGRESS_FG)
    pct_text = f"{pct}%"
    if label:
        pct_text = f"{label}  {pct_text}"
    tw = font.getlength(pct_text)
    draw.text((x + w - tw - 8, y - 2), pct_text, font=font, fill=FG if pct < 100 else GREEN)


def build_frames(font):
    frames = []
    line_h = font.getbbox("Ag")[3] + 4

    # ─── SCENE 1: turbo doctor ──────────────────────────────
    doctor_output = [
        "═ TurboPrivate AI System Check ═",
        "",
        "[Platform]  win32, Python 3.12.10",
        "",
        "[RUNTIME]",
        "  PyTorch       [OK]  2.6.0",
        "  CUDA          [OK]  NVIDIA RTX 4090 (24 GB VRAM)",
        "  vLLM          [OK]  0.8.3",
        "  Transformers  [OK]  4.51.0",
        "  FastAPI       [OK]  0.136.0",
        "",
        "[SYSTEM]",
        "  Memory  [OK]  12.4 / 64.0 GB (19%)",
        "  CPU     [OK]  24 cores (8% used)",
        "  Disk    [OK]  412.7 GB free of 1.0 TB",
        "",
        "[TOOLS]",
        "  Docker  [OK]  27.5.1",
        "  kubectl [OK]  v1.32.0",
        "  Helm    [OK]  v3.17.0",
        "",
        "[NETWORK]",
        "  PyPI         [OK]  reachable",
        "  GitHub       [OK]  reachable",
        "  HuggingFace  [OK]  reachable",
        "",
        "[OK] System ready for deployment",
    ]
    reveal = [f"$ turbo doctor"]
    for i, line in enumerate(doctor_output):
        reveal.append(line)
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(img)
        draw_terminal(draw, font, reveal + [""] + [" " * 4 + "[>>>] checking..."], step_txt="Step 1/4")
        frames.append(img)

    # ─── SCENE 2: turbo deploy with progress bar ────────────
    deploy_cmd = "$ turbo deploy --provider bare-metal --gpu auto"
    deploy_lines = [
        deploy_cmd,
        "",
        "  ═══ Provisioning Cluster ═══",
        "  Target: bare-metal (gpu: auto)",
        "  Nodes:  4x NVIDIA RTX 4090",
        "",
    ]
    progress_stages = [
        (0, "Initializing..."),
        (8, "  SSH connecting to nodes..."),
        (18, "  SSH connected  [OK]"),
        (25, "  Installing K3s on master..."),
        (35, "  K3s master ready  [OK]"),
        (42, "  Joining worker nodes..."),
        (52, "  All nodes joined  [OK]"),
        (60, ""),
        (68, "  ═══ Deploying Services ═══"),
        (72, "  Installing Helm charts..."),
        (78, "  api:            deployed  [OK]"),
        (82, "  inference:      deployed  [OK]"),
        (86, "  safety-gate:    deployed  [OK]"),
        (90, "  memory-rag:     deployed  [OK]"),
        (94, "  worker:         deployed  [OK]"),
        (96, "  monitoring:     deployed  [OK]"),
        (100, ""),
    ]
    bar_x, bar_y, bar_w, bar_h = 60, 260, 840, 22
    for pct, log_line in progress_stages:
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(img)
        display = list(deploy_lines)
        if log_line:
            display.append(log_line)
        if pct > 0 and pct < 100:
            display.append("")
            display.append(f"  ─── {pct}% ───")
        elif pct == 100:
            display.append("")
            display.append((f"  ✓ Deployment complete!", GREEN))
            display.append((f"  API: http://10.0.0.1:8000", CYAN))
        draw_terminal(draw, font, display, step_txt="Step 2/4")
        draw_progress_bar(draw, font, bar_x, bar_y, bar_w, bar_h, pct, "Deploying" if pct < 100 else "Done")
        frames.append(img)

    # freeze at 100%
    for _ in range(8):
        frames.append(frames[-1])

    # ─── SCENE 3: turbo status with green services ──────────
    status_output = [
        "$ turbo status",
        "",
        "  ═══ Cluster: prod-cluster ═══",
        "  Provider: bare-metal  |  GPU: auto (4x RTX 4090)",
        "  Uptime:  3d 14h 22m  |  Nodes:  4/4 healthy",
        "",
        "  ─── Services ───",
    ]
    for srv, color, state in STATUS_SERVICES:
        status_output.append((f"    ●  {srv:15s}  {state:>10s}", color))
    status_output.append("")
    status_output.append(("    ●  All 8 services running  [OK]", GREEN))

    reveal = []
    for i in range(1, len(status_output) + 1):
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(img)
        chunk = status_output[:i]
        if i < len(status_output):
            chunk = chunk + [""] + [" " * 4 + "[>>>] fetching status..."]
        draw_terminal(draw, font, chunk, step_txt="Step 3/4")
        frames.append(img)

    for _ in range(8):
        frames.append(frames[-1])

    # ─── SCENE 4: final success summary ─────────────────────
    summary = [
        "$ turbo deploy --provider bare-metal --gpu auto",
        "",
        ("  ✓ TurboPrivate AI is LIVE!", GREEN),
        ("", None),
        ("  ═══ Deployment Summary ═══", SECTION),
        ("  Cluster:     prod-cluster", FG),
        ("  GPU:         4x NVIDIA RTX 4090", FG),
        ("  Services:    8/8 running", GREEN),
        ("  API:         http://10.0.0.1:8000", CYAN),
        ("  Dashboard:   http://10.0.0.1:5173", CYAN),
        ("  Docs:        http://10.0.0.1:8000/docs", CYAN),
        ("", None),
        ("  Run 'turbo doctor' to verify the deployment.", FG),
    ]
    reveal = []
    for i in range(1, len(summary) + 1):
        img = Image.new("RGB", (WIDTH, HEIGHT), BG)
        draw = ImageDraw.Draw(img)
        draw_terminal(draw, font, summary[:i], show_step=False)
        frames.append(img)

    for _ in range(15):
        frames.append(frames[-1])

    return frames


def main():
    font = get_font(14)
    frames = build_frames(font)
    out_path = PROJECT_ROOT / "demo" / "turboprivate-demo.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
    )
    print(f"GIF saved: {out_path} ({len(frames)} frames, {len(frames) * 80 / 1000:.1f}s)")
    print(f"Size: {out_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
