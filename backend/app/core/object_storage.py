"""S3-compatible object storage helpers."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


class ObjectStorageError(RuntimeError):
    """Raised when an object storage operation fails."""


@dataclass
class StoredObject:
    key: str
    bucket: str
    provider: str
    size: int
    content_type: str
    etag: Optional[str] = None

    @property
    def uri(self) -> str:
        return make_object_uri(self.bucket, self.key)


def _safe_segment(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._/-]", "-", value.strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    return cleaned.strip("/") or "object"


def _safe_extension(filename: str, fallback: str = "bin") -> str:
    suffix = Path(filename).suffix.lower().lstrip(".")
    return suffix or fallback


def make_object_uri(bucket: str, key: str) -> str:
    return f"object://{bucket}/{key}"


def parse_object_uri(uri: Optional[str]) -> tuple[str, str] | None:
    if not uri or not uri.startswith("object://"):
        return None
    payload = uri[len("object://") :]
    if "/" not in payload:
        return None
    bucket, key = payload.split("/", 1)
    if not bucket or not key:
        return None
    return bucket, key


def build_storage_key(*parts: str, filename: Optional[str] = None, sha256: Optional[str] = None) -> str:
    segments = [_safe_segment(part) for part in parts if part]
    if filename:
        ext = _safe_extension(filename)
        if sha256:
            segments.append(f"{sha256}.{ext}")
        else:
            segments.append(_safe_segment(filename))
    elif sha256:
        segments.append(sha256)

    prefix = settings.OBJECT_STORAGE_BASE_PREFIX.strip("/")
    full_segments = [prefix] if prefix else []
    full_segments.extend(segments)
    return "/".join(segment for segment in full_segments if segment)


def build_skill_object_key(skill_id: int, version: str, sha256: str, filename: str) -> str:
    return build_storage_key("skills", str(skill_id), version, filename=filename, sha256=sha256)


def build_knowledge_object_key(
    agent_id: int,
    knowledge_file_id: int,
    sha256: str,
    filename: str,
) -> str:
    return build_storage_key(
        "knowledge",
        str(agent_id),
        str(knowledge_file_id),
        filename=filename,
        sha256=sha256,
    )


def build_playwright_screenshot_key(
    session_id: str,
    execution_id: str,
    sha256: str,
    image_format: str = "png",
) -> str:
    filename = f"screenshot.{image_format}"
    return build_storage_key(
        "playwright",
        "screenshots",
        session_id,
        execution_id,
        filename=filename,
        sha256=sha256,
    )


def build_marketplace_media_key(owner_hint: str, sha256: str, filename: str) -> str:
    return build_storage_key("marketplace", "media", owner_hint, filename=filename, sha256=sha256)


class S3ObjectStorageClient:
    """S3-compatible object storage client (works with AWS S3 and MinIO)."""

    def __init__(self) -> None:
        self.provider = settings.OBJECT_STORAGE_PROVIDER
        self.bucket = settings.OBJECT_STORAGE_BUCKET
        self.endpoint_url = settings.OBJECT_STORAGE_ENDPOINT_URL
        self.region = settings.OBJECT_STORAGE_REGION
        self.access_key = settings.OBJECT_STORAGE_ACCESS_KEY_ID
        self.secret_key = settings.OBJECT_STORAGE_SECRET_ACCESS_KEY
        self.auto_create_bucket = settings.OBJECT_STORAGE_AUTO_CREATE_BUCKET
        self.signed_url_ttl = settings.OBJECT_STORAGE_SIGNED_URL_TTL_SECONDS
        self.available = all(
            [
                self.provider.lower() == "s3",
                bool(self.bucket),
                bool(self.access_key),
                bool(self.secret_key),
            ]
        )
        self._bucket_ready = False
        self._bucket_lock = asyncio.Lock()

        if not self.available:
            self._client = None
            return

        config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "path" if settings.OBJECT_STORAGE_FORCE_PATH_STYLE else "auto"},
        )
        self._client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            use_ssl=settings.OBJECT_STORAGE_USE_SSL,
            config=config,
        )

    async def _run(self, fn, *args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)

    async def ensure_bucket(self) -> None:
        if not self.available or not self._client:
            raise ObjectStorageError("Object storage is not configured.")
        if self._bucket_ready:
            return

        async with self._bucket_lock:
            if self._bucket_ready:
                return

            try:
                await self._run(self._client.head_bucket, Bucket=self.bucket)
            except ClientError as exc:
                error_code = (exc.response or {}).get("Error", {}).get("Code")
                missing_bucket = error_code in {"404", "NoSuchBucket", "NotFound"}
                if missing_bucket and self.auto_create_bucket:
                    logger.info("Object storage bucket '%s' missing; creating it.", self.bucket)
                    create_kwargs: dict[str, Any] = {"Bucket": self.bucket}
                    if self.region and self.region != "us-east-1":
                        create_kwargs["CreateBucketConfiguration"] = {
                            "LocationConstraint": self.region
                        }
                    await self._run(self._client.create_bucket, **create_kwargs)
                else:
                    raise ObjectStorageError(f"Unable to access bucket '{self.bucket}': {exc}") from exc
            except (BotoCoreError, Exception) as exc:  # noqa: BLE001
                raise ObjectStorageError(f"Unable to initialize object storage bucket: {exc}") from exc

            self._bucket_ready = True

    async def put_object_bytes(
        self,
        *,
        key: str,
        data: bytes,
        content_type: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> StoredObject:
        await self.ensure_bucket()
        try:
            response = await self._run(
                self._client.put_object,
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                Metadata=metadata or {},
            )
        except (BotoCoreError, ClientError, Exception) as exc:  # noqa: BLE001
            raise ObjectStorageError(f"Failed to upload object '{key}': {exc}") from exc

        return StoredObject(
            key=key,
            bucket=self.bucket,
            provider="s3",
            size=len(data),
            content_type=content_type,
            etag=(response.get("ETag") or "").strip('"') or None,
        )

    async def get_object_bytes(self, key: str) -> bytes:
        await self.ensure_bucket()
        try:
            response = await self._run(self._client.get_object, Bucket=self.bucket, Key=key)
            body = response["Body"]
            return await self._run(body.read)
        except (BotoCoreError, ClientError, Exception) as exc:  # noqa: BLE001
            raise ObjectStorageError(f"Failed to read object '{key}': {exc}") from exc

    async def delete_object(self, key: str) -> None:
        await self.ensure_bucket()
        try:
            await self._run(self._client.delete_object, Bucket=self.bucket, Key=key)
        except (BotoCoreError, ClientError, Exception) as exc:  # noqa: BLE001
            raise ObjectStorageError(f"Failed to delete object '{key}': {exc}") from exc

    async def object_exists(self, key: str) -> bool:
        await self.ensure_bucket()
        try:
            await self._run(self._client.head_object, Bucket=self.bucket, Key=key)
            return True
        except ClientError as exc:
            code = (exc.response or {}).get("Error", {}).get("Code")
            if code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise ObjectStorageError(f"Failed to check object '{key}': {exc}") from exc
        except (BotoCoreError, Exception) as exc:  # noqa: BLE001
            raise ObjectStorageError(f"Failed to check object '{key}': {exc}") from exc

    async def generate_signed_url(self, key: str, ttl_seconds: Optional[int] = None) -> str:
        await self.ensure_bucket()
        expires = ttl_seconds or self.signed_url_ttl
        try:
            return await self._run(
                self._client.generate_presigned_url,
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires,
            )
        except (BotoCoreError, ClientError, Exception) as exc:  # noqa: BLE001
            raise ObjectStorageError(f"Failed to create signed URL for '{key}': {exc}") from exc


_object_storage_client = S3ObjectStorageClient()


def get_object_storage_client() -> S3ObjectStorageClient:
    return _object_storage_client


async def initialize_object_storage() -> None:
    client = get_object_storage_client()
    if not client.available:
        logger.warning(
            "Object storage is not fully configured; upload endpoints will return controlled errors."
        )
        return

    try:
        await client.ensure_bucket()
        logger.info("Object storage bucket '%s' is ready.", client.bucket)
    except ObjectStorageError as exc:
        logger.warning("Object storage initialization failed: %s", exc)
