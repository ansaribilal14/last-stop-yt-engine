# STORAGE POLICY
- Tier 1 (permanent): Git — all code, scripts, research, narration, timelines, manifests.
- Tier 2 (persistent, user-controlled): GitHub Release assets — films, clip archives (≤2GiB each).
- Tier 3 (temporary mirror): storage.to — fast delivery mirror, anonymous 25GB/3-day expiry;
  owner_token saved beside asset (*.storageto.json); delete after user confirms download.
- Upload order on asset completion: verify file → SHA-256 → upload_storageto.py →
  release upload → update ASSET_MANIFEST.json → commit+push. Never batch-defer uploads.
