import os
import subprocess
import struct
import pygame
import moderngl
from PIL import Image

# ==============================================================================
# ANIMATION CONFIGURATION
# ==============================================================================
SHADER_NAME = "balatro.txt"  # The .txt shader filename (must be in the same folder)
WIDTH = 1920                # Output width in pixels (e.g., 1920, 1280, 800)
HEIGHT = 1080                 # Output height in pixels (e.g., 1080, 720, 600)
LOOP_DURATION = 10.0            # Effective duration of the final loop (in seconds)
FADE_DURATION = 1.0              # Crossfade transition duration (in seconds)
FPS = 30                      # Framerate of the output animation

TOTAL_RECORDING_DURATION = LOOP_DURATION + FADE_DURATION
TOTAL_FRAMES = int(TOTAL_RECORDING_DURATION * FPS)

pygame.init()
pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF | pygame.HIDDEN)

ctx = moderngl.create_context()

vertex_shader = """
#version 130
in vec2 in_vert;
void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

if not os.path.exists(SHADER_NAME):
    raise FileNotFoundError(f"Error: Shader file '{SHADER_NAME}' not found!")

with open(SHADER_NAME, 'r') as f:
    raw_shader = f.read()

header = """#version 130
uniform vec2 iResolution;
uniform float iTime;
out vec4 fragColor;
vec2 fragCoord;
"""

raw_shader = raw_shader.replace("void mainImage(out vec4 fragColor, in vec2 fragCoord)", "void mainImage()")
raw_shader = raw_shader.replace("iResolution.xy", "iResolution")

main_function = """
void main() {
    fragCoord = gl_FragCoord.xy;
    mainImage();
}
"""
fragment_shader_content = header + raw_shader + main_function

print(f"🎬 Rendering {TOTAL_FRAMES} frames at {WIDTH}x{HEIGHT} @ {FPS} FPS...")


program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader_content)

vertices = [-1.0, -1.0,  1.0, -1.0, -1.0,  1.0, -1.0,  1.0,  1.0, -1.0,  1.0,  1.0]
binary_data = struct.pack(f"{len(vertices)}f", *vertices)
vbo = ctx.buffer(binary_data)
quad = ctx.simple_vertex_array(program, vbo, 'in_vert')

fbo = ctx.framebuffer(color_attachments=ctx.renderbuffer((WIDTH, HEIGHT)))
fbo.use()

if 'iResolution' in program:
    program['iResolution'].value = (WIDTH, HEIGHT)

for frame in range(TOTAL_FRAMES):
    current_time = frame / FPS
    if 'iTime' in program:
        program['iTime'].value = current_time
        
    ctx.clear(0.0, 0.0, 0.0, 1.0)
    quad.render()
    

    image = Image.frombytes('RGBA', (WIDTH, HEIGHT), fbo.read(components=4))
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(f"frame-{frame:04d}.png")

print("⚡ Frames generated successfully!")
print("🌀 Building dynamic FFmpeg filter for seamless crossfade...")

dynamic_filter = (
    f"split[orig][copy];"
    f"[copy]trim=start=0:end={FADE_DURATION},setpts=PTS-STARTPTS[fadein];"
    f"[orig]trim=start={FADE_DURATION}:end={TOTAL_RECORDING_DURATION},setpts=PTS-STARTPTS[main];"
    f"[main][fadein]xfade=transition=fade:duration={FADE_DURATION}:offset={LOOP_DURATION},"
    f"split[s0][s1];[s0]palettegen=max_colors=32:stats_mode=diff[p];"
    f"[s1][p]paletteuse=dither=none"
)

ffmpeg_command = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", "frame-%04d.png",
    "-filter_complex", dynamic_filter,
    "output_seamless_loop.gif"
]

print("📦 Compiling and compressing final GIF (output_seamless_loop.gif)...")

try:
    subprocess.run(ffmpeg_command, check=True)
    print("\n✨ PROCESS COMPLETED!")
    print(f"-> Your {LOOP_DURATION}s seamless GIF at {FPS} FPS is ready.")
except FileNotFoundError:
    print("\n❌ ERROR: FFmpeg was not found on your system!")
    print("-> The PNG frames were generated, but the GIF could not be compiled.")
    print("-> Please install FFmpeg and add it to your system PATH.")
except subprocess.CalledProcessError:
    print("\n❌ ERROR: FFmpeg failed to compile the GIF. Check your filter settings.")

# 10. Clean up temporary assets
print("🧹 Cleaning up temporary PNG frames...")
for file in os.listdir("."):
    if file.startswith("frame-") and file.endswith(".png"):
        os.remove(file)

pygame.quit()