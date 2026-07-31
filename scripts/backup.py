#!/usr/bin/env python3
"""
SQLite backup to Cloudflare R2 with grandfather-father-son retention.

Usage:
    python scripts/backup.py daily     — daily backup, retains 3 days
    python scripts/backup.py weekly    — weekly backup, retains 4 weeks
    python scripts/backup.py monthly   — monthly backup, retains 2 months

Required environment variables (set in Coolify):
    R2_ACCESS_KEY_ID        — R2 API access key
    R2_SECRET_ACCESS_KEY    — R2 API secret
    R2_ENDPOINT_URL         — https://<account_id>.r2.cloudflarestorage.com
    R2_BUCKET               — bucket name (e.g. "nurturedstory-backups")

Scheduled via Coolify Scheduled Tasks:
    daily   — 0 3 * * *      (3am UTC every day)
    weekly  — 0 4 * * 0      (4am UTC Sunday)
    monthly — 0 5 1 * *      (5am UTC 1st of month)
"""

import os
import sys
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
from botocore.config import Config


DB_PATH = Path("/app/data/db.sqlite3")

# Retention days per cadence
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


def snapshot_db(dest_path: Path) -> None:
    """Take a live snapshot of the SQLite DB using the online backup API."""
    with sqlite3.connect(DB_PATH) as source, sqlite3.connect(dest_path) as dest:
        source.backup(dest)


def upload_to_r2(client, bucket: str, local_path: Path, key: str) -> None:
    client.upload_file(str(local_path), bucket, key)


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

    # S3 delete_objects accepts up to 1000 keys per request
    for i in range(0, len(to_delete), 1000):
        batch = to_delete[i:i + 1000]
        client.delete_objects(Bucket=bucket, Delete={"Objects": batch})
        for item in batch:
            log(f"Pruned old backup: {item['Key']}")


def main() -> None:
    cadence = sys.argv[1] if len(sys.argv) > 1 else "daily"
    if cadence not in RETENTION:
        log(f"ERROR: unknown cadence '{cadence}' (expected daily|weekly|monthly)")
        sys.exit(1)

    log(f"Starting {cadence} backup")

    if not DB_PATH.exists():
        log(f"ERROR: database not found at {DB_PATH}")
        sys.exit(1)

    access_key = get_env("R2_ACCESS_KEY_ID")
    secret_key = get_env("R2_SECRET_ACCESS_KEY")
    endpoint   = get_env("R2_ENDPOINT_URL")
    bucket     = get_env("R2_BUCKET")

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        # R2 uses "auto" region — required by the boto3 signature
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    key = f"{cadence}/db-{timestamp}.sqlite3"

    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        snapshot_db(tmp_path)
        upload_to_r2(client, bucket, tmp_path, key)
        log(f"Uploaded to s3://{bucket}/{key}")

        prune_old_backups(client, bucket, cadence, RETENTION[cadence])
    finally:
        tmp_path.unlink(missing_ok=True)

    log("Backup complete")


if __name__ == "__main__":
    main()
