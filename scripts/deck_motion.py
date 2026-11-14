"""Motion motifs for Morph decks, learned from a frame-by-frame study of three template promo videos
(research PR: docs/PPTX-MORPH-TEMPLATE-STUDY.md on that branch).

The motifs are generic mechanisms, not copies of anyone's design: every function takes a *state* (a number or index) and
returns / draws the same named objects in a different pose, so two slides drawn with different states are tweened by
Morph. Geometry functions are pure (stdlib only) so tests can check them; draw helpers need pptx_world's Ctx.

  ripple_radii / draw_ripple        concentric rings growing out of a centre mark         (M1)
  ring_layout / column_layout       satellites on a ring  ->  the same satellites in a rail   (M11, M12)
  draw_menu                         ring-or-rail navigation: pass the layout and the active index
  wheel_layout / draw_wheel         list items on an arc: tilt, shrink and fade away from the active one (M8)
  roll_layout / draw_roll           numerals / titles that roll through the frame with rotation (M7)
  shuffle_layout / draw_cards       a card grid that re-deals with rotation and overlap (M6)

Status: SPIKE. Layout maths is unit-tested; how PowerPoint tweens rotation and font size is NOT verified (no PowerPoint here).
"""
import math

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

import deck_kit as K
from deck_kit import T


# ------------------------------------------------------------------------------------------------ pure geometry
def mix_hex(a, b, t):
    """Blend colour a towards b (t=0 -> a, t=1 -> b); 6-digit hex strings."""
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(x + (y - x) * max(0.0, min(1.0, t))):02X}" for x, y in zip(ca, cb))


def ripple_radii(n, t, r_max):
    """n rings; at progress t (0..1) ring i has radius r_max * t * (i + 1) / n, so they fan out evenly."""
    return [r_max * t * (i + 1) / n for i in range(n)]


def ring_layout(n, cx, cy, r, start_deg=-90.0):
    """n points on a circle, the first at start_deg (-90 = twelve o'clock), clockwise."""
    return [(cx + r * math.cos(math.radians(start_deg + 360.0 * i / n)),
             cy + r * math.sin(math.radians(start_deg + 360.0 * i / n))) for i in range(n)]


def column_layout(n, x, y0, pitch):
    return [(x, y0 + i * pitch) for i in range(n)]


def wheel_layout(n, active, cx, cy, radius, step_deg=14.0, max_pt=34.0, min_pt=20.0, rot_sign=1.0, fade_over=3.0):
    """Items on the left half of an arc centred at (cx, cy). Item i sits `i - active` steps from the active one:
    the active item is at (cx - radius, cy), the others move round the arc, tilt by their angle, shrink and fade.
    Returns dicts with the item centre (x, y), rotation in degrees, font size and fade 0..1 (0 = fully visible)."""
    out = []
    for i in range(n):
        off = i - active
        th = math.radians(off * step_deg)
        f = min(1.0, abs(off) / fade_over)
        out.append({"x": cx - radius * math.cos(th), "y": cy + radius * math.sin(th), "rot": rot_sign * off * step_deg,
                    "pt": max_pt + (min_pt - max_pt) * f, "fade": f ** 1.5, "active": off == 0})
    return out


def roll_layout(n, active, x, y, dy, rot_step=-20.0):
    """Items that roll through one spot: the active item rests at (x, y); item i is `i - active` steps away,
    shifted by dy per step and turned by rot_step degrees per step."""
    return [{"x": x, "y": y + (i - active) * dy, "rot": (i - active) * rot_step, "active": i == active} for i in range(n)]


def shuffle_layout(cols, rows, x, y, w, h, gap, state):
    """A cols x rows card grid. state 0 = tidy grid; state 1 = re-dealt (each card turned and nudged towards the centre,
    so neighbours overlap); state 2 = tidy again (use a different content set). Returns (x, y, w, h, rot) per card."""
    cards = []
    cx, cy = x + (cols * w + (cols - 1) * gap) / 2, y + (rows * h + (rows - 1) * gap) / 2
    for r in range(rows):
        for c in range(cols):
            px, py = x + c * (w + gap), y + r * (h + gap)
            if state == 1:
                sign = 1 if (r + c) % 2 == 0 else -1
                px += (cx - (px + w / 2)) * 0.22
                py += (cy - (py + h / 2)) * 0.22
                cards.append((px, py, w, h, 7.0 * sign))
            else:
                cards.append((px, py, w, h, 0.0))
    return cards


# ------------------------------------------------------------------------------------------------ draw helpers
def draw_ripple(c, name, cx, cy, radii, fill, base_alpha=0.22, line=None):
    """Concentric rings as ovals (largest first so the smaller ones sit on top). Names `{name}{i}` are stable."""
    for i in reversed(range(len(radii))):
        c.oval(f"{name}{i}", cx, cy, max(0.05, radii[i]), fill, alpha=base_alpha, line=line)


def draw_menu(c, name, labels, points, active=None, r_idle=0.42, r_active=0.55, color=K.COPPER, idle_fill="E3DFD2",
              label_dx=0.75, pt=24):
    """Round markers with a letter inside and a text label beside them; `points` decides ring or rail."""
    for i, (label, (x, y)) in enumerate(zip(labels, points)):
        on = active == i
        c.oval(f"{name}{i}", x, y, r_active if on else r_idle, color if on else idle_fill)
        T(c, f"{name}k{i}", chr(65 + i), x - 0.4, y - 0.26, 0.8, 0.5, pt, K.WHITE if on else K.MUTED, bold=True,
          align=PP_ALIGN.CENTER)
        T(c, f"{name}n{i}", label, x + label_dx, y - 0.26, 3.2, 0.5, pt, K.INK if on or active is None else K.MUTED, bold=on)


def draw_wheel(c, name, labels, layout, color, bg="FBFAF6", w=3.6, h=0.5):
    for i, (label, it) in enumerate(zip(labels, layout)):
        col = mix_hex(color if it["active"] else K.SUB, bg, it["fade"])
        T(c, f"{name}{i}", ("▸ " if it["active"] else "") + label, it["x"] - w / 2, it["y"] - h / 2, w, h, it["pt"], col,
          bold=it["active"], rot=it["rot"], track=it["fade"] < 1.0)  # fully faded items are not "read" text


def draw_roll(c, name, labels, layout, pt, color, w=4.0, h=1.2, align=PP_ALIGN.LEFT):
    for i, (label, it) in enumerate(zip(labels, layout)):
        T(c, f"{name}{i}", label, it["x"], it["y"], w, h, pt, color, bold=True, rot=it["rot"], align=align,
          track=it["active"])  # only the resting item counts as read text; the others wait off-screen


def draw_cards(c, name, texts, cards, fill=K.WHITE, line=K.LINE, pt=24):
    for i, (text, (x, y, w, h, rot)) in enumerate(zip(texts, cards)):
        c.rect(f"{name}{i}", x, y, w, h, fill, line=(line, 1.0), kind=MSO_SHAPE.ROUNDED_RECTANGLE, round_=0.08, rot=rot)
        T(c, f"{name}t{i}", text, x + 0.2, y + h / 2 - 0.3, w - 0.4, 0.6, pt, K.INK, bold=True, align=PP_ALIGN.CENTER, rot=rot)
