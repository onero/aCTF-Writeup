+++
title = 'ImageMagick'
categories = ['Misc']
date = "2026-08-23T15:30:00+01:00"
description = "Do command-line image surgery with ImageMagick: inspect with identify, stitch strips with append, crop regions, convert formats, and reveal hidden layers."
tags = ["imagemagick", "forensics", "steganography", "image-processing"]
scrollToTop = true
+++

# ImageMagick: Command-Line Image Surgery

[ImageMagick](https://imagemagick.org/) is a scriptable image-manipulation toolkit — think Photoshop operations you can run from the terminal and loop over. In CTFs it earns its keep for the unglamorous but constant tasks: stitching image fragments back together, cropping a region out of a larger picture, converting formats, and flattening layers. No GUI, no clicking, fully reproducible.

Two Brunner 2026 challenges used it directly: *Magic or Not* (stitching decoded strips into the final image) and *Business Trip* (cropping a region for closer inspection).

## Installation

```bash
# Debian/Ubuntu
sudo apt install imagemagick
# macOS
brew install imagemagick
```

Modern ImageMagick (v7) uses a single `magick` command; v6 uses individual commands like `convert`, `identify`, `montage`. Both are shown below — if `convert` is missing, prefix with `magick` (e.g. `magick convert ...` or just `magick ...`).

## Inspect first: identify

Before transforming anything, know what you have — dimensions, format, colour depth:

```bash
identify image.png
#   image.png PNG 800x600 800x600+0+0 8-bit sRGB 45KB
identify -verbose image.png    # everything: geometry, channels, embedded profiles
```

## Stitching images together (append)

This is the *Magic or Not* move: you've decoded several horizontal strips and need them recombined into one image.

```bash
# horizontal — place images left to right
convert strip1.png strip2.png strip3.png +append combined.png

# vertical — stack top to bottom
convert row1.png row2.png row3.png -append combined.png
```

Mnemonic: **`+append`** joins **side by side** (columns), **`-append`** **stacks** (rows). Glob works too, but mind the ordering — shell globbing is lexical, so name fragments `00, 01, ... 10` (zero-padded) or list them explicitly:

```bash
convert $(ls -v strip*.png) +append combined.png
```

## Cropping a region

The *Business Trip* move: pull a specific rectangle out of a larger image (a sign, a landmark, a corner with a leak).

```bash
convert input.jpg -crop 300x200+50+80 region.jpg
#                        │   │   │  └ y offset from top-left
#                        │   │   └── x offset from top-left
#                        │   └────── height
#                        └────────── width  (WxH+X+Y)
```

To slice an image into a grid of equal tiles (handy when a challenge splits a flag across cells):

```bash
convert input.png -crop 100x100 tile_%02d.png    # every 100x100 block -> tile_00.png ...
```

## Format conversion and everyday transforms

```bash
convert image.webp image.png          # convert format by changing the extension
convert image.png -flatten out.png     # merge layers / remove alpha (reveals hidden layers)
convert image.png -negate inverted.png # invert colours — occasionally reveals hidden text
convert image.png -rotate 90 out.png
convert image.png -resize 200% big.png # upscale to read tiny detail
convert a.png b.png -compose difference -composite diff.png   # spot-the-difference
```

`-flatten` and `-negate` are quietly useful in stego-adjacent challenges: flattening can expose content hidden in a transparent or non-visible layer, and negating sometimes surfaces low-contrast text.

## montage: contact sheets

When you have many fragments and want to eyeball them at once (order, orientation, which piece goes where):

```bash
montage tile_*.png -tile 4x -geometry +2+2 sheet.png
```

## A word on the security policy

ImageMagick ships a `policy.xml` (often under `/etc/ImageMagick-*/`) that restricts risky coders and resources — a response to past vulnerabilities (e.g. "ImageTragick", ghostscript-backed formats). If a legitimate operation is refused with a `not authorized` error, that policy is why. Loosen it only for files you trust, and prefer working in a throwaway directory or container when handling challenge-supplied images.

## Best practices

- **`identify` before you transform.** Knowing exact dimensions makes crop/append offsets exact instead of trial-and-error.
- **Zero-pad and sort fragment names.** `+append`ing globbed strips in the wrong order is the most common way stitching goes sideways — use `ls -v` or explicit ordering.
- **Keep the original.** Always write to a new filename; ImageMagick will happily overwrite in place.
- **Reach for `-flatten` / `-negate` / `difference`** when a "normal-looking" image is the whole challenge — the hidden content is often one transform away.

## Conclusion

ImageMagick is the duct tape of image challenges: rarely the star, constantly needed. Whenever you've got pieces to reassemble, a region to isolate, or a format that won't open, one `convert` line beats a round-trip through a graphics editor — and it's repeatable when you inevitably get the offsets wrong the first time. Happy converting!
