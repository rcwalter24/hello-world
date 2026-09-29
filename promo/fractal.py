"""Numba Mandelbrot kernel (kept apart from the manim namespace)."""
import numba
import numpy as np


@numba.njit(parallel=True, fastmath=True)
def mandel(cx, cy, w, px, py, maxit):
    out = np.zeros((py, px), np.float64)
    h = w * py / px
    for j in numba.prange(py):
        y0 = cy + h / 2 - h * j / (py - 1)
        for i in range(px):
            x0 = cx - w / 2 + w * i / (px - 1)
            x = 0.0; y = 0.0; n = 0
            while x * x + y * y < 256.0 and n < maxit:
                x, y = x * x - y * y + x0, 2 * x * y + y0
                n += 1
            if n == maxit:
                out[j, i] = -1.0
            else:
                out[j, i] = n + 1 - np.log2(np.log(np.sqrt(x * x + y * y)))
    return out
