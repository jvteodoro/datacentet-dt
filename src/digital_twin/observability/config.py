from __future__ import annotations

OBS_TOPK_DEFAULT = 20
OBS_TOPK_HARD_MAX = 100

OBS_HIST_BINS_BACKLOG: tuple[float, ...] = (0.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0)
OBS_HIST_BINS_CPU: tuple[float, ...] = (0.0, 10.0, 20.0, 40.0, 60.0, 80.0, 100.0)
OBS_HIST_BINS_MEM: tuple[float, ...] = (0.0, 16.0, 32.0, 64.0, 128.0, 256.0, 512.0)
