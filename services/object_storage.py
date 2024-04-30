import boto3
from botocore.exceptions import ClientError
from core import settings

class ObjectStorage:
    KB = 1024
    MB = 1024 * KB

    SUPPORTED_FILE_TYPES = {
        'image/png': 'png',
        'image/jpeg': 'jpg',
    }

    def __init__(self, settings):
        self.s3 = boto3.resource(
            service_name='s3',
            region_name='eu-north-1',
            aws_access_key_id=settings.AWS_ACCESS_KEY1,
            aws_secret_access_key=settings.AWS_SECRET_KEY1
        )
        self.bucket = self.s3.Bucket('smekteps3')

    async def s3_upload(self, contents: bytes, key: str):
        print(f'Uploading {key} to s3')
        self.bucket.put_object(Key=key, Body=contents)

    async def s3_download(self, key: str):
        try:
            return self.s3.Object(bucket_name='smekteps3', key=key).get()['Body'].read()
        except ClientError as err:
            print(err)

    async def s3_delete(self, key: str):
        try:
            return self.s3.Object('smekteps3', key).delete()
        except ClientError as err:
            print(err)

object_storage_service = ObjectStorage(settings)