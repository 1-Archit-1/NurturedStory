#!/usr/bin/env python3
"""
Backup script for SQLite DB and media files to Cloudflare R2.

Usage:
    python scripts/backup.py daily     — daily DB backup, retains 3 days
    python scripts/backup.py weekly    — weekly DB backup, retains 4 weeks
    python scripts/backup.py monthly   — monthly DB backup, retains 2 months
    python scripts/backup.py media     — sync media files to R2 (no versioning)

Required environment variables (set in Coolify):
    R2_ACCESS_KEY_ID        — R2 API access key
    R2_SECRET_ACCESS_KEY    — R2 API secret
    R2_ENDPOINT_URL         — https://<account_id>.r2.cloudflarestorage.com
    R2_BUCKET               — bucket name (e.g. "nurturedstory-backups")

Scheduled via Coolify Scheduled Tasks:
    daily   — python scripts/backup.py daily    — 0 3 * * *   (retains 3 days)
    weekly  — python scripts/backup.py weekly   — 0 4 * * 0   (retains 4 weeks)
    monthly — python scripts/backup.py monthly  — 0 5 1 * *   (retains 2 months)
    media   — python scripts/backup.py media    — 0 2 * * 0   (every Sunday 2am)
"""

import os
import sys
import sqlite3
import hashlib
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
from botocore.config import Config


DB_PATH    = Path("/app/data/db.sqlite3")
MEDIA_PATH = Path("/app/media")

# Retention days per DB backup cadence
RETENTION = {
    "daily":   3,
    "weekly":  28,
    "monthly": 62,
}


def log(message: str) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{timestamp}] {message}", flush=True)


def get_env(name: str) -> str:
    """Read a required env var or exit with a clear error."""
    value = os.environ.get(name)
    if not value:
        log(f"ERROR: {name} is not set")
        sys.exit(1)
    return value


def make_client() -> boto3.client:
    return boto3.client(
        "s3",
        endpoint_url=get_env("R2_ENDPOINT_URL"),
        aws_access_key_id=get_env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=get_env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


# =============================================================================
# DB backup
# =============================================================================

def snapshot_db(dest_path: Path) -> None:
    """Take a live snapshot of the SQLite DB using the online backup API."""
    with sqlite3.connect(DB_PATH) as source, sqlite3.connect(dest_path) as dest:
        source.backup(dest)


def prune_old_backups(client, bucket: str, prefix: str, retain_days: int) -> None:
    """Delete objects in the given prefix older than retain_days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=retain_days)

    paginator = client.get_paginator("list_objects_v2")
    to_delete = []
    for page in paginator.paginate(Bucket=bucket, Prefix=f"{prefix}/"):
        for obj in page.get("Contents", []):
            if obj["LastModified"] < cutoff:
                to_delete.append({"Key": obj["Key"]})

    if not to_delete:
        return

    for i in range(0, len(to_delete), 1000):
        batch = to_delete[i:i + 1000]
        client.delete_objects(Bucket=bucket, Delete={"Objects": batch})
        for item in batch:
            log(f"Pruned: {item['Key']}")


def backup_db(cadence: str) -> None:
    log(f"Starting {cadence} DB backup")

    if not DB_PATH.exists():
        log(f"ERROR: database not found at {DB_PATH}")
        sys.exit(1)

    client = make_client()
    bucket = get_env("R2_BUCKET")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    key = f"{cadence}/db-{timestamp}.sqlite3"

    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        snapshot_db(tmp_path)
        client.upload_file(str(tmp_path), bucket, key)
        log(f"Uploaded to s3://{bucket}/{key}")
        prune_old_backups(client, bucket, cadence, RETENTION[cadence])
    finally:
        tmp_path.unlink(missing_ok=True)

    log("DB backup complete")


# =============================================================================
# Media sync
# =============================================================================

def backup_media() -> None:
    """
    Sync /app/media to R2 under the 'media/' prefix.
    Uses ETag comparison to skip unchanged files — only uploads new/modified files.
    Does not delete files from R2 that are removed locally (safe default).
    """
    log("Starting media sync")

    if not MEDIA_PATH.exists():
        log("No media directory found — skipping")
        return

    client = make_client()
    bucket = get_env("R2_BUCKET")

    # Build a map of existing R2 objects: key → ETag
    existing: dict[str, str] = {}
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix="media/"):
        for obj in page.get("Contents", []):
            existing[obj["Key"]] = obj["ETag"].strip('"')

    uploaded = 0
    skipped  = 0

    for local_file in sorted(MEDIA_PATH.rglob("*")):
        if not local_file.is_file():
            continue

        relative = local_file.relative_to(MEDIA_PATH)
        r2_key   = f"media/{relative.as_posix()}"

        # Compare MD5 with R2 ETag to skip unchanged files
        md5 = hashlib.md5(local_file.read_bytes()).hexdigest()

        if existing.get(r2_key) == md5:
            skipped += 1
            continue

        client.upload_file(str(local_file), bucket, r2_key)
        log(f"Uploaded: {r2_key}")
        uploaded += 1

    log(f"Media sync complete — {uploaded} uploaded, {skipped} unchanged")


# =============================================================================
# Entry point
# =============================================================================

def main() -> None:
    cadence = sys.argv[1] if len(sys.argv) > 1 else "daily"

    if cadence == "media":
        backup_media()
    elif cadence in RETENTION:
        backup_db(cadence)
    else:
        log(f"ERROR: unknown cadence '{cadence}' (expected daily|weekly|monthly|media)")
        sys.exit(1)


if __name__ == "__main__":
    main()
