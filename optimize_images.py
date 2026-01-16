import os
from pathlib import Path
from PIL import Image

ROOTS = [
    Path(__file__).resolve().parent / 'src' / 'static' / 'images',
    Path(__file__).resolve().parent / 'src' / 'staticfiles' / 'images'
]
MAX_W = 2000
MIN_BYTES = 120 * 1024  # skip tiny files

skipped = 0
optimized = 0

for root in ROOTS:
    if not root.exists():
        continue
    for path in root.rglob('*'):
        if path.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
            continue
        if path.stat().st_size < MIN_BYTES:
            skipped += 1
            continue
        try:
            im = Image.open(path)
            # Resize if wider than MAX_W
            if im.width > MAX_W:
                im = im.resize((MAX_W, int(im.height * MAX_W / im.width)), Image.LANCZOS)
            # Convert PNG with no alpha to palette
            if path.suffix.lower() == '.png':
                has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
                if has_alpha:
                    im = im.convert('RGBA')
                    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
                    bg.paste(im, mask=im.split()[-1])
                    im = bg.convert('RGB')
                im = im.convert('P', palette=Image.ADAPTIVE, colors=256)
                im.save(path, format='PNG', optimize=True)
            else:
                im = im.convert('RGB')
                im.save(path, format='JPEG', quality=82, progressive=True, optimize=True)
            optimized += 1
            print(f"optimized {path} -> {path.stat().st_size/1024:.1f} KB")
        except Exception as e:
            print(f"skip {path}: {e}")

print(f"Done. optimized={optimized}, skipped_small={skipped}")
