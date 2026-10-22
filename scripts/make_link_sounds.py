"""Landing sounds of spent belt links (Blender 5.2, headless: its numpy and aud write Ogg Vorbis).

    blender -b --factory-startup -P scripts/make_link_sounds.py

Writes Contents/mods/GoMExtensionGunsOfTien/42/media/sounds/gunsoftien_link_<surface>_<n>.ogg, six variations for
each of Hot Brass's six surfaces (Concrete, Dirt, Grass, Puddles, Snow, Wood); gen_scripts.py belt_links() declares
them as sound events GunsOfTien_Link_<Surface>_<n> and shared/GunsOfTien/BeltLinks.lua adds a "Link" family to Hot
Brass's impact sounds. Synthesised, so the mod owns them; fixed seeds, the same files every run.

What a spent M27 / M13 link sounds like landing: a few grams of thin stamped spring steel, an open, irregular shape.
On a hard floor a short, dry, high "tick" (higher and far shorter than a brass case's ring: no tube to resonate,
partials from about 3 to 11 kHz dying within tens of milliseconds), one or two smaller bounces, often a brief scrape or
skitter as it tumbles, and a faint rattle where two links touch. Wood is the same, duller and shorter with a soft
knock under it; dirt and grass a small muffled tap with hardly any metal; snow a near-silent pat; a puddle a tiny plip.
"""

import os
import sys

import aud
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "Contents/mods/GoMExtensionGunsOfTien/42/media/sounds"))
RATE = 48000
# Loudness per surface (user, 2026-10-22: balanced against the casings for a satisfying sound): the impact (the
# loudest 10 ms) 3 dB under Hot Brass's own bullet casing on the same surface (its six files measured 2026-10-22:
# concrete -16.7, dirt -20.1, grass -23.3, puddles -17.0, snow -19.6, wood -17.4 dB), so the brass stays the main
# sound and the link adds a lighter, crisper tick to it; both play at Hot Brass's script volume 0.3.
UNDER_CASING_DB = 3.0
CASING_HIT_DB = {"Concrete": -16.7, "Dirt": -20.1, "Grass": -23.3, "Puddles": -17.0, "Snow": -19.6, "Wood": -17.4}
VARIATIONS = 6                                  # as Hot Brass's own families


def t_axis(seconds):
    return np.arange(int(RATE * seconds)) / RATE


def lowpass(x, cutoff):
    """One-pole low-pass, run twice."""
    a = np.exp(-2.0 * np.pi * cutoff / RATE)
    for _ in range(2):
        y = np.empty_like(x)
        acc = 0.0
        for i, v in enumerate(x):
            acc = (1.0 - a) * v + a * acc
            y[i] = acc
        x = y
    return x


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


def resonate(x, freq, decay):
    """A two-pole resonator (a ringing mode of the piece) driven by x, ringing down with time constant `decay`."""
    r = np.exp(-1.0 / (decay * RATE))
    c = 2.0 * r * np.cos(2.0 * np.pi * freq / RATE)
    y = np.zeros_like(x)
    y1 = y2 = 0.0
    for i, v in enumerate(x):
        y0 = v + c * y1 - r * r * y2
        y[i] = y0
        y2, y1 = y1, y0
    return y * (1.0 - r)


def tick(rng, length, f_lo, f_hi, decay_lo, decay_hi, partials=4):
    """A small, irregular steel piece hitting the floor: a short burst of noise (the impact) exciting a few of its
    ringing modes, each with its own pitch and damping, plus the raw click. Noise-driven modes keep it from sounding
    like a struck tone (pure sines stacked in a burst read as a chime)."""
    t = t_axis(length)
    hit = rng.standard_normal(len(t)) * np.exp(-t / rng.uniform(0.0004, 0.0012))
    out = np.zeros_like(t)
    for _ in range(partials):
        out += rng.uniform(0.3, 1.0) * resonate(hit, rng.uniform(f_lo, f_hi), rng.uniform(decay_lo, decay_hi))
    out /= np.abs(out).max() + 1e-9
    return 0.8 * out + 0.35 * highpass(hit, 3000.0)


def thud(rng, length, cutoff, decay):
    t = t_axis(length)
    return lowpass(rng.standard_normal(len(t)), cutoff) * np.exp(-t / decay) * 4.0


def place(buf, sound, at, gain):
    i = int(at * RATE)
    n = min(len(sound), len(buf) - i)
    if n > 0:
        buf[i:i + n] += gain * sound[:n]


def link_sound(surface, seed):
    rng = np.random.default_rng(seed)
    buf = np.zeros(int(RATE * 0.6))
    if surface in ("Concrete", "Wood"):
        hard = surface == "Concrete"
        f_lo, f_hi = (2600.0, 8500.0) if hard else (1600.0, 5000.0)
        d_lo, d_hi = (0.004, 0.016) if hard else (0.002, 0.007)
        at = 0.005
        gain = 1.0
        for bounce in range(rng.integers(2, 4)):                 # the landing and one or two smaller bounces
            place(buf, tick(rng, 0.12, f_lo, f_hi, d_lo, d_hi), at, gain)
            if not hard:
                place(buf, thud(rng, 0.05, 900.0, 0.012), at, 0.5 * gain)
            at += rng.uniform(0.045, 0.11) * (0.7 ** bounce)
            gain *= rng.uniform(0.3, 0.5)
        for _ in range(rng.integers(2, 6)):                      # skitter: tiny ticks as it tumbles to rest
            at += rng.uniform(0.008, 0.025)
            place(buf, tick(rng, 0.03, f_lo * 1.2, f_hi, 0.001, 0.004, 2), at, gain * rng.uniform(0.15, 0.35))
    elif surface in ("Dirt", "Grass"):
        place(buf, thud(rng, 0.06, 1400.0 if surface == "Dirt" else 900.0, 0.010), 0.004, 1.0)
        place(buf, tick(rng, 0.03, 1500.0, 4000.0, 0.002, 0.005, 3), 0.004, 0.25 if surface == "Dirt" else 0.12)
        if surface == "Grass":
            rustle = highpass(rng.standard_normal(int(RATE * 0.08)), 3000.0) * np.exp(-t_axis(0.08) / 0.02)
            place(buf, rustle, 0.002, 0.15)
    elif surface == "Snow":
        place(buf, thud(rng, 0.05, 600.0, 0.012), 0.004, 0.6)
    elif surface == "Puddles":
        t = t_axis(0.06)
        f = 900.0 + 1400.0 * t / 0.06 * rng.uniform(0.8, 1.2)
        plip = np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-t / 0.015)
        place(buf, plip, 0.006, 0.7)
        place(buf, highpass(thud(rng, 0.04, 6000.0, 0.006), 1500.0), 0.004, 0.5)
        place(buf, tick(rng, 0.04, 2500.0, 7000.0, 0.003, 0.008, 3), 0.004, 0.2)
    # trim the silence, fade the tail, set the impact's loudness
    end = len(buf)
    while end > 1 and abs(buf[end - 1]) < 1e-4:
        end -= 1
    buf = buf[:max(end, int(RATE * 0.05))]
    fade = min(len(buf), int(RATE * 0.01))
    buf[-fade:] *= np.linspace(1.0, 0.0, fade)
    w = RATE // 100
    n = max(1, len(buf) // w)
    hit = np.sqrt((np.pad(buf, (0, n * w + w - len(buf)))[:n * w].reshape(n, w) ** 2).mean(axis=1)).max()
    target = 10.0 ** ((CASING_HIT_DB[surface] - UNDER_CASING_DB) / 20.0)
    return buf * (target / (hit + 1e-12))


def main():
    os.makedirs(OUT, exist_ok=True)
    for s_i, surface in enumerate(("Concrete", "Dirt", "Grass", "Puddles", "Snow", "Wood")):
        for v in range(VARIATIONS):
            data = link_sound(surface, 1000 + s_i * 10 + v).astype(np.float32).reshape(-1, 1)
            path = os.path.join(OUT, "gunsoftien_link_%s_%02d.ogg" % (surface.lower(), v + 1))
            snd = aud.Sound.buffer(data, RATE)
            snd.write(path, rate=RATE, channels=aud.CHANNELS_MONO, container=aud.CONTAINER_OGG,
                      codec=aud.CODEC_VORBIS, bitrate=96000)
            print("wrote", os.path.relpath(path, os.path.join(HERE, "..")), "%.3f s" % (len(data) / RATE))


if __name__ == "__main__":
    main()
