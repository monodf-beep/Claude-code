"""
Stop Motion Video Generator for Savoie IA
Generates animated frames featuring mountains, AI neural network visuals,
and branding for the Savoie IA collective.
"""

import math
import random
import os
from PIL import Image, ImageDraw, ImageFont

# === CONFIG ===
WIDTH, HEIGHT = 1920, 1080
FPS = 8  # stop motion feel
DURATION_SEC = 20
TOTAL_FRAMES = FPS * DURATION_SEC
OUT_DIR = "frames"

# Savoie IA color palette
BG_DARK = (27, 27, 27)        # #1b1b1b
TEXT_LIGHT = (197, 193, 185)   # #c5c1b9
ACCENT = (87, 94, 207)        # #575ECF
ACCENT_GLOW = (120, 126, 230)
WHITE = (255, 255, 255)
MOUNTAIN_DARK = (40, 42, 55)
MOUNTAIN_MID = (55, 58, 75)
MOUNTAIN_LIGHT = (70, 74, 95)
SNOW = (200, 205, 215)
STAR_COLOR = (180, 180, 200)

os.makedirs(OUT_DIR, exist_ok=True)

random.seed(42)

# Pre-generate stars
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2), random.random()) for _ in range(150)]

# Pre-generate neural network nodes
nn_nodes = []
for _ in range(25):
    nn_nodes.append({
        'x': random.randint(WIDTH // 4, 3 * WIDTH // 4),
        'y': random.randint(HEIGHT // 4, 3 * HEIGHT // 4),
        'vx': random.uniform(-2, 2),
        'vy': random.uniform(-1.5, 1.5),
        'size': random.randint(3, 8),
        'phase': random.uniform(0, math.pi * 2),
    })

# Snowflakes for mountain scene
snowflakes = []
for _ in range(60):
    snowflakes.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT),
        'speed': random.uniform(1, 4),
        'size': random.randint(2, 5),
        'drift': random.uniform(-1, 1),
    })


def draw_mountains(draw, offset=0):
    """Draw layered mountain silhouettes."""
    # Back mountains
    peaks_back = []
    x = -50
    while x < WIDTH + 100:
        y = 550 + math.sin(x * 0.003 + 1.5) * 120 + math.sin(x * 0.007) * 60
        peaks_back.append((x, y))
        x += 8
    peaks_back.append((WIDTH + 100, HEIGHT))
    peaks_back.insert(0, (-50, HEIGHT))
    draw.polygon(peaks_back, fill=MOUNTAIN_DARK)

    # Mid mountains
    peaks_mid = []
    x = -50
    while x < WIDTH + 100:
        y = 620 + math.sin(x * 0.004 + 0.8 + offset * 0.01) * 100 + math.sin(x * 0.009) * 45
        peaks_mid.append((x, y))
        x += 6
    peaks_mid.append((WIDTH + 100, HEIGHT))
    peaks_mid.insert(0, (-50, HEIGHT))
    draw.polygon(peaks_mid, fill=MOUNTAIN_MID)

    # Front mountains
    peaks_front = []
    x = -50
    while x < WIDTH + 100:
        y = 700 + math.sin(x * 0.005 + offset * 0.02) * 80 + math.sin(x * 0.012) * 35
        peaks_front.append((x, y))
        x += 5
    peaks_front.append((WIDTH + 100, HEIGHT))
    peaks_front.insert(0, (-50, HEIGHT))
    draw.polygon(peaks_front, fill=MOUNTAIN_LIGHT)

    # Snow caps on back mountains
    for i in range(0, len(peaks_back) - 2, 30):
        px, py = peaks_back[i]
        if py < 580:
            for dx in range(-15, 16, 3):
                dy = abs(dx) * 0.8
                draw.ellipse([px + dx - 2, py + dy - 2, px + dx + 2, py + dy + 2], fill=SNOW)


def draw_stars(draw, frame):
    """Draw twinkling stars."""
    for sx, sy, brightness in stars:
        twinkle = 0.5 + 0.5 * math.sin(frame * 0.3 + brightness * 10)
        alpha = int(180 * twinkle * brightness)
        r = int(STAR_COLOR[0] * twinkle)
        g = int(STAR_COLOR[1] * twinkle)
        b = int(STAR_COLOR[2] * twinkle)
        size = 1 + int(brightness * 2 * twinkle)
        draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=(r, g, b))


def draw_neural_network(draw, frame, alpha_factor=1.0):
    """Draw animated neural network nodes and connections."""
    positions = []
    for i, node in enumerate(nn_nodes):
        x = node['x'] + math.sin(frame * 0.15 + node['phase']) * 30
        y = node['y'] + math.cos(frame * 0.12 + node['phase'] * 1.3) * 20
        positions.append((x, y))

    # Draw connections
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            dist = math.hypot(positions[i][0] - positions[j][0],
                              positions[i][1] - positions[j][1])
            if dist < 300:
                intensity = int((1 - dist / 300) * 80 * alpha_factor)
                pulse = 0.5 + 0.5 * math.sin(frame * 0.2 + i * 0.5)
                color = (
                    int(ACCENT[0] * pulse * alpha_factor),
                    int(ACCENT[1] * pulse * alpha_factor),
                    int(ACCENT[2] * pulse * alpha_factor),
                )
                draw.line([positions[i], positions[j]], fill=color, width=1)

    # Draw nodes
    for i, (x, y) in enumerate(positions):
        pulse = 0.6 + 0.4 * math.sin(frame * 0.25 + nn_nodes[i]['phase'])
        size = nn_nodes[i]['size'] * pulse
        glow_color = (
            int(ACCENT_GLOW[0] * pulse * alpha_factor),
            int(ACCENT_GLOW[1] * pulse * alpha_factor),
            int(ACCENT_GLOW[2] * pulse * alpha_factor),
        )
        # Glow
        draw.ellipse([x - size * 2, y - size * 2, x + size * 2, y + size * 2], fill=(
            int(ACCENT[0] * 0.2 * alpha_factor),
            int(ACCENT[1] * 0.2 * alpha_factor),
            int(ACCENT[2] * 0.2 * alpha_factor),
        ))
        # Core
        draw.ellipse([x - size, y - size, x + size, y + size], fill=glow_color)


def draw_snowfall(draw, frame):
    """Draw falling snowflakes."""
    for sf in snowflakes:
        y = (sf['y'] + frame * sf['speed'] * 3) % HEIGHT
        x = sf['x'] + math.sin(frame * 0.1 + sf['drift'] * 5) * 10
        s = sf['size']
        brightness = 150 + int(50 * math.sin(frame * 0.2 + sf['drift']))
        draw.ellipse([x - s, y - s, x + s, y + s], fill=(brightness, brightness, brightness + 10))


def draw_text_with_shadow(draw, pos, text, font, fill, shadow_color=(0, 0, 0)):
    """Draw text with a shadow effect."""
    x, y = pos
    # Shadow
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
    draw.text(pos, text, font=font, fill=fill)


def get_font(size):
    """Try to load a good font, fall back to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


# === SCENE DEFINITIONS ===
# Scene 1 (0-4s): Title reveal with mountains
# Scene 2 (4-8s): Neural network animation + "Intelligence Artificielle"
# Scene 3 (8-12s): Mountains + snow + "Experts en Savoie"
# Scene 4 (12-16s): Combined scene + tagline
# Scene 5 (16-20s): Logo + call to action

font_title = get_font(90)
font_subtitle = get_font(50)
font_body = get_font(36)
font_small = get_font(28)
font_url = get_font(32)

print(f"Generating {TOTAL_FRAMES} frames...")

for f in range(TOTAL_FRAMES):
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)
    t = f / TOTAL_FRAMES  # 0..1 progress
    sec = f / FPS

    # === SCENE 1: Title Reveal (0-4s) ===
    if sec < 4:
        scene_t = sec / 4  # 0..1 within scene

        # Gradient sky
        for y in range(HEIGHT // 2):
            ratio = y / (HEIGHT // 2)
            r = int(BG_DARK[0] + (15 - BG_DARK[0]) * ratio * 0.3)
            g = int(BG_DARK[1] + (15 - BG_DARK[1]) * ratio * 0.3)
            b = int(BG_DARK[2] + (40 - BG_DARK[2]) * ratio * 0.5)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        draw_stars(draw, f)
        draw_mountains(draw, f)

        # Title fade-in with stop motion jitter
        if scene_t > 0.2:
            alpha = min(1.0, (scene_t - 0.2) / 0.4)
            jitter_x = random.randint(-3, 3) if scene_t < 0.6 else 0
            jitter_y = random.randint(-2, 2) if scene_t < 0.6 else 0

            title = "SAVOIE IA"
            bbox = draw.textbbox((0, 0), title, font=font_title)
            tw = bbox[2] - bbox[0]
            tx = (WIDTH - tw) // 2 + jitter_x
            ty = 200 + jitter_y

            title_color = (
                int(WHITE[0] * alpha),
                int(WHITE[1] * alpha),
                int(WHITE[2] * alpha),
            )
            draw_text_with_shadow(draw, (tx, ty), title, font_title, title_color)

            # Accent line under title
            if scene_t > 0.5:
                line_w = int((scene_t - 0.5) / 0.5 * 400)
                line_x = (WIDTH - line_w) // 2
                draw.rectangle([line_x, ty + 110, line_x + line_w, ty + 115], fill=ACCENT)

        # Subtitle
        if scene_t > 0.6:
            sub_alpha = min(1.0, (scene_t - 0.6) / 0.3)
            subtitle = "Le collectif des experts en IA"
            bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
            sw = bbox[2] - bbox[0]
            sub_color = (
                int(TEXT_LIGHT[0] * sub_alpha),
                int(TEXT_LIGHT[1] * sub_alpha),
                int(TEXT_LIGHT[2] * sub_alpha),
            )
            draw_text_with_shadow(draw, ((WIDTH - sw) // 2, 340), subtitle, font_subtitle, sub_color)

    # === SCENE 2: Neural Network (4-8s) ===
    elif sec < 8:
        scene_t = (sec - 4) / 4

        # Dark background with subtle gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(BG_DARK[0] * (1 - ratio * 0.3))
            g = int(BG_DARK[1] * (1 - ratio * 0.3))
            b = int(BG_DARK[2] + 20 * ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        nn_alpha = min(1.0, scene_t / 0.3)
        draw_neural_network(draw, f, nn_alpha)

        # Text
        if scene_t > 0.2:
            text_alpha = min(1.0, (scene_t - 0.2) / 0.3)
            text = "Intelligence Artificielle"
            bbox = draw.textbbox((0, 0), text, font=font_subtitle)
            tw = bbox[2] - bbox[0]
            color = (
                int(ACCENT_GLOW[0] * text_alpha),
                int(ACCENT_GLOW[1] * text_alpha),
                int(ACCENT_GLOW[2] * text_alpha),
            )
            draw_text_with_shadow(draw, ((WIDTH - tw) // 2, 100), text, font_subtitle, color)

        if scene_t > 0.5:
            text_alpha = min(1.0, (scene_t - 0.5) / 0.3)
            lines = [
                "Solutions innovantes",
                "Expertise locale",
                "Transformation digitale",
            ]
            for i, line in enumerate(lines):
                if scene_t > 0.5 + i * 0.12:
                    la = min(1.0, (scene_t - 0.5 - i * 0.12) / 0.2)
                    jx = random.randint(-2, 2) if la < 0.8 else 0
                    color = (
                        int(TEXT_LIGHT[0] * la),
                        int(TEXT_LIGHT[1] * la),
                        int(TEXT_LIGHT[2] * la),
                    )
                    # Bullet point
                    bx = WIDTH // 2 - 200 + jx
                    by = 850 + i * 55
                    draw.ellipse([bx, by + 10, bx + 12, by + 22], fill=ACCENT)
                    draw.text((bx + 25, by), line, font=font_body, fill=color)

    # === SCENE 3: Mountain + Snow (8-12s) ===
    elif sec < 12:
        scene_t = (sec - 8) / 4

        # Sky gradient (dawn)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(20 + 30 * (1 - ratio))
            g = int(20 + 15 * (1 - ratio))
            b = int(40 + 50 * (1 - ratio))
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        draw_stars(draw, f)
        draw_mountains(draw, f)
        draw_snowfall(draw, f)

        # Text overlay
        if scene_t > 0.15:
            ta = min(1.0, (scene_t - 0.15) / 0.3)
            text = "Au coeur des Alpes"
            bbox = draw.textbbox((0, 0), text, font=font_title)
            tw = bbox[2] - bbox[0]
            color = (int(255 * ta), int(255 * ta), int(255 * ta))
            jx = random.randint(-2, 2) if ta < 0.7 else 0
            draw_text_with_shadow(draw, ((WIDTH - tw) // 2 + jx, 180), text, font_title, color)

        if scene_t > 0.4:
            ta = min(1.0, (scene_t - 0.4) / 0.3)
            text = "Experts en Savoie"
            bbox = draw.textbbox((0, 0), text, font=font_subtitle)
            tw = bbox[2] - bbox[0]
            color = (
                int(ACCENT_GLOW[0] * ta),
                int(ACCENT_GLOW[1] * ta),
                int(ACCENT_GLOW[2] * ta),
            )
            draw_text_with_shadow(draw, ((WIDTH - tw) // 2, 300), text, font_subtitle, color)

    # === SCENE 4: Combined (12-16s) ===
    elif sec < 16:
        scene_t = (sec - 12) / 4

        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(BG_DARK[0] * (1 + 0.2 * math.sin(ratio * math.pi)))
            g = int(BG_DARK[1] * (1 + 0.1 * math.sin(ratio * math.pi)))
            b = int(min(255, BG_DARK[2] + 30 * math.sin(ratio * math.pi)))
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        draw_neural_network(draw, f, 0.5)
        draw_mountains(draw, f)
        draw_snowfall(draw, f)

        # Services list with stop motion entrance
        services = [
            "Conseil & Strategie IA",
            "Machine Learning",
            "Data Science",
            "Automatisation",
        ]

        if scene_t > 0.1:
            ta = min(1.0, (scene_t - 0.1) / 0.2)
            text = "Nos Expertises"
            bbox = draw.textbbox((0, 0), text, font=font_subtitle)
            tw = bbox[2] - bbox[0]
            color = (int(255 * ta), int(255 * ta), int(255 * ta))
            draw_text_with_shadow(draw, ((WIDTH - tw) // 2, 100), text, font_subtitle, color)
            # Accent line
            lw = int(tw * ta)
            lx = (WIDTH - lw) // 2
            draw.rectangle([lx, 170, lx + lw, 174], fill=ACCENT)

        for i, svc in enumerate(services):
            appear_t = 0.25 + i * 0.12
            if scene_t > appear_t:
                sa = min(1.0, (scene_t - appear_t) / 0.15)
                jx = random.randint(-4, 4) if sa < 0.6 else 0
                jy = random.randint(-3, 3) if sa < 0.6 else 0

                bx = WIDTH // 2 - 220 + jx
                by = 220 + i * 70 + jy

                # Card background
                draw.rounded_rectangle(
                    [bx - 20, by - 5, bx + 480, by + 50],
                    radius=10,
                    fill=(35, 37, 50, 180),
                    outline=ACCENT if i == 0 else None,
                    width=2,
                )
                draw.ellipse([bx, by + 12, bx + 16, by + 28], fill=ACCENT)
                color = (
                    int(TEXT_LIGHT[0] * sa),
                    int(TEXT_LIGHT[1] * sa),
                    int(TEXT_LIGHT[2] * sa),
                )
                draw.text((bx + 30, by + 5), svc, font=font_body, fill=color)

    # === SCENE 5: CTA / Finale (16-20s) ===
    else:
        scene_t = (sec - 16) / 4

        # Animated gradient background
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            wave = math.sin(ratio * math.pi * 2 + f * 0.1) * 0.1
            r = int(min(255, BG_DARK[0] + ACCENT[0] * (0.15 + wave) * ratio))
            g = int(min(255, BG_DARK[1] + ACCENT[1] * (0.15 + wave) * ratio))
            b = int(min(255, BG_DARK[2] + ACCENT[2] * (0.3 + wave) * ratio))
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        draw_stars(draw, f)
        draw_neural_network(draw, f, 0.3)

        # Big title
        ta = min(1.0, scene_t / 0.3)
        title = "SAVOIE IA"
        bbox = draw.textbbox((0, 0), title, font=font_title)
        tw = bbox[2] - bbox[0]
        jx = random.randint(-2, 2) if scene_t < 0.3 else 0
        color = (int(255 * ta), int(255 * ta), int(255 * ta))
        draw_text_with_shadow(draw, ((WIDTH - tw) // 2 + jx, 250), title, font_title, color)

        # Accent bar
        if scene_t > 0.2:
            bw = int(min(1.0, (scene_t - 0.2) / 0.2) * 500)
            bx = (WIDTH - bw) // 2
            draw.rectangle([bx, 365, bx + bw, 370], fill=ACCENT)

        # Subtitle
        if scene_t > 0.3:
            sa = min(1.0, (scene_t - 0.3) / 0.2)
            text = "Le collectif des experts en intelligence artificielle"
            bbox = draw.textbbox((0, 0), text, font=font_body)
            tw = bbox[2] - bbox[0]
            color = (
                int(TEXT_LIGHT[0] * sa),
                int(TEXT_LIGHT[1] * sa),
                int(TEXT_LIGHT[2] * sa),
            )
            draw_text_with_shadow(draw, ((WIDTH - tw) // 2, 400), text, font_body, color)

        if scene_t > 0.4:
            sa = min(1.0, (scene_t - 0.4) / 0.2)
            text = "de Savoie"
            bbox = draw.textbbox((0, 0), text, font=font_body)
            tw = bbox[2] - bbox[0]
            color = (
                int(ACCENT_GLOW[0] * sa),
                int(ACCENT_GLOW[1] * sa),
                int(ACCENT_GLOW[2] * sa),
            )
            draw_text_with_shadow(draw, ((WIDTH - tw) // 2, 450), text, font_body, color)

        # CTA Button
        if scene_t > 0.55:
            ba = min(1.0, (scene_t - 0.55) / 0.2)
            pulse = 0.9 + 0.1 * math.sin(f * 0.4)
            btn_w, btn_h = 500, 70
            btn_x = (WIDTH - btn_w) // 2
            btn_y = 550
            btn_color = (
                int(ACCENT[0] * pulse * ba),
                int(ACCENT[1] * pulse * ba),
                int(ACCENT[2] * pulse * ba),
            )
            draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=35, fill=btn_color)
            cta = "Rejoignez le collectif"
            bbox = draw.textbbox((0, 0), cta, font=font_body)
            ctw = bbox[2] - bbox[0]
            cth = bbox[3] - bbox[1]
            draw.text((btn_x + (btn_w - ctw) // 2, btn_y + (btn_h - cth) // 2 - 3), cta, font=font_body,
                       fill=(int(255 * ba), int(255 * ba), int(255 * ba)))

        # URL
        if scene_t > 0.7:
            ua = min(1.0, (scene_t - 0.7) / 0.2)
            url = "savoie-ia-landing-page.lovable.app"
            bbox = draw.textbbox((0, 0), url, font=font_url)
            uw = bbox[2] - bbox[0]
            color = (
                int(TEXT_LIGHT[0] * ua * 0.7),
                int(TEXT_LIGHT[1] * ua * 0.7),
                int(TEXT_LIGHT[2] * ua * 0.7),
            )
            draw.text(((WIDTH - uw) // 2, 660), url, font=font_url, fill=color)

    # Save frame
    frame_path = os.path.join(OUT_DIR, f"frame_{f:04d}.png")
    img.save(frame_path)

    if f % 20 == 0:
        print(f"  Frame {f}/{TOTAL_FRAMES}")

print(f"Done! {TOTAL_FRAMES} frames generated in {OUT_DIR}/")
