from datetime import timedelta
from io import BytesIO

from minio import Minio  # pyright: ignore[reportMissingTypeStubs]
from minio.error import S3Error  # pyright: ignore[reportMissingTypeStubs]
from minio.helpers import ObjectWriteResult  # pyright: ignore[reportMissingTypeStubs]
from urllib3 import BaseHTTPResponse

from .base import BaseS3StorageAdapter


class MinioAdapter(BaseS3StorageAdapter):

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
    ) -> None:

        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )

    def create_bucket(self, bucket_name: str) -> None:

        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
        except S3Error as err:
            if err.code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                pass  # safe to ignore
            else:
                raise

    def is_exists(self, bucket_name: str, object_name: str) -> bool:

        objects = self.client.list_objects(bucket_name, object_name)

        return any(
            obj.object_name == object_name
            for obj in objects
        )

    def get_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires: timedelta,
    ) -> str:

        return self.client.presigned_put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=expires,
        )

    def put(
        self,
        bucket_name: str,
        object_name: str,
        buffer: BytesIO,
        length: int,
        content_type: str
    ) -> ObjectWriteResult:

        return self.client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=buffer,
            length=length,
            content_type=content_type,
        )

    def get(
        self,
        bucket_name: str,
        object_name: str,
    ) -> BaseHTTPResponse | None:

        try:
            return self.client.get_object(
                bucket_name=bucket_name,
                object_name=object_name,
            )
        except S3Error as err:
            if err.code == "NoSuchKey":
                return None
            raise
