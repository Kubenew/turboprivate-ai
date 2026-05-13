"""Generate TurboPrivate AI deployment demo GIF."""

import subprocess
import tempfile
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


def run_command(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10, cwd=PROJECT_ROOT)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {e}"


PROJECT_ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    ("turbo doctor", lambda: run_command("python -m turbo doctor")),
    ("turbo --help", lambda: run_command("python -m turbo --help")),
    ("turbo model --help", lambda: run_command("python -m turbo model --help")),
    ("turbo safety --help", lambda: run_command("python -m turbo safety --help")),
    ("turbo model pull meta-llama/Llama-3-8B", lambda: run_command("python -m turbo model pull meta-llama/Llama-3-8B")),
    ("turbo model quantize meta-llama/Llama-3-8B --bits 4", lambda: run_command("python -m turbo model quantize meta-llama/Llama-3-8B --bits 4")),
    ("turbo infra init --name my-cluster", lambda: run_command("python -m turbo infra init --name my-cluster")),
    ("turbo backup --name pre-deploy", lambda: run_command("python -m turbo backup --name pre-deploy")),
]


WIDTH, HEIGHT = 960, 640
BG = "#0f172a"
FG = "#e2e8f0"
GREEN = "#34d399"
YELLOW = "#fbbf24"
CYAN = "#818cf8"
DIM = "#475569"
PROMPT = "#6366f1"
BORDER = "#1e293b"

COLORS = {"bg": BG, "fg": FG, "green": GREEN, "yellow": YELLOW, "cyan": CYAN, "dim": DIM, "prompt": PROMPT}


def draw_frame(draw, font, lines, step_idx):
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=COLORS["bg"])
    draw.rectangle([0, 0, WIDTH, 36], fill=BORDER)
    title = " TurboPrivate AI  —  Deployment Demo  —  v0.1.2"
    draw.text((12, 9), title, font=font, fill=COLORS["cyan"])
    draw.text((WIDTH - 120, 9), f"Step {step_idx}/{len(STEPS)}", font=font, fill=COLORS["dim"])
    y = 52
    prompt_str = "$ "
    for line in lines:
        if line.startswith(prompt_str):
            cmd = line[len(prompt_str):]
            draw.text((16, y), prompt_str, font=font, fill=COLORS["green"])
            draw.text((16 + font.getlength(prompt_str), y), cmd, font=font, fill=COLORS["fg"])
        elif line.startswith("[OK]"):
            draw.text((16, y), line, font=font, fill=COLORS["green"])
        elif line.startswith("[!!]") or line.startswith("[XX]"):
            draw.text((16, y), line, font=font, fill=COLORS["yellow"])
        elif line.strip().startswith("=="):
            draw.text((16, y), line, font=font, fill=COLORS["dim"])
        elif line.strip().startswith("RUNTIME") or line.strip().startswith("SYSTEM") or line.strip().startswith("TOOLS") or line.strip().startswith("NETWORK"):
            draw.text((16, y), line, font=font, fill=COLORS["cyan"])
        else:
            draw.text((16, y), line, font=font, fill=COLORS["fg"])
        y += font.getbbox("Ag")[3] + 4


def main():
    font = get_font(14)
    frames = []

    for i, (cmd, runner) in enumerate(STEPS):
        output = runner()
        lines = output.split("\n")
        lines = [l for l in lines if l.strip()] or [f"(no output: {cmd})"]

        for reveal in range(1, len(lines) + 1):
            img = Image.new("RGB", (WIDTH, HEIGHT), BG)
            draw = ImageDraw.Draw(img)
            displayed = [f"$ {cmd}"] + lines[:reveal]
            if reveal < len(lines):
                displayed.append("")
                displayed.append(" " * 4 + f"[{'>' * 3}] running...")
            draw_frame(draw, font, displayed, i + 1)
            frames.append(img)

    for _ in range(10):
        frames.append(frames[-1])

    out_path = PROJECT_ROOT / "demo" / "turboprivate-demo.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
    )
    print(f"GIF saved: {out_path} ({len(frames)} frames)")
    print(f"Size: {out_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
