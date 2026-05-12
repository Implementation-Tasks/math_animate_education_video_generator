# Math Proof Animator

*Transform complex mathematical proofs into professional animated videos with synchronized audio narration.*

## Overview

Math Proof Animator is a sophisticated Python-based system for automatically generating high-quality educational videos that visualize geometric proofs. It combines:

- **Geometric Visualization**: Precise construction and rendering of geometric figures
- **Text-to-Speech Integration**: Professional audio narration with Microsoft Edge TTS
- **Audio-Visual Synchronization**: Frame-perfect alignment between animation and narration
- **Automated Pipeline**: Complete workflow from LaTeX problem definition to final video

Perfect for creating content for:
- Online mathematics education
- Competitive mathematics preparation
- Academic proof documentation
- Mathematical video essays

## Features

✨ **Key Capabilities:**

- **Automatic Animation Generation** - Render complex geometric constructions programmatically
- **Synchronized Narration** - Text-to-speech with precise timing cues (VTT format)
- **Professional Output** - 1280×720 HD video at 12 FPS
- **Customizable Styling** - Color schemes, typography, line styles fully configurable
- **Modular Architecture** - Each component can be used independently or integrated
- **Vietnamese Mathematics Support** - Built for Vietnamese-language mathematical content (adaptable to other languages)

## Prerequisites

- **Python 3.13** or higher
- **FFmpeg** - For video encoding (install via [ffmpeg.org](https://ffmpeg.org/download.html))
- **Virtual Environment** - Python venv or similar

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Implementation-Tasks/math_animate_education_video_generator.git
cd math_animate_education_video_generator
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv env
& ".\env\Scripts\Activate.ps1"
```

**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
- `manim` - Mathematical animation library
- `edge-tts` - Microsoft Edge text-to-speech
- `numpy` - Numerical computing
- `pillow` - Image processing
- `av` - Audio/video handling

## Quick Start

### Basic Workflow

1. **Define Your Problem** - Create a `source.md` with LaTeX problem statement
2. **Generate Audio** - Convert text to speech narration
3. **Create Timestamps** - Align narration with VTT timing file
4. **Configure Geometry** - Save geometric point coordinates to JSON
5. **Render Animation** - Generate synchronized animation
6. **Compose Video** - Combine animation with text overlays

### Example: Run Complete Pipeline

```bash
# Ensure environment is active
python professional_math_video.py
```

This runs:
1. Geometric construction calculation
2. Animation rendering
3. Video composition and encoding

### Individual Components

**Generate Geometric Construction:**
```python
from geometric_construction import build_construction

construction_data = build_construction()
# Returns: {"radius": float, "points": {...}}
```

**Create Animation:**
```bash
manim -ql manim_timestamp_synced_animation.py TimestampSyncedGeometryAnimation -o output.mp4
```

**Compose Final Video:**
```bash
python make_animation_video.py
```

## Project Structure

```
├── README.md                              # This file
├── FullDescription.MD                     # Detailed technical documentation
│
├── Source Materials
├── source.md                              # LaTeX problem definition
├── geometric_construction.json            # Pre-calculated coordinates
├── sourcecompile_mathspeech.txt          # Narration transcription
├── sourcecompile_mathspeech.vtt          # Timing cues (WebVTT)
├── sourcecompile_mathspeech.mp3          # Audio narration
│
├── Core Modules
├── geometric_construction.py              # Geometry engine (coordinate calculations)
├── manim_symbolic_fixed.py               # Advanced animation setup
├── manim_timestamp_synced_animation.py   # Main animation scene
├── make_animation_video.py               # Video composition & text overlays
│
├── Supporting Scripts
├── animation.py                          # Basic animation demo
├── professional_math_video.py            # Full pipeline orchestrator
├── manim_audio_precise_animation.py     # Audio sync utilities
├── manim_geometry_animation.py          # Alternative geometry renderer
│
├── Environment
├── env/                                  # Python virtual environment
├── requirements.txt                      # Python dependencies (if present)
│
└── Output
    └── media/                           # Generated files (videos, images)
        ├── images/
        ├── videos/
        └── Tex/
```

## Configuration

### Video Settings (`make_animation_video.py`)

```python
WIDTH = 1280              # Video width in pixels
HEIGHT = 720              # Video height in pixels
FPS = 12                  # Frames per second
BG = (247, 249, 252)      # Background color (RGB)
```

### Color Scheme

```python
INK = "#18202c"           # Main text color
BLUE = "#235bae"          # Primary geometric color
GREEN = "#238c64"         # Alternate geometric color
ORANGE = "#d2781e"        # Highlight color
RED = "#c8373c"           # Important lines/proofs
PURPLE = "#6e4baa"        # Secondary color
```

### Audio Settings

- **Engine**: Microsoft Edge Text-to-Speech (edge-tts)
- **Duration**: Configurable per narration
- **Format**: MP3
- **Sync**: VTT (WebVTT) subtitle format for frame timing

## How It Works

### 1. Geometric Calculation

The `geometric_construction.py` module:
- Calculates triangle incenter
- Finds circle-line intersections
- Projects points onto lines
- Computes all required geometric points with sub-pixel precision
- Outputs coordinates as JSON for reproducibility

### 2. Audio Generation

Convert transcribed text to speech:
```bash
edge-tts --voice en-US-AriaNeural \
         --text "Your mathematical text here" \
         --write-media output.mp3
```

Pass narration through VTT timing for frame-perfect synchronization.

### 3. Animation Rendering

Manim rendering pipeline:
- Parse VTT timing cues into animation triggers
- Create geometric objects in scene
- Synchronize animations with audio timestamps
- Render with professional color scheme

### 4. Video Composition

Final assembly (`make_animation_video.py`):
- Generate PIL image frames with text overlays
- Add geometric animations per scene
- Burn-in subtitles and proofs
- Encode with FFmpeg to H.264
- Combine with audio track

## Example Problem

The current implementation animates a geometry proof involving:
- **Triangle ABC** with inscribed circle
- **Three-part proof** showing parallel lines, concyclic points, and perpendicularity
- **275-second narration** synchronized to animation

Problem statement available in [source.md](source.md).

## Creating Your Own Content

### Step 1: Write Your Problem

Create `source.md` in LaTeX format:
```latex
\textbf{Problem:} 
Triangle ABC with points...

\textbf{Proof:}
Consider the following construction...
```

### Step 2: Transcribe Narration

Create `sourcecompile_mathspeech.txt`:
```
PROBLEM STATEMENT

Triangle ABC is acute and non-isosceles...
```

### Step 3: Generate Coordinates

Calculate geometric points:
```python
from geometric_construction import build_construction, save_construction

data = {
    "radius": 1.809,
    "points": {
        "A": [0, 4.5],
        "B": [-2.5, 0],
        "C": [6, 0],
        # ... all required points
    }
}
# Save to geometric_construction.json
```

### Step 4: Generate Audio

```bash
edge-tts --voice vi-VN-HoaiMyNeural \
         --file sourcecompile_mathspeech.txt \
         --write-media sourcecompile_mathspeech.mp3
```

### Step 5: Create Timing File

Create `sourcecompile_mathspeech.vtt` with cue timings:
```vtt
WEBVTT

1
00:00:00,100 --> 00:00:01,650
First statement

2
00:00:01,650 --> 00:00:06,550
Second statement
```

### Step 6: Run Pipeline

```bash
python professional_math_video.py
```

## Performance Notes

- **Rendering Time**: Depends on animation complexity (typically 5-15 minutes for 275-second video)
- **Memory Usage**: ~2-4 GB during rendering
- **File Output**: ~100-500 MB per video
- **FPS**: 12 FPS keeps file size manageable while maintaining smoothness

## Troubleshooting

**Video not generating:**
- Ensure FFmpeg is installed and in PATH
- Check Python virtual environment is activated
- Verify geometric_construction.json exists and is valid

**Audio out of sync:**
- Verify VTT timing matches actual audio duration
- Check audio sample rate (typically 44.1 kHz or 48 kHz)

**Geometry rendering incorrectly:**
- Validate coordinate values in geometric_construction.json
- Check triangle is non-degenerate (vertices not collinear)

## Requirements

See detailed requirements in [FullDescription.MD](FullDescription.MD#technology-stack).

**Main Dependencies:**
- Python 3.13+
- Manim 0.20.1
- NumPy 1.24+
- Pillow 10.0+
- edge-tts 7.2.8
- FFmpeg 5.0+

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions welcome! Areas for enhancement:

- Support for additional languages
- 3D geometry visualization
- Interactive proof exploration
- Real-time animation preview
- Batch video generation pipeline

## Support

For issues, questions, or suggestions:
1. Check [FullDescription.MD](FullDescription.MD) for detailed technical documentation
2. Review example implementations in included `.py` files
3. Test with provided sample geometry to isolate issues

## Acknowledgments

Built with:
- **Manim** - Mathematical animation engine
- **Microsoft Edge TTS** - Professional audio synthesis
- **NumPy** - Scientific computing
- **FFmpeg** - Video processing
- **Pillow** - Image manipulation

## Citation

If you use this project in academic work, citation details TBD.

---

**Last Updated**: May 12, 2026
**Status**: Active Development
