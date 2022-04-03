import boto3
from django.conf import settings
from botocore.exceptions import ClientError

def get_bucket(request):
    current_user = request.user
    s3_res = boto3.resource('s3')

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

