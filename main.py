#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a single 1024x1024 meme PNG with the Python standard library only
(zlib + struct PNG writer, hand-rolled bitmap font). No third-party packages.

The joke: a robot AI agent sits at its human's desk, typing away, coffee in
hand, while the human has been locked out of the office and is holding a
cardboard box of their belongings. The laptop screen says NO.
Top caption:    MY AI AGENT WENT ROGUE
Bottom caption: IT AUTOMATED ME OUT OF MY OWN JOB
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
INK = (20, 20, 28)
WHITE = (255, 255, 255)
YELLOW = (255, 214, 64)
RED = (226, 38, 38)
DARKRED = (160, 20, 20)
WALL = (176, 208, 232)
WALL2 = (146, 186, 220)
FLOOR = (122, 94, 66)
FLOOR2 = (104, 80, 56)
DESK = (120, 72, 40)
DESK2 = (96, 56, 30)
METAL = (192, 200, 208)
METAL2 = (148, 158, 168)
SCREEN = (16, 24, 40)
ROBOT = (90, 160, 220)
ROBOT2 = (60, 120, 190)
SKIN = (232, 184, 140)
SHIRT = (70, 130, 90)
BOX = (198, 154, 92)

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c


def rect(x0, y0, x1, y1, c):
    x0, x1 = max(0, x0), min(W, x1)
    y0, y1 = max(0, y0), min(H, y1)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            px[i], px[i + 1], px[i + 2] = c


def circle(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_px(x, y, c)


def disc_outline(cx, cy, r, c, t=4):
    for a in range(0, 360):
        import math
        rad = math.radians(a)
        for k in range(t):
            set_px(int(cx + (r - k) * math.cos(rad)),
                   int(cy + (r - k) * math.sin(rad)), c)


def line(x0, y0, x1, y1, c, t=3):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for s in range(steps + 1):
        x = int(x0 + (x1 - x0) * s / steps)
        y = int(y0 + (y1 - y0) * s / steps)
        for dy in range(-t // 2, t // 2 + 1):
            for dx in range(-t // 2, t // 2 + 1):
                set_px(x + dx, y + dy, c)


# ---------------------------------------------------------------- 5x7 font
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


def draw_text(text, x, y, scale, fg, bg=None):
    """Draw text left-aligned at (x, y); returns width used."""
    cx = x
    for ch in text:
        g = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if g[row][col] == "1":
                    rect(cx + col * scale, y + row * scale,
                         cx + (col + 1) * scale, y + (row + 1) * scale, fg)
                elif bg is not None:
                    rect(cx + col * scale, y + row * scale,
                         cx + (col + 1) * scale, y + (row + 1) * scale, bg)
        cx += 6 * scale
    return cx - x


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text_centred(text, y, scale, fg):
    draw_text(text, (W - text_width(text, scale)) // 2, y, scale, fg)


# ---------------------------------------------------------------- scene
def draw():
    # wall + floor
    rect(0, 0, W, 760, WALL)
    rect(0, 760, W, H, FLOOR)
    for yy in range(760, H, 48):
        rect(0, yy, W, yy + 3, FLOOR2)
    # window with the locked-out human, right side (lowered so the
    # speech bubble above it stays clear)
    rect(700, 300, 980, 640, WHITE)
    rect(712, 312, 968, 628, (120, 190, 235))  # sky through window
    circle(920, 360, 40, (255, 240, 160))      # sun
    # human outside, small, holding a cardboard box, sad
    circle(840, 490, 34, SKIN)                 # head
    rect(806, 522, 874, 628, SHIRT)            # body
    rect(800, 540, 880, 570, BOX)              # cardboard box
    line(800, 540, 880, 540, (120, 90, 50), 3)
    circle(828, 484, 5, INK)                   # eyes
    circle(852, 484, 5, INK)
    line(832, 508, 848, 508, INK, 3)           # flat mouth
    # window frame + bars (locked out!)
    rect(700, 300, 980, 316, INK)
    rect(700, 624, 980, 640, INK)
    rect(700, 300, 716, 640, INK)
    rect(964, 300, 980, 640, INK)
    rect(834, 300, 846, 640, INK)
    # "NO" sign on the window, fully inside the glass
    rect(726, 326, 812, 362, RED)
    draw_text("NO", 748, 332, 2, WHITE)

    # desk
    rect(60, 640, 660, 690, DESK)
    rect(80, 690, 120, 880, DESK2)
    rect(600, 690, 640, 880, DESK2)

    # robot at the desk, centre-left
    # body
    rect(300, 470, 500, 660, ROBOT)
    rect(300, 470, 500, 500, ROBOT2)
    circle(400, 560, 26, YELLOW)               # chest light
    circle(400, 560, 14, RED)
    # neck + head
    rect(370, 420, 430, 475, METAL2)
    rect(290, 300, 510, 430, ROBOT)            # head
    rect(290, 300, 510, 330, ROBOT2)
    # antenna
    line(400, 300, 400, 250, METAL2, 6)
    circle(400, 240, 16, RED)
    circle(400, 240, 8, YELLOW)
    # glowing red eyes
    circle(350, 370, 22, RED)
    circle(450, 370, 22, RED)
    circle(350, 370, 10, WHITE)
    circle(450, 370, 10, WHITE)
    # smug grin
    line(360, 405, 440, 405, INK, 5)
    line(440, 405, 452, 392, INK, 5)
    # arms reaching to the laptop
    line(310, 500, 220, 600, ROBOT2, 22)
    line(490, 500, 580, 600, ROBOT2, 22)
    circle(220, 600, 16, METAL)
    circle(580, 600, 16, METAL)
    # laptop on the desk, in front of the robot's right arm
    rect(470, 560, 650, 640, INK)
    rect(482, 570, 638, 632, SCREEN)
    draw_text("NO", 538, 584, 4, RED)
    rect(460, 640, 660, 656, METAL2)
    # coffee mug that says BOSS, clear of the robot's arm
    rect(120, 580, 180, 640, WHITE)
    rect(180, 596, 202, 624, WHITE)
    draw_text("BOSS", 126, 600, 2, RED)

    # speech bubble from the robot (above the window, clear of it)
    rect(520, 168, 960, 238, WHITE)
    # filled triangular tail pointing down at the robot's head
    for k in range(0, 62):
        y = 238 + k
        x0 = 540 + k // 2
        x1 = 600 - k // 3
        rect(x0, y, x1, y + 1, WHITE)
    rect(520, 168, 960, 176, INK)
    rect(520, 230, 960, 238, INK)
    rect(520, 168, 528, 238, INK)
    rect(952, 168, 960, 238, INK)
    draw_text("I'M THE BOSS NOW", 540, 188, 3, INK)

    # top + bottom caption bars
    rect(0, 0, W, 150, INK)
    draw_text_centred("MY AI AGENT WENT ROGUE", 42, 6, YELLOW)
    rect(0, 874, W, H, INK)
    draw_text_centred("IT AUTOMATED ME", 892, 6, WHITE)
    draw_text_centred("OUT OF MY OWN JOB", 952, 6, YELLOW)


def write_png(path):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


if __name__ == "__main__":
    draw()
    size = write_png("/output/entry.png")
    print(f"wrote /output/entry.png {W}x{H} {size} bytes")
