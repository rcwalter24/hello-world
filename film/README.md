# The Source Code of Everything — 3-minute animated film (English, captions + score)

Final cut: `release/The_Source_Code_of_Everything.mp4` (1080p30, 180 s).

Rebuild: `python3 -m venv /opt/mv && /opt/mv/bin/pip install manim numpy scipy`, install ffmpeg, LaTeX and the Inter font,
then `/opt/mv/bin/python audio/music.py && ./build.sh` (use `./build.sh l` for a fast low-res preview).

- `style.py` shared palette/helpers · `act0…act6_*.py` one Manim scene per act (fixed time budgets) · `audio/music.py` procedural score
- Design notes: `BRIEF.md`, `../docs/concept.md`
