# Project Full Description: Interactive Mathematical Proof Animation System

## Overview
This project is a sophisticated **Python-based automated system for creating professional mathematical education videos** that combines:
- Complex geometric problem visualization
- Text-to-speech (TTS) narration with precise timing
- Synchronized animation rendering using Manim library
- Multi-step video production pipeline with subtitle generation

The project demonstrates a complete workflow for transforming academic mathematics problems into engaging visual education content with synchronized sound.

---

## Core Problem Domain

### Mathematical Content
The project focuses on a challenging **geometry proof problem** (in Vietnamese):

**Problem Statement:**
- Triangle ABC is acute and non-isosceles (AB < AC)
- Triangle ABC is circumscribed around circle (I) with center I
- Circle (I) is tangent to sides BC, CA, AB at points D, E, F respectively
- K, L are the feet of perpendiculars from B, C to a line through I parallel to EF

**Three Parts to Prove:**
1. **Part 1:** DK is parallel to IC
2. **Part 2:** Lines KF and EL intersect at a point on circle (I)
3. **Part 3:** Given M, N as points where DK, DL intersect circle (I) again, and P where MN intersects BC, prove that PI ⊥ AS (where S is the other endpoint of diameter DS)

This is an advanced competition mathematics problem requiring detailed geometric analysis.

---

## Project Architecture & File Structure

### 1. **Source Content Files**

#### `source.md` (Main Problem Document)
- Contains the complete geometry problem in **LaTeX/TikZ format**
- Includes the detailed geometric construction diagram specification
- Provides the full mathematical solution with step-by-step proofs
- Written in Vietnamese mathematical notation

#### `sourcecompile_mathspeech.txt` (Audio Transcription)
- Converted natural language version of the mathematical problem and solution
- Breaks down complex theorems into spoken sentences
- Organized by problem parts and proof steps
- Approximately 275 seconds of audio content

#### `sourcecompile_mathspeech.vtt` (Video Subtitle Timing)
- WebVTT format subtitle file with precise timestamps
- Synchronizes text segments with audio playback timing
- Used for both subtitle display and animation synchronization
- Enables frame-by-frame animation triggering

#### `sourcecompile_mathspeech.mp3` (Audio File)
- Mono/stereo MP3 audio file (275.328 seconds duration)
- Generated from transcribed text using edge-tts (Microsoft Edge Text-to-Speech)
- Provides professional narration for the mathematical exposition

#### `geometric_construction.json` (Coordinate Data)
- Pre-calculated coordinates for all geometric points (A, B, C, I, D, E, F, K, L, M, N, P, S, J)
- Incircle radius measurement
- Enables precise, reproducible geometric construction
- Data format:
  ```json
  {
    "radius": <float>,
    "points": {
      "A": [x, y],
      "B": [x, y],
      ...
    }
  }
  ```

### 2. **Core Python Modules**

#### `geometric_construction.py` (Geometry Engine)
**Purpose:** Low-level geometric computation and construction

**Key Classes:**
- `Point`: Immutable 2D point with vector operations
  - Supports: addition, subtraction, scaling, dot product, cross product, normalization
  - Utility methods: `norm()`, `as_tuple()` for conversion

**Key Functions:**
- `distance(a, b)`: Euclidean distance between points
- `foot_point(p, a, b)`: Project point p onto line ab
- `line_intersection(a, b, c, d)`: Find intersection of two lines
- `circle_line_intersections(center, radius, a, b)`: Find circle-line intersection points
- `incenter(a, b, c)`: Compute triangle incenter (center of inscribed circle)
- `build_construction()`: Load and validate the geometry from JSON

**Purpose:** Provides computational foundation for all geometric algorithms

---

#### `manim_symbolic_fixed.py` (Advanced Animation Engine)
**Purpose:** Creates synchronized animation sequences with precise timing

**Features:**
- Color scheme definition (INK, MUTED, BLUE, GREEN, ORANGE, RED, PURPLE)
- Uses DejaVu Sans font for mathematical notation
- CUE system: Parses VTT subtitle timing into animation triggers
- `parse_vtt(path)`: Converts VTT subtitles into indexed timing cues

**Data Structures:**
```python
@dataclass(frozen=True)
class Cue:
    index: int      # Subtitle sequence number
    start: float    # Start time in seconds
    end: float      # End time in seconds
    text: str       # Subtitle text content
```

**Animation Pipeline:**
- Reads geometric data from JSON
- Loads corresponding audio file
- Parses VTT timing information
- Renders animated scene synchronized to audio narration
- Creates multiple animation passes for different proof parts

---

#### `manim_timestamp_synced_animation.py` (Main Animation Scene)
**Purpose:** Orchestrates the complete animated geometric proof

**Key Class:** `TimestampSyncedGeometryAnimation(Scene)`

**Animation Objects Dictionary:**
Creates Manim VMobject instances for:
- **"triangle":** ABC triangle with vertices and labels
- **"incircle":** Circle (I) with center point
- **"contacts":** Points D, E, F (tangency points)
- **"ef":** Line segment EF (orange, stroke_width=4)
- **"kl":** Line segment KL with perpendicular points (orange)
- **"bkcl":** Construction lines BK and CL (dashed, muted)
- **"dk_ic":** Key segments DK and IC for Part 1 (red, highlighted)
- Additional objects for Parts 2 and 3

**Rendering Features:**
- Custom coordinate transformation: `p(name)` - scales and translates coordinates
- Line types: solid, dashed with custom colors and widths
- Dot rendering with labels and directional positioning
- Synchronized timing tied to audio cues

**Background Color:** Light gray (#f7f9fc) for professional appearance

---

#### `make_animation_video.py` (Video Composition)
**Purpose:** Combines geometric animation with text overlays for final video

**Specifications:**
- **Resolution:** 1280 × 720 pixels (standard HD)
- **Frame Rate:** 12 FPS (smooth animation at lower compute cost)
- **Background:** Light cream color (RGB: 247, 249, 252)
- **Color Scheme:** Matches symbolic animation module

**Scene Structure:**
Defines 6 major scenes with time ranges:
1. **"Đề bài" (Problem Statement):** 0.00-0.16s
   - Shows triangle, incircle, tangency points
   - Establishes problem setup

2. **"Mục tiêu" (Objectives):** 0.16-0.29s
   - Lists three proof parts as text
   - Provides proof overview

3. **"Phần 1" (Part 1 Proof):** 0.29-0.46s
   - Demonstrates DK ∥ IC
   - Shows angle relationships

4. **"Phần 2" (Part 2 Proof):** 0.46-0.68s
   - Shows concyclic points
   - Demonstrates line intersection on circle

5. **"Phần 3" (Part 3 Proof):** 0.68-0.88s
   - Constructs rectangle MNEF
   - Shows triangle similarity

6. **"Kết luận" (Conclusion):** 0.88-1.01s
   - Final result and verification
   - Summary of findings

**Video Assembly Process:**
- Renders PIL Image frames with text overlays
- Each scene has associated animation tags for geometric object visibility
- Uses FFmpeg for video encoding
- Supports subtitle burn-in and audio synchronization

---

### 3. **Production Files**

#### `animation.py` (Basic Animation Demo)
- Simpler animation example showing basic line properties
- Demonstrates Manim scene structure
- Tests fundamental animation techniques (FadeIn, FadeOut, Create, Write)
- Illustrates rendering of geometric primitives

#### `professional_math_video.py` (Video Assembly Script)
- Orchestrates complete video production pipeline
- Runs: `geometry_construction.py` → `manim_*_animation.py` → `make_animation_video.py`
- Manages subprocess execution and file I/O
- Handles FFmpeg integration for final encoding

#### `manim_audio_precise_animation.py`
- Enhanced audio synchronization module
- Precise frame-to-timestamp mapping
- Calculates frame delays and video duration
- Ensures sub-frame timing accuracy

#### `manim_geometry_animation.py`
- Earlier iteration of geometry animation
- Provides alternative rendering approach
- Used for prototyping and testing

#### `manim_symbolic_full_animation.py`
- Complete animation with all proof sections
- Includes full LaTeX formula rendering
- Integrates all three proof parts seamlessly

---

### 4. **Support & Logging**

#### `geogebra_construction.txt`
- Backup geometric construction in GeoGebra format
- Alternative tool for verification
- Can be imported into GeoGebra for manual verification

#### `quytrinh.txt`
- Process documentation (currently empty/placeholder)
- Intended for step-by-step workflow notes

#### `VIDEOFLOW.txt` (Workflow Documentation)
- Describes production pipeline:
  1. `source.md` (LaTeX problem) → extracted text content
  2. Text → `sourcecompile_mathspeech.txt` (narration)
  3. Narration → `sourcecompile_mathspeech.vtt` (timing subtitles)
  4. VTT + narration → `sourcecompile_mathspeech.mp3` (audio)
  5. Synchronized with Manim animations → final video

#### `editnew.md` (Edit Specifications)
- Video editing requirements for vertical frame format
- Text/explanation placement above animation
- Animation positioning below text layer

#### `.aider.chat.history.md` & `.aider.input.history`
- Aider AI chat history (for context/debugging)
- Development interaction logs

---

### 5. **Environment & Dependencies**

#### `env/` (Python Virtual Environment)
Complete isolated Python environment with:

**Key Dependencies:**
- **manim** (0.20.1): Animation engine for mathematical visualization
- **edge_tts** (7.2.8): Text-to-speech audio generation
- **srt**: SRT/VTT subtitle file manipulation
- **scipy** (1.17.1): Scientific computing
- **Pillow (PIL)**: Image processing
- **NumPy**: Numerical computing
- **beautiful-soup4**: HTML/XML parsing
- **av** (17.0.1): Audio/video processing
- **moderngl** (3.1.1): OpenGL graphics library
- **cairo**: 2D graphics rendering

#### Output Directories

**`media/`** - Generated output files
- `images/`: Rendered animation frames and construction diagrams
- `videos/`: Final video outputs
- `Tex/`: LaTeX temporary files
- `texts/`: Text rendering caches

**`_tts_segments/`** - Audio segment files
- Individual MP3 chunks from text-to-speech synthesis
- `concat.txt`: FFmpeg concat demuxer file for segment assembly

---

## Workflow Pipeline

### Step 1: Problem Definition
```
source.md (LaTeX) → Manual transcription
                 → sourcecompile_mathspeech.txt
```

### Step 2: Audio Generation
```
Transcribed text → edge-tts library
                → sourcecompile_mathspeech.mp3 (275.328s)
```

### Step 3: Timing Synchronization
```
sourcecompile_mathspeech.mp3 → Manual/automatic alignment
                            → sourcecompile_mathspeech.vtt
```

### Step 4: Geometric Construction
```
Triangle ABC coordinates & incircle parameters
                                    ↓
                     geometric_construction.json
                          (pre-calculated points)
```

### Step 5: Animation Rendering
```
geometric_construction.json + sourcecompile_mathspeech.vtt
                     ↓
        manim_timestamp_synced_animation.py
                     ↓
            Synchronized animation frames
```

### Step 6: Video Composition
```
Animation frames + Text overlays + Audio
                     ↓
          make_animation_video.py
                     ↓
      Final video (1280×720, 12FPS, MP4)
```

---

## Technical Highlights

### Geometric Algorithms
- **Precise coordinate calculations** for complex triangle-incircle configuration
- **Circle-line intersection** using quadratic formula
- **Point projection** onto lines for perpendicular constructions
- **Incenter calculation** using weighted average of vertices

### Audio-Visual Synchronization
- **VTT timing cues** trigger animation events
- **Precise frame timing** ensures audio-visual alignment
- **Sub-second accuracy** for mathematical narration

### Animation Features
- **Complex multi-part proof visualization**
- **Layered object rendering** (triangle, circle, construction lines, points)
- **Color-coded elements** for visual clarity
- **Professional typography** with mathematical notation

### Performance Optimizations
- **Pre-calculated geometry** (JSON storage)
- **Lower FPS (12 FPS)** for faster rendering
- **Modular scene structure** for incremental rendering
- **Efficient Manim memory management**

---

## Unique Aspects

1. **Academic-Grade Mathematics**: Advanced competition-level geometry proofs
2. **Multi-Language Support**: Vietnamese mathematical narrative with international conventions
3. **Automated Production**: Complete pipeline from LaTeX to final video
4. **Precise Synchronization**: Audio narration perfectly aligned with geometric visualizations
5. **Professional Quality**: HD resolution, custom color schemes, proper typography
6. **Reproducibility**: All constructions based on saved coordinate data
7. **Modular Design**: Each component can be independently tested/modified

---

## Use Cases

1. **Educational Content Creation**: Generate math education videos automatically
2. **Mathematical Proof Visualization**: Animate complex geometry proofs
3. **Academic Documentation**: Create video proofs for mathematical papers
4. **Online Mathematics Courses**: Produce high-quality instructional content
5. **Competition Mathematics**: Visualize challenging olympiad-level problems

---

## Technology Stack

| Category | Technology |
|----------|-----------|
| **Animation** | Manim 0.20.1 |
| **Graphics** | ModernGL, Cairo |
| **Audio** | Edge-TTS, FFmpeg |
| **Computation** | NumPy, SciPy |
| **Image Processing** | Pillow (PIL) |
| **Subtitle Format** | WebVTT |
| **Video Codec** | H.264 (via FFmpeg) |
| **Language** | Python 3.13 |
| **Development** | Aider (AI-assisted coding) |

---

## Project Status

- **Phase**: Active Development/Production
- **Primary Use**: Creating Vietnamese mathematical education content
- **Output Quality**: Professional HD (1280×720)
- **Audio Duration**: ~275 seconds per video
- **Customization**: Highly modular for different geometric problems

---

## Summary

This project represents a **complete automated system** for transforming complex mathematical problems into professional educational video content. By integrating precise geometric calculations, high-quality audio narration, and synchronized Manim animations, it creates engaging visual explanations of advanced mathematics suitable for educational platforms, online courses, or academic documentation.

The system is particularly valuable for:
- Converting static mathematical proofs into dynamic visualizations
- Generating content at scale for mathematics education
- Demonstrating geometric relationships that are difficult to convey in text or static diagrams
- Creating archive-quality educational resources with precise A/V synchronization
