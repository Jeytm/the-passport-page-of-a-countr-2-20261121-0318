#!/usr/bin/env python3
"""Entrypoint: render the invented Tarnovia passport spread.

Writes one image, entry.png, to $MAKEFUN_OUTPUT_DIR (default: current
directory). Stdlib + Pillow only, no network, deterministic.
"""

import os

import render


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    img = render.render()
    img.save(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
