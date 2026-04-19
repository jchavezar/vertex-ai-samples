"""Regenerate docs/embedding_space.png — UMAP projection of indexed embeddings.

Two ways to source vectors:

  1. From a local NPZ (ids + fused vectors) produced by the v1 build pipeline.
     Used in the original demo; kept as a fast offline path.

  2. From Vector Search via `read_index_datapoints` — the source of truth in v2.
     Use this once the streaming index has been populated.

Run:
    python pipeline/plot_embeddings.py --npz path/to/asset_index.npz
    # or
    python pipeline/plot_embeddings.py --from-vs --limit 400
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "docs" / "embedding_space.png"


def _kind_of(asset_id: str) -> str:
    s = str(asset_id)
    if s.startswith("ia-audio") or "-audio-" in s:
        return "music"
    m = re.match(r"(px|pb|envato)-([a-z]+)-", s)
    if not m:
        return "other"
    k = m.group(2)
    return {"vector": "graphic", "illustration": "graphic", "sfx": "sfx"}.get(k, k)


def load_from_npz(path: Path) -> tuple[np.ndarray, np.ndarray]:
    d = np.load(path, allow_pickle=True)
    return d["ids"], d["fused"]


def load_from_vector_search(limit: int) -> tuple[np.ndarray, np.ndarray]:
    """Pull a sample of datapoints (ids + vectors) from Vector Search."""
    from google.cloud import firestore  # type: ignore
    from google.cloud import aiplatform_v1  # type: ignore

    sys.path.insert(0, str(ROOT / "app"))
    import os
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    fs = firestore.Client(project=project)
    docs = list(fs.collection("segments").limit(limit).stream())
    ids = [d.id for d in docs]
    if not ids:
        raise SystemExit("no segments found in Firestore")
    print(f"sampled {len(ids)} segment ids from Firestore")

    from google.cloud import aiplatform  # type: ignore
    aiplatform.init(project=project, location=location)
    eps = aiplatform.MatchingEngineIndexEndpoint.list(
        filter='display_name="envato-vibe-endpoint"'
    )
    if not eps:
        raise SystemExit("no MatchingEngineIndexEndpoint named envato-vibe-endpoint")
    ep = eps[0]
    deployed = ep.deployed_indexes[0]
    index_resource = deployed.index

    api_endpoint = f"{location}-aiplatform.googleapis.com"
    client = aiplatform_v1.IndexServiceClient(
        client_options={"api_endpoint": api_endpoint}
    )

    vectors: list[np.ndarray] = []
    kept_ids: list[str] = []
    BATCH = 100
    for i in range(0, len(ids), BATCH):
        chunk = ids[i:i + BATCH]
        resp = client.read_index_datapoints(
            request=aiplatform_v1.ReadIndexDatapointsRequest(
                index=index_resource, ids=chunk,
            )
        )
        for dp in resp.datapoints:
            vectors.append(np.array(dp.feature_vector, dtype=np.float32))
            kept_ids.append(dp.datapoint_id)
    return np.array(kept_ids), np.stack(vectors)


def plot(ids: np.ndarray, X: np.ndarray, out: Path) -> None:
    import umap  # type: ignore
    import matplotlib.pyplot as plt

    print(f"loaded {X.shape[0]} vectors @ {X.shape[1]}-dim")
    kinds = np.array([_kind_of(i) for i in ids])
    print("counts:", {k: int((kinds == k).sum()) for k in np.unique(kinds)})

    reducer = umap.UMAP(
        n_neighbors=18, min_dist=0.18, metric="cosine", random_state=42,
    )
    emb2 = reducer.fit_transform(X)

    PALETTE = {
        "photo":   "#1A73E8", "video":   "#34A853",
        "music":   "#A142F4", "graphic": "#F4B400",
        "sfx":     "#EA4335", "other":   "#9AA0A6",
    }
    ORDER = ["photo", "video", "music", "graphic", "sfx", "other"]
    LABELS = {
        "photo": "Photos", "video": "Videos", "music": "Music",
        "graphic": "Graphics / Illustrations",
        "sfx": "Sound effects", "other": "Other",
    }

    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=170)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFBFC")

    for k in ORDER:
        mask = kinds == k
        if not mask.any():
            continue
        ax.scatter(
            emb2[mask, 0], emb2[mask, 1],
            s=70, c=PALETTE[k], label=f"{LABELS[k]} ({mask.sum()})",
            edgecolors="white", linewidths=1.2, alpha=0.95,
        )

    ax.set_title(
        f"{X.shape[0]} real assets, one shared 3072-dim embedding space\n"
        "UMAP projection · colour = modality · proximity = semantic similarity",
        fontsize=13, fontweight="600", color="#202124", pad=18, loc="left",
    )
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#DADCE0")
    ax.tick_params(colors="#5F6368", labelsize=8)
    ax.set_xlabel("UMAP-1", color="#5F6368", fontsize=9)
    ax.set_ylabel("UMAP-2", color="#5F6368", fontsize=9)
    ax.grid(True, color="#ECEFF1", linewidth=0.6, zorder=0)

    leg = ax.legend(
        loc="upper left", bbox_to_anchor=(1.01, 1.0),
        frameon=False, fontsize=10, title="Modality",
        title_fontsize=10, labelcolor="#202124",
    )
    leg.get_title().set_color("#202124")
    leg.get_title().set_fontweight("600")

    plt.tight_layout(rect=[0, 0.02, 0.85, 1])
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=170, bbox_inches="tight", facecolor="white")
    print(f"saved -> {out}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--npz", type=Path, help="local NPZ produced by v1 build")
    g.add_argument("--from-vs", action="store_true",
                   help="pull live vectors from Vector Search")
    p.add_argument("--limit", type=int, default=400,
                   help="max datapoints when sourcing from Vector Search")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = p.parse_args()

    if args.npz:
        ids, X = load_from_npz(args.npz)
    else:
        ids, X = load_from_vector_search(args.limit)
    plot(ids, X, args.out)


if __name__ == "__main__":
    main()
