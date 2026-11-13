"""The .22 LR shot (Blender 5.2, headless: its numpy and aud read and write Ogg Vorbis).

    blender -b --factory-startup -P scripts/make_22lr_sound.py

User, 2026-11-13: "yes synthesize it. just remember other .22 LR will use this sound too". One sound event for every
.22 LR gun of both mods, `GunsOfTien_22LRShoot` (the main mod, beside the round), several variations picked at random
by the game (`GameSound.getRandomClip`: one sound, several `clip` blocks). Synthesised, so the mod owns it; fixed seeds,
the same files every run.

Writes
    Contents/mods/GoMExtensionGunsOfTien/42/media/sounds/gunsoftien_22lr_shoot_<n>.ogg   VARIATIONS mono files
    Contents/mods/GoMExtensionGunsOfTien/42/media/scripts/GunsOfTien/sounds_22lr.txt     the sound event

What an unsuppressed .22 LR from a pistol-length barrel sounds like, against a 9 mm pistol: a far smaller powder
charge (about 2 grains against 6), so a sharp, light, dry crack with little low end: a fast broadband blast centred
around 1.5-4 kHz dying within a few milliseconds, only a hint of thump below 300 Hz, no supersonic crack worth the name
(high-velocity .22 leaves a 9" barrel about the speed of sound). A blowback .22's light bolt clacks back and forward
within about 30 ms, a small metallic tick, and the shot rolls off outdoors in a short, quiet, darker tail with a faint
slap-back.

Level: mastered as game gunshots are (a soft saturation fattens the crack and body), its peak at -1 dBFS and its
loudest 30 ms at LOUDEST_DB. Vanilla's 9 mm shots are FMOD events in its banks; its loose media/sound/9mmShot.ogg is a
flat, clipped 400 ms burst (its loudest 30 ms at -1 dB), no usable reference. So how loud the game plays it against
GoM's M9 (the clip's `volume` times the gun's SoundGain, GoM's pistols 1.5) is set by ear in game: a .22 LR pistol
should sound about 6 dB under a 9 mm one (scripts/sound_model.py: 71 / 20 against 111 / 32).
"""

import os

import aud
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.normpath(os.path.join(HERE, "..", "Contents/mods/GoMExtensionGunsOfTien/42/media"))
OUT = os.path.join(MEDIA, "sounds")
SCRIPT = os.path.join(MEDIA, "scripts/GunsOfTien/sounds_22lr.txt")
RATE = 48000
VARIATIONS = 4
LOUDEST_DB = -9.0                 # the loudest 30 ms (RMS, dBFS): peaks then land about -1 dBFS
CLIP_VOLUME = 1.0                 # the clip's `volume` in the sound script (set by ear in game)
EVENT = "GunsOfTien_22LRShoot"


def t_axis(seconds):
    return np.arange(int(RATE * seconds)) / RATE


def lowpass(x, cutoff):
    """One-pole low-pass, run twice (make_link_sounds.py's)."""
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
    """A two-pole resonator driven by x, ringing down with time constant `decay` (make_link_sounds.py's)."""
    r = np.exp(-1.0 / (decay * RATE))
    c = 2.0 * r * np.cos(2.0 * np.pi * freq / RATE)
    y = np.zeros_like(x)
    y1 = y2 = 0.0
    for i, v in enumerate(x):
        y0 = v + c * y1 - r * r * y2
        y[i] = y0
        y2, y1 = y1, y0
    return y * (1.0 - r)


def place(buf, sound, at, gain):
    i = int(at * RATE)
    n = min(len(sound), len(buf) - i)
    if n > 0:
        buf[i:i + n] += gain * sound[:n]


def norm(x):
    return x / (np.abs(x).max() + 1e-12)


def blast(rng):
    """The muzzle blast: a near-instant rise, a sharp negative swing (the pressure wave's N shape, very short for a
    .22), and broadband noise dying in a few milliseconds, its energy pushed up into the 1.5-4 kHz band by a few
    ringing modes (the crack), with a small low thump under it."""
    t = t_axis(0.12)
    env = np.minimum(t / 0.00015, 1.0) * np.exp(-t / rng.uniform(0.0025, 0.0035))
    noise = rng.standard_normal(len(t)) * env
    # the body: the gas leaving the muzzle, a little longer and darker than the crack
    body_env = np.minimum(t / 0.0004, 1.0) * np.exp(-t / rng.uniform(0.014, 0.020))
    gas = lowpass(highpass(rng.standard_normal(len(t)), 250.0), 3200.0) * body_env
    crack = np.zeros_like(t)
    for _ in range(4):
        crack += rng.uniform(0.5, 1.0) * resonate(noise, rng.uniform(1500.0, 4200.0), rng.uniform(0.0015, 0.004))
    crack = norm(crack)
    # the N-wave: up for ~0.25 ms, down for ~0.35 ms
    n_wave = np.zeros_like(t)
    a, b = int(RATE * 0.00025), int(RATE * 0.0006)
    n_wave[:a] = np.linspace(0.0, 1.0, a)
    n_wave[a:b] = np.linspace(1.0, -0.7, b - a)
    n_wave[b:b + a] = np.linspace(-0.7, 0.0, a)
    thump = norm(lowpass(rng.standard_normal(len(t)), 260.0) * np.exp(-t / rng.uniform(0.010, 0.014)))
    body = norm(highpass(noise, 600.0))
    return 0.9 * n_wave + 0.75 * crack + 0.5 * body + 0.45 * norm(gas) + 0.3 * thump


def clack(rng, bright):
    """The light blowback bolt hitting its stop or the breech: a short noise burst ringing a few steel modes."""
    t = t_axis(0.03)
    hit = rng.standard_normal(len(t)) * np.exp(-t / rng.uniform(0.0003, 0.0008))
    out = np.zeros_like(t)
    for _ in range(4):
        out += rng.uniform(0.4, 1.0) * resonate(hit, rng.uniform(2200.0, 6500.0) * bright, rng.uniform(0.002, 0.006))
    return norm(0.8 * norm(out) + 0.3 * highpass(hit, 2500.0))


def tail(rng, length):
    """The shot rolling off outdoors: dark diffuse noise swelling a little and dying, with a faint slap-back."""
    t = t_axis(length)
    swell = np.minimum(t / 0.02, 1.0) * np.exp(-t / rng.uniform(0.12, 0.18))
    return norm(lowpass(rng.standard_normal(len(t)), rng.uniform(900.0, 1400.0)) * swell)


def shot(seed):
    rng = np.random.default_rng(seed)
    buf = np.zeros(int(RATE * 0.7))
    b = blast(rng)
    place(buf, b, 0.0, 1.0)
    place(buf, clack(rng, 1.0), rng.uniform(0.007, 0.010), 0.12)        # the bolt back against its buffer
    place(buf, clack(rng, 1.15), rng.uniform(0.020, 0.028), 0.10)       # forward, chambering the next round
    place(buf, tail(rng, 0.65), 0.004, 0.12)
    slap = lowpass(b, 1800.0)
    place(buf, norm(slap), rng.uniform(0.09, 0.14), 0.08)                # a wall or treeline far off
    buf = np.tanh(3.0 * buf) / np.tanh(3.0)                             # soft saturation: a game gunshot's density
    fade = int(RATE * 0.05)
    buf[-fade:] *= np.linspace(1.0, 0.0, fade)
    return buf


def loudest(x, ms=30):
    w = int(RATE * ms / 1000)
    n = max(1, len(x) // w)
    x = np.pad(x, (0, n * w + w - len(x)))[:n * w].reshape(n, w)
    return np.sqrt((x ** 2).mean(axis=1)).max()


def main():
    os.makedirs(OUT, exist_ok=True)
    target = 10.0 ** (LOUDEST_DB / 20.0)
    files = []
    for v in range(VARIATIONS):
        buf = shot(2200 + v)
        buf *= target / loudest(buf)
        peak = np.abs(buf).max()
        if peak > 0.89:                                   # -1 dBFS at most: lower the whole shot instead
            buf *= 0.89 / peak
        name = "gunsoftien_22lr_shoot_%d.ogg" % (v + 1)
        path = os.path.join(OUT, name)
        snd = aud.Sound.buffer(buf.astype(np.float32).reshape(-1, 1), RATE)
        snd.write(path, rate=RATE, channels=aud.CHANNELS_MONO, container=aud.CONTAINER_OGG, codec=aud.CODEC_VORBIS,
                  bitrate=128000)
        files.append(name)
        print("wrote", name, "peak %.1f dB, loudest 30 ms %.1f dB"
              % (20 * np.log10(np.abs(buf).max()), 20 * np.log10(loudest(buf))))
    clips = "".join("""        clip
        {
            distanceMax = 1000,
            volume = %s,
            file = media/sounds/%s,
        }
""" % (CLIP_VOLUME, f) for f in files)
    text = """module Base
{
    /* The .22 LR shot for every .22 LR gun of both mods (scripts/make_22lr_sound.py; synthesised, one variation
       picked at random per shot). Vanilla's M9Shoot as the pattern: category Item, two at a time per emitter. */
    sound %s
    {
        category = Item,
        maxInstancesPerEmitter = 2,
%s    }
}
""" % (EVENT, clips)
    with open(SCRIPT, "w", newline="\n") as fh:
        fh.write(text)
    print("wrote", SCRIPT)


if __name__ == "__main__":
    main()
