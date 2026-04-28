"""Chat 110c: three atomic data edits.

1. layers.yaml — recolor tpit_subs from cyan #06b6d4 to substations purple #a78bfa.
2. layers.yaml — reorder Transmission & Grid block from
     [transmission, substations, tpit_subs, tpit_lines]
   to
     [substations, tpit_subs, transmission, tpit_lines]
   so substations + their planned upgrades are adjacent in the sidebar before
   the line layers.
3. combined_geoms.geojson — replace longfellow_ranch geometry. Old polygon
   was placed in southern Pecos/Terrell/Brewster (Mitchell family ranch
   homestead), but the Project Horizon AI campus (Poolside / CoreWeave) is at
   the central-Pecos ERCOT cluster. New polygon centered ~30.77, -102.68.
   This also resolves overlap with la_escalera in the south.

All writes use temp-file + os.replace (OPERATING.md §6.15).
"""
import json, os, tempfile

YAML = "layers.yaml"
GEOJSON = "combined_geoms.geojson"

# --- Pass 1: layers.yaml -----------------------------------------------------

with open(YAML) as f:
    yaml_lines = f.read().splitlines(keepends=True)

# Find block boundaries by `- id:` markers at column 0.
block_starts = [i for i, line in enumerate(yaml_lines) if line.startswith("- id:")]
block_starts.append(len(yaml_lines))

blocks = []  # list of (id, lines_slice)
for i in range(len(block_starts) - 1):
    s, e = block_starts[i], block_starts[i + 1]
    chunk = yaml_lines[s:e]
    lid = chunk[0].split("- id:", 1)[1].strip()
    blocks.append((lid, chunk))

# Verify expected ids are present
ids = [b[0] for b in blocks]
for need in ("transmission", "substations", "tpit_subs", "tpit_lines"):
    assert need in ids, f"missing layer id in YAML: {need}"

# Recolor tpit_subs purple
for lid, chunk in blocks:
    if lid == "tpit_subs":
        for k, line in enumerate(chunk):
            if line.startswith("  color: '#06b6d4'"):
                chunk[k] = "  color: '#a78bfa'\n"
                print(f"[recolor] tpit_subs cyan -> purple")
                break

# Reorder: insert tpit_subs right after substations, then transmission stays
# in its slot relative to the others. Concretely, target order within group is
# substations, tpit_subs, transmission, tpit_lines.
desired_order = ["substations", "tpit_subs", "transmission", "tpit_lines"]
trans_block_ids = set(desired_order)
trans_blocks = {lid: chunk for lid, chunk in blocks if lid in trans_block_ids}

# Build new block list: walk original; when first transmission-group id is hit,
# emit the four in desired order and skip subsequent transmission-group ids.
new_blocks = []
emitted_trans = False
for lid, chunk in blocks:
    if lid in trans_block_ids:
        if not emitted_trans:
            for d in desired_order:
                new_blocks.append((d, trans_blocks[d]))
            emitted_trans = True
        continue
    new_blocks.append((lid, chunk))

# Sanity: total length unchanged (line count of all chunks == original)
orig_lines = sum(len(c) for _, c in blocks)
new_lines = sum(len(c) for _, c in new_blocks)
assert orig_lines == new_lines, f"line count drift: {orig_lines} -> {new_lines}"

# Reassemble: preamble (everything before first `- id:`) + blocks
preamble = yaml_lines[: block_starts[0]]
out_yaml = "".join(preamble) + "".join("".join(c) for _, c in new_blocks)

with tempfile.NamedTemporaryFile(
    mode="w", dir=os.path.dirname(os.path.abspath(YAML)) or ".",
    prefix=".layers.yaml.", suffix=".tmp", delete=False
) as tf:
    tf.write(out_yaml)
    tmp_path = tf.name
os.replace(tmp_path, YAML)
print(f"[reorder] new transmission group order: {desired_order}")

# --- Pass 2: combined_geoms.geojson — Longfellow geometry --------------------

# New ~10x10 mi polygon centered ~30.77, -102.68 (Project Horizon campus area;
# matches ERCOT queue cluster operator confirmed as Longfellow).
# Sized to leave >15 mi gap to GW Ranch at ~31.13, -102.84.
LONGFELLOW_NEW_RING = [
    [-102.76, 30.84],
    [-102.61, 30.84],
    [-102.59, 30.78],
    [-102.62, 30.71],
    [-102.71, 30.69],
    [-102.77, 30.74],
    [-102.78, 30.80],
    [-102.76, 30.84],
]

with open(GEOJSON) as f:
    gj = json.load(f)

moved = 0
for feat in gj["features"]:
    p = feat.get("properties") or {}
    if p.get("layer_id") == "longfellow_ranch":
        feat["geometry"] = {"type": "Polygon", "coordinates": [LONGFELLOW_NEW_RING]}
        moved += 1

assert moved >= 1, "no longfellow_ranch feature found in combined_geoms.geojson"
print(f"[move] longfellow_ranch geometry replaced ({moved} feature(s))")

with tempfile.NamedTemporaryFile(
    mode="w", dir=os.path.dirname(os.path.abspath(GEOJSON)) or ".",
    prefix=".combined_geoms.", suffix=".tmp", delete=False
) as tf:
    json.dump(gj, tf)
    tmp_path = tf.name
os.replace(tmp_path, GEOJSON)
print("[done]")
