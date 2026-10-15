"""Source-document artifact storage (Phase 6, contract §3).

Design boundary (§3 / DATA_OPERATIONS_RUNBOOK):
- PostgreSQL keeps Source METADATA and LINEAGE (sources, source_capabilities,
  capability_sources). It is Product Truth and never moves.
- Object storage (Cloud Storage in GCP; local directory in dev) keeps only
  document ARTIFACTS (the governed source documents themselves).

The store returns opaque references (`local://SRC-ID/name` today,
`gs://bucket/prefix/SRC-ID/name` when GCS is configured). References may be
stored in DB text fields later; artifacts never become Product Truth.

GCS driver activates only when google-cloud-storage is installed AND
SOURCE_DOC_BUCKET is set — the shared DEV deployment wires it when service
accounts exist (see PHASE_6_REPORT external-inputs list).
"""

import os
from pathlib import Path
from urllib.parse import quote


class DocNotFound(Exception):
    pass


class LocalDocStore:
    """DEV/driver: filesystem-backed artifact store (stateless app; the
    directory is an external volume in containerised use)."""

    scheme = "local"

    def __init__(self, root):
        self.root = Path(root)

    def put(self, source_id: str, name: str, data: bytes) -> str:
        dest = self._path(source_id, name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return f"local://{quote(source_id)}/{quote(name)}"

    def get(self, ref: str) -> bytes:
        path = self._ref_to_path(ref)
        if not path.is_file():
            raise DocNotFound(ref)
        return path.read_bytes()

    def list(self, source_id: str) -> list[str]:
        d = self.root / source_id
        if not d.is_dir():
            return []
        return sorted(p.name for p in d.iterdir() if p.is_file())

    def delete(self, ref: str) -> None:
        path = self._ref_to_path(ref)
        if path.is_file():
            path.unlink()

    def _path(self, source_id: str, name: str) -> Path:
        return self.root / source_id / name

    def _ref_to_path(self, ref: str) -> Path:
        if not ref.startswith(f"{self.scheme}://"):
            raise DocNotFound(f"unsupported ref scheme: {ref}")
        rel = ref.split("://", 1)[1]
        path = (self.root / rel).resolve()
        if not str(path).startswith(str(self.root.resolve())):
            raise DocNotFound(f"ref escapes store root: {ref}")
        return path


class GcsDocStore:
    """Cloud driver (activated when SOURCE_DOC_BUCKET is set and
    google-cloud-storage is available; wired during DEV deployment)."""

    scheme = "gs"

    def __init__(self, bucket: str, prefix: str = "source-documents"):
        from google.cloud import storage  # optional dependency

        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket)
        self.prefix = prefix.strip("/")

    def _blob(self, source_id: str, name: str):
        return self.bucket.blob(f"{self.prefix}/{source_id}/{name}")

    def put(self, source_id: str, name: str, data: bytes) -> str:
        self._blob(source_id, name).upload_from_string(
            data, content_type="application/octet-stream")
        return f"gs://{self.bucket.name}/{self.prefix}/{quote(source_id)}/{quote(name)}"

    def get(self, ref: str) -> bytes:
        if not ref.startswith(f"{self.scheme}://"):
            raise DocNotFound(f"unsupported ref scheme: {ref}")
        _, _, blob_path = ref.partition("://")
        bucket_name, _, object_name = blob_path.partition("/")
        blob = self.client.bucket(bucket_name).blob(object_name)
        if not blob.exists():
            raise DocNotFound(ref)
        return blob.download_as_bytes()

    def list(self, source_id: str) -> list[str]:
        it = self.client.list_blobs(
            self.bucket, prefix=f"{self.prefix}/{source_id}/")
        return sorted(b.name.rsplit("/", 1)[-1]
                      for b in it if b.name and not b.name.endswith("/"))

    def delete(self, ref: str) -> None:
        _, _, blob_path = ref.partition("://")
        bucket_name, _, object_name = blob_path.partition("/")
        self.client.bucket(bucket_name).blob(object_name).delete()


def from_env() -> LocalDocStore | GcsDocStore:
    """Choose the driver from the environment (Cloud Run contract §15)."""
    bucket = os.environ.get("SOURCE_DOC_BUCKET")
    if bucket:
        return GcsDocStore(bucket, os.environ.get("SOURCE_DOC_PREFIX", "source-documents"))
    return LocalDocStore(os.environ.get(
        "SOURCE_DOC_LOCAL_DIR", "./data/source-documents"))
