from minio import Minio

from app.core.config import settings


def get_minio_client() -> Minio:
    client = Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )

    if not client.bucket_exists(settings.minio_bucket_name):
        client.make_bucket(settings.minio_bucket_name)

    return client
