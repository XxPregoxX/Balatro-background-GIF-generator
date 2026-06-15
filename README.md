# Shader to Seamless GIF Renderer

A Python utility that leverages the GPU to render GLSL Fragment Shaders (Shadertoy format) and compile them into perfectly looping, highly optimized GIFs with seamless crossfade transitions.

## 🚀 Features

* **GPU Accelerated:** Uses `ModernGL` and `Pygame` to render shaders directly on the hardware, ensuring fast frame generation.
* **Seamless Loops:** Dynamically calculates and applies an `xfade` filter via FFmpeg to blend the beginning and end of the animation, creating a perfect, unnoticeable loop.
* **Optimized Output:** Automatically generates a strict 32-color palette using a differential statistics mode (`palettegen=stats_mode=diff`) to drastically reduce GIF file size while maintaining visual fidelity (ideal for platforms like Canva or PowerPoint).
* **Fully Dynamic Configuration:** Variables for resolution, target frame rate, loop duration, and fade length can be adjusted at the top of the script, and the FFmpeg filter chain auto-adapts dynamically.

## 💻 How to Use

1. Clone this repository.
2. Place your GLSL shader file in the root folder and name it `balatro.txt` (or update `SHADER_NAME` in the script).
3. Set up your virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
