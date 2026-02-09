"""
Generate an ambient electronic music track for the Savoie IA stop motion video.
100% programmatically generated = royalty-free, libre de droit.
Uses only numpy + wave (standard library) - no external music libraries needed.
"""

import numpy as np
import wave
import struct

SAMPLE_RATE = 44100
DURATION = 20  # seconds
TOTAL_SAMPLES = SAMPLE_RATE * DURATION

def sine_wave(freq, duration, sr=SAMPLE_RATE, amplitude=0.3):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * freq * t)

def triangle_wave(freq, duration, sr=SAMPLE_RATE, amplitude=0.2):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return amplitude * (2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1)

def envelope(samples, attack=0.1, decay=0.1, sustain_level=0.7, release=0.3):
    """ADSR envelope."""
    n = len(samples)
    sr = SAMPLE_RATE
    env = np.ones(n)

    att_samples = int(attack * sr)
    dec_samples = int(decay * sr)
    rel_samples = int(release * sr)

    # Attack
    if att_samples > 0:
        env[:att_samples] = np.linspace(0, 1, att_samples)
    # Decay
    if dec_samples > 0:
        start = att_samples
        end = min(start + dec_samples, n)
        env[start:end] = np.linspace(1, sustain_level, end - start)
    # Sustain
    sus_start = att_samples + dec_samples
    sus_end = max(n - rel_samples, sus_start)
    env[sus_start:sus_end] = sustain_level
    # Release
    if rel_samples > 0 and sus_end < n:
        env[sus_end:] = np.linspace(sustain_level, 0, n - sus_end)

    return samples * env

def pad_sound(freq, duration, amplitude=0.15):
    """Create a lush pad sound with multiple detuned oscillators."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    sound = np.zeros(len(t))
    # Multiple slightly detuned sine waves for richness
    for detune in [-2, -1, 0, 1, 2]:
        f = freq * (1 + detune * 0.002)
        sound += amplitude * 0.3 * np.sin(2 * np.pi * f * t)
        sound += amplitude * 0.15 * np.sin(2 * np.pi * f * 2 * t)  # octave
    # Slow LFO for movement
    lfo = 1 + 0.1 * np.sin(2 * np.pi * 0.2 * t)
    sound *= lfo
    return envelope(sound, attack=0.8, decay=0.5, sustain_level=0.6, release=1.0)

def bass_note(freq, duration, amplitude=0.25):
    """Deep bass note."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    sound = amplitude * np.sin(2 * np.pi * freq * t)
    sound += amplitude * 0.4 * np.sin(2 * np.pi * freq * 0.5 * t)  # sub
    return envelope(sound, attack=0.05, decay=0.3, sustain_level=0.5, release=0.5)

def arp_note(freq, duration, amplitude=0.12):
    """Bright arpeggio note."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    sound = amplitude * np.sin(2 * np.pi * freq * t)
    sound += amplitude * 0.5 * np.sin(2 * np.pi * freq * 2 * t)
    sound += amplitude * 0.2 * np.sin(2 * np.pi * freq * 3 * t)
    return envelope(sound, attack=0.01, decay=0.15, sustain_level=0.3, release=0.2)

def noise_sweep(duration, amplitude=0.03):
    """Filtered noise sweep for texture."""
    n = int(SAMPLE_RATE * duration)
    noise = amplitude * np.random.randn(n)
    # Simple lowpass via moving average
    kernel_size = 100
    kernel = np.ones(kernel_size) / kernel_size
    filtered = np.convolve(noise, kernel, mode='same')
    return envelope(filtered, attack=2, decay=1, sustain_level=0.5, release=3)

# === BUILD THE TRACK ===
print("Generating ambient electronic track...")

output = np.zeros(TOTAL_SAMPLES)

# Key: D minor / D dorian for a modern, slightly mysterious feel
# D3=146.83, F3=174.61, A3=220, C4=261.63, D4=293.66, E4=329.63, F4=349.23, A4=440

# === PAD PROGRESSION (sustained chords throughout) ===
pad_chords = [
    # (start_sec, duration, [frequencies])
    (0, 5, [146.83, 220, 293.66]),       # Dm
    (4.5, 5, [174.61, 261.63, 349.23]),  # F
    (9, 5, [130.81, 196, 261.63]),        # C
    (13.5, 5, [146.83, 220, 293.66]),    # Dm
    (17, 4, [174.61, 220, 293.66]),       # Dm/F -> resolve
]

for start, dur, freqs in pad_chords:
    for freq in freqs:
        pad = pad_sound(freq, dur, 0.1)
        s = int(start * SAMPLE_RATE)
        e = s + len(pad)
        if e > TOTAL_SAMPLES:
            pad = pad[:TOTAL_SAMPLES - s]
            e = TOTAL_SAMPLES
        output[s:e] += pad

# === BASS LINE ===
bass_pattern = [
    # (start, dur, freq)
    (2, 1.5, 73.42),     # D2
    (4, 1.5, 87.31),     # F2
    (6, 1.5, 73.42),     # D2
    (8, 1.5, 65.41),     # C2
    (10, 1.5, 73.42),    # D2
    (12, 1.5, 87.31),    # F2
    (14, 1.5, 73.42),    # D2
    (16, 1.5, 65.41),    # C2
    (18, 2, 73.42),      # D2 (resolve)
]

for start, dur, freq in bass_pattern:
    bass = bass_note(freq, dur, 0.2)
    s = int(start * SAMPLE_RATE)
    e = s + len(bass)
    if e > TOTAL_SAMPLES:
        bass = bass[:TOTAL_SAMPLES - s]
        e = TOTAL_SAMPLES
    output[s:e] += bass

# === ARPEGGIO PATTERN (starts at scene 2, 4 sec) ===
arp_freqs = [293.66, 349.23, 440, 523.25, 440, 349.23]  # D4, F4, A4, C5, A4, F4
arp_start = 4.0
arp_note_dur = 0.25
arp_gap = 0.35

for i in range(30):
    t = arp_start + i * arp_gap
    if t + arp_note_dur > DURATION:
        break
    freq = arp_freqs[i % len(arp_freqs)]
    # Velocity variation for humanization
    amp = 0.08 + 0.04 * np.sin(i * 0.7)
    note = arp_note(freq, arp_note_dur, amp)
    s = int(t * SAMPLE_RATE)
    e = s + len(note)
    if e > TOTAL_SAMPLES:
        note = note[:TOTAL_SAMPLES - s]
        e = TOTAL_SAMPLES
    output[s:e] += note

# === TEXTURE: noise sweep ===
sweep = noise_sweep(DURATION, 0.02)
output[:len(sweep)] += sweep

# === BELL/CHIME HITS (scene transitions) ===
def bell(freq, duration=1.5, amplitude=0.08):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    sound = amplitude * np.sin(2 * np.pi * freq * t)
    sound += amplitude * 0.6 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t * 3)
    sound += amplitude * 0.3 * np.sin(2 * np.pi * freq * 3.0 * t) * np.exp(-t * 5)
    return sound * np.exp(-t * 1.5)

bell_hits = [
    (0.5, 587.33),   # D5 - intro
    (4.0, 783.99),   # G5 - scene 2
    (8.0, 659.26),   # E5 - scene 3
    (12.0, 587.33),  # D5 - scene 4
    (16.0, 783.99),  # G5 - finale
]

for t, freq in bell_hits:
    b = bell(freq)
    s = int(t * SAMPLE_RATE)
    e = s + len(b)
    if e > TOTAL_SAMPLES:
        b = b[:TOTAL_SAMPLES - s]
        e = TOTAL_SAMPLES
    output[s:e] += b

# === MASTER: normalize and fade out ===
# Fade in (1 sec) and fade out (2 sec)
fade_in = np.linspace(0, 1, SAMPLE_RATE * 1)
output[:len(fade_in)] *= fade_in

fade_out = np.linspace(1, 0, SAMPLE_RATE * 2)
output[-len(fade_out):] *= fade_out

# Normalize
peak = np.max(np.abs(output))
if peak > 0:
    output = output / peak * 0.85

# === WRITE WAV ===
output_16bit = np.int16(output * 32767)

with wave.open("music.wav", "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(output_16bit.tobytes())

print("Music generated: music.wav (20 seconds, ambient electronic)")
print("License: 100% original, generated programmatically - libre de droit / royalty-free")
