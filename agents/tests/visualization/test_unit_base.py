"""Unit tests: matplotlib base helpers."""

import base64

import matplotlib.pyplot as plt

from agents.modeling_charts import fig_to_base64_png
from .helpers import assert_valid_png_base64


def test_fig_to_base64_png_produces_valid_png():
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.plot([0, 1], [1, 0])
    ax.set_title("unit")
    b64 = fig_to_base64_png(fig)
    assert_valid_png_base64(b64)
    fig2, _ = plt.subplots()
    plt.close(fig2)


def test_fig_to_base64_png_roundtrips_through_standard_b64decode():
    fig, ax = plt.subplots(figsize=(1.5, 1.5))
    ax.text(0.5, 0.5, "x", ha="center")
    b64 = fig_to_base64_png(fig)
    decoded = base64.standard_b64decode(b64)
    assert decoded.startswith(b"\x89PNG")
