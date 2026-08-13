"""Local Image Generation plugin — Diffusers wrapper.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from backend.app.hands import registry

_IMAGES_DIR = Path(os.environ.get("JARVIS_IMAGES_DIR", "generated_images"))
_IMAGES_DIR.mkdir(exist_ok=True)


def _image_generate(prompt: str, filename: str = "output.png") -> dict[str, Any]:
    """Generate image locally using Diffusers / Stable Diffusion model."""
    try:
        from diffusers import StableDiffusionPipeline
        import torch
        
        pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
        image = pipe(prompt).images[0]
        
        filepath = _IMAGES_DIR / filename
        image.save(str(filepath))
        return {"status": "generated", "filepath": str(filepath.resolve())}
    except Exception as exc:
        return {"error": f"Diffusers pipeline uninitialized: {exc}. Requires PyTorch & Diffusers packages."}


registry.register(
    {
        "name": "image_generate",
        "description": "Generate an image from prompt text locally using PyTorch Diffusers pipeline.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_once",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
                "filename": {"type": "string"},
            },
            "required": ["prompt"],
        },
        "returns": {"type": "object", "properties": {"filepath": {"type": "string"}}},
        "scopes": ["media:write"],
        "tags": ["image", "generation", "diffusers"],
    },
    _image_generate,
)
