# THE UNREASONABLE BEAUTY

An animated promo film (English) on the beauty of **mathematics, physics and computation**,
from counting dots to the open problems at the edge of knowledge.

- Final video: `output/the_unreasonable_beauty.mp4` (1080p30, with synthesized soundtrack)
- Concept & storyboard (中文): [`STORYBOARD.md`](STORYBOARD.md)

## Chapters

| # | Chapter | Highlights |
|---|---|---|
| 0 | Opening | a single point splits into the three disciplines |
| I | NUMBER | Gauss's sum as a picture · binary counting · Sieve of Eratosthenes |
| II | SHAPE | Pythagoras by rearrangement · rolling circle → π and the cycloid · Galileo |
| III | CHANGE | derivative, integral, FTC · Newton + step-by-step simulation · figure-eight 3-body orbit |
| IV | WAVES | Euler's formula & identity · Fourier epicycles drawing π · square-wave synthesis |
| V | LIGHT & QUANTA | Maxwell's equations · 3D EM wave · double slit, one electron at a time |
| VI | COMPUTATION | Turing machine adding one · quicksort · Game of Life · Mandelbrot zoom ×100,000 |
| VII | LEARNING | neural network forward pass · gradient descent on a loss landscape |
| VIII | THE FRONTIER | curved spacetime & LIGO chirp · qubits · Riemann ζ on the critical line · open questions |
| ∞ | Finale | "Mathematics is the language. Physics is the story. Computation is the pen." |

## Build

Requirements: Python 3.10+, [Manim Community](https://www.manim.community/) 0.19+, a LaTeX
install (with `dvisvgm`), FFmpeg, the Montserrat and Inter fonts, plus `numba`, `mpmath`, `scipy`.

```bash
pip install manim numba mpmath scipy
./build.sh l   # quick 480p preview
./build.sh h   # final 1080p30 → output/the_unreasonable_beauty.mp4
```

Render a single scene: `manim -pql --disable_caching ch4_waves.py S04_Waves`.
