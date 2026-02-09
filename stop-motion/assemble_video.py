"""
Assemble stop motion frames + music into final video.
Uses imageio with ffmpeg backend.
"""

import imageio.v3 as iio
import numpy as np
import wave
import os
import subprocess

FRAMES_DIR = "frames"
MUSIC_FILE = "music.wav"
OUTPUT_VIDEO = "savoie_ia_stopmotion_silent.mp4"
OUTPUT_FINAL = "savoie_ia_stopmotion.mp4"
FPS = 8

# Get ffmpeg path from imageio-ffmpeg
import imageio_ffmpeg
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Using ffmpeg: {ffmpeg_path}")

# Get sorted frame files
frame_files = sorted([
    os.path.join(FRAMES_DIR, f)
    for f in os.listdir(FRAMES_DIR)
    if f.endswith('.png')
])
print(f"Found {len(frame_files)} frames")

# Create silent video from frames
print("Creating video from frames...")
with iio.imopen(OUTPUT_VIDEO, "w", plugin="pyav") as out:
    out.init_video_stream("h264", fps=FPS)
    for i, fpath in enumerate(frame_files):
        frame = iio.imread(fpath)
        out.write_frame(frame)
        if i % 20 == 0:
            print(f"  Encoding frame {i}/{len(frame_files)}")

print(f"Silent video created: {OUTPUT_VIDEO}")

# Combine video + audio using ffmpeg
print("Merging audio and video...")
cmd = [
    ffmpeg_path,
    "-y",
    "-i", OUTPUT_VIDEO,
    "-i", MUSIC_FILE,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    OUTPUT_FINAL,
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    size_mb = os.path.getsize(OUTPUT_FINAL) / (1024 * 1024)
    print(f"\nFinal video created: {OUTPUT_FINAL} ({size_mb:.1f} MB)")
    print(f"Resolution: 1920x1080, FPS: {FPS}, Duration: 20s")
    print("Audio: Ambient electronic (generated, libre de droit)")
else:
    print(f"FFmpeg error: {result.stderr}")
    # Fallback: just keep the silent video
    print(f"Silent video available: {OUTPUT_VIDEO}")
