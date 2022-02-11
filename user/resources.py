
import boto3
from django.conf import settings
# from config import S3_BUCKET, S3_KEY, S3_SECRET
# from flask import session
from botocore.exceptions import ClientError
# from flask_login import current_user


def _get_s3_resource(request):
    current_user = request.user
    if settings.S3_KEY and settings.S3_SECRET:
        return boto3.resource(
            's3',
            aws_access_key_id=settings.S3_KEY,
            aws_secret_access_key=settings.S3_SECRET
        )
    else:
        return boto3.resource('s3')


def get_bucket(request):
    current_user = request.user
    # s3_resource = _get_s3_resource()
    s3_res = boto3.resource('s3')
    # user = User.query.get_or_404(current_user.id)

    return s3_res.Bucket(current_user.profile.bucket_name)

def get_bucket_v2(request):
    current_user = request.user
    get_last_modified = lambda obj: int(obj['LastModified'].timestamp())

    s3 = boto3.client('s3')

    objs = s3.list_objects_v2(Bucket=current_user.profile.bucket_name)['KeyCount']
    if objs != 0:
        objects = s3.list_objects_v2(Bucket=current_user.profile.bucket_name)['Contents']
        return sorted(objects, key=get_last_modified, reverse=True)
    else:
        files = {}
        return files



# def get_bucket_size(request):
#     size_byte=0
#     current_user = request.user
#     bucket_name = current_user.profile.bucket_name
#     s3_res = boto3.resource('s3')
#     bucket = s3_res.Bucket(bucket_name)
#     for my_bucket_object in bucket.objects.all():
#         print(my_bucket_object.key)
#         size_byte=size_byte + my_bucket_object.size
#     return size_byte


    
# get_bucket_size()

def get_buckets_list(request):
    current_user = request.user
    client = boto3.client('s3')
    return client.list_buckets().get('Buckets')

def create_s3_bucket(bucket_name):
    s3_res = boto3.resource('s3')
    try:
        rsp = s3_res.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
        'LocationConstraint': 'ap-south-1'})
    except ClientError as err:
        print(err)
        return False
    return True

