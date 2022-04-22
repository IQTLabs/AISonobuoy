"""Provides simplified and documented methods for interacting with AWS S3.
"""
import logging

import boto3


root = logging.getLogger()
if not root.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    root.addHandler(ch)

logger = logging.getLogger("S3Utilities")
logger.setLevel(logging.INFO)


def create_bucket(bucket, region="us-east-1"):
    """Creates a new S3 bucket.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.create_bucket

    Request Syntax
    --------------
    response = client.create_bucket(
        ACL='private'|'public-read'|'public-read-write'|'authenticated-read',
        Bucket='string',
        CreateBucketConfiguration={
            'LocationConstraint': 'af-south-1'|'ap-east-1'|'ap-northeast-1'|'ap-northeast-2'|'ap-northeast-3'|'ap-south-1'|'ap-southeast-1'|'ap-southeast-2'|'ca-central-1'|'cn-north-1'|'cn-northwest-1'|'EU'|'eu-central-1'|'eu-north-1'|'eu-south-1'|'eu-west-1'|'eu-west-2'|'eu-west-3'|'me-south-1'|'sa-east-1'|'us-east-2'|'us-gov-east-1'|'us-gov-west-1'|'us-west-1'|'us-west-2'
        },
        GrantFullControl='string',
        GrantRead='string',
        GrantReadACP='string',
        GrantWrite='string',
        GrantWriteACP='string',
        ObjectLockEnabledForBucket=True|False
    )

    Response Syntax
    ---------------
    {
        'Location': 'string'
    }

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket
    region : str
        Region in which the S3 bucket resides

    Returns
    -------
    response : obj
        A requests.Response object

    """
    client = boto3.client("s3")
    try:
        if region == "us-east-1":
            response = client.create_bucket(
                Bucket=bucket,
            )
        else:
            response = client.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={
                    "LocationConstraint": region,
                },
            )
        logger.info(f"Bucket {bucket} has been created in region {region}")
    except Exception as e:
        logger.error(f"Could not create bucket {bucket} in region {region}: {e}")
    return response


def put_object(file_obj, bucket, key):
    """Adds an object to a bucket.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_object

    Request Syntax
    --------------
    response = client.put_object(
        ACL='private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control',
        Body=b'bytes'|file,
        Bucket='string',
        CacheControl='string',
        ContentDisposition='string',
        ContentEncoding='string',
        ContentLanguage='string',
        ContentLength=123,
        ContentMD5='string',
        ContentType='string',
        Expires=datetime(2015, 1, 1),
        GrantFullControl='string',
        GrantRead='string',
        GrantReadACP='string',
        GrantWriteACP='string',
        Key='string',
        Metadata={
            'string': 'string'
        },
        ServerSideEncryption='AES256'|'aws:kms',
        StorageClass='STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE'|'OUTPOSTS',
        WebsiteRedirectLocation='string',
        SSECustomerAlgorithm='string',
        SSECustomerKey='string',
        SSEKMSKeyId='string',
        SSEKMSEncryptionContext='string',
        BucketKeyEnabled=True|False,
        RequestPayer='requester',
        Tagging='string',
        ObjectLockMode='GOVERNANCE'|'COMPLIANCE',
        ObjectLockRetainUntilDate=datetime(2015, 1, 1),
        ObjectLockLegalHoldStatus='ON'|'OFF',
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    {
        'Expiration': 'string',
        'ETag': 'string',
        'ServerSideEncryption': 'AES256'|'aws:kms',
        'VersionId': 'string',
        'SSECustomerAlgorithm': 'string',
        'SSECustomerKeyMD5': 'string',
        'SSEKMSKeyId': 'string',
        'SSEKMSEncryptionContext': 'string',
        'BucketKeyEnabled': True|False,
        'RequestCharged': 'requester'
    }

    Parameters
    ----------
    file_obj : obj
        A file object opened read binary
    bucket : str
        Name of the S3 bucket
    key : str
        Name of the key for the file

    Returns
    -------
    response : obj
        A requests.Response object

    """
    response = None
    s3 = boto3.resource("s3")
    try:
        s3.Object(bucket, key).load()
        logger.info(f"Key {key} exists in bucket {bucket}")
        return
    except Exception as e:
        if e.response["Error"]["Code"] == "404":
            try:
                client = boto3.client("s3")
                response = client.put_object(
                    Body=file_obj,
                    Bucket=bucket,
                    Key=key,
                )
                logger.info(f"Put key {key} to bucket {bucket}")
            except Exception as e:
                logger.info(f"Could not put key {key} to bucket {bucket}: {e}")
        else:
            logger.error(f"Could not load key {key} from bucket {bucket}: {e}")
    return response


def create_multipart_upload(bucket, key):
    """This action initiates a multipart upload and returns an upload
    ID.

    This upload ID is used to associate all of the parts in the
    specific multipart upload. You specify this upload ID in each of
    your subsequent upload part requests (see UploadPart ). You also
    include this upload ID in the final request to either complete or
    abort the multipart upload request.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.create_multipart_upload

    Request Syntax
    --------------
    response = client.create_multipart_upload(
        ACL='private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control',
        Bucket='string',
        CacheControl='string',
        ContentDisposition='string',
        ContentEncoding='string',
        ContentLanguage='string',
        ContentType='string',
        Expires=datetime(2015, 1, 1),
        GrantFullControl='string',
        GrantRead='string',
        GrantReadACP='string',
        GrantWriteACP='string',
        Key='string',
        Metadata={
            'string': 'string'
        },
        ServerSideEncryption='AES256'|'aws:kms',
        StorageClass='STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE'|'OUTPOSTS',
        WebsiteRedirectLocation='string',
        SSECustomerAlgorithm='string',
        SSECustomerKey='string',
        SSEKMSKeyId='string',
        SSEKMSEncryptionContext='string',
        BucketKeyEnabled=True|False,
        RequestPayer='requester',
        Tagging='string',
        ObjectLockMode='GOVERNANCE'|'COMPLIANCE',
        ObjectLockRetainUntilDate=datetime(2015, 1, 1),
        ObjectLockLegalHoldStatus='ON'|'OFF',
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    {
        'AbortDate': datetime(2015, 1, 1),
        'AbortRuleId': 'string',
        'Bucket': 'string',
        'Key': 'string',
        'UploadId': 'string',
        'ServerSideEncryption': 'AES256'|'aws:kms',
        'SSECustomerAlgorithm': 'string',
        'SSECustomerKeyMD5': 'string',
        'SSEKMSKeyId': 'string',
        'SSEKMSEncryptionContext': 'string',
        'BucketKeyEnabled': True|False,
        'RequestCharged': 'requester'
    }

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket
    key : str
        Name of the key for the multipart upload

    Returns
    -------
    response : obj
        A requests.Response object

    """
    response = None
    s3 = boto3.resource("s3")
    try:
        s3.Object(bucket, key).load()
        logger.info(f"Key {key} exists in bucket {bucket}")
        return
    except Exception as e:
        if e.response["Error"]["Code"] == "404":
            client = boto3.client("s3")
            try:
                response = client.create_multipart_upload(
                    Bucket=bucket,
                    Key=key,
                )
                logger.info(
                    f"Created multipart upload {response['UploadId']} for key {key} in bucket {bucket}"
                )
            except Exception as e:
                logger.error(
                    f"Could not create a multipart upload for key {key} in bucket {bucket}: {e}"
                )
        else:
            logger.error(f"Could not load key {key} from bucket {bucket}: {e}")
    return response


def upload_part(file_obj, bucket, key, part_number, upload_id):
    """Uploads a part in a multipart upload.

    You must initiate a multipart upload (see CreateMultipartUpload )
    before you can upload any part. In response to your initiate
    request, Amazon S3 returns an upload ID, a unique identifier, that
    you must include in your upload part request.

    Part numbers can be any number from 1 to 10,000, inclusive. A part
    number uniquely identifies a part and also defines its position
    within the object being created. If you upload a new part using
    the same part number that was used with a previous part, the
    previously uploaded part is overwritten. Each part must be at
    least 5 MB in size, except the last part. There is no size limit
    on the last part of your multipart upload.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_part

    Request Syntax
    --------------
    response = client.upload_part(
        Body=b'bytes'|file,
        Bucket='string',
        ContentLength=123,
        ContentMD5='string',
        Key='string',
        PartNumber=123,
        UploadId='string',
        SSECustomerAlgorithm='string',
        SSECustomerKey='string',
        RequestPayer='requester',
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    {
        'ServerSideEncryption': 'AES256'|'aws:kms',
        'ETag': 'string',
        'SSECustomerAlgorithm': 'string',
        'SSECustomerKeyMD5': 'string',
        'SSEKMSKeyId': 'string',
        'BucketKeyEnabled': True|False,
        'RequestCharged': 'requester'
    }


    Parameters
    ----------
    file_obj : obj
        A file object opened read binary
    bucket : str
        Name of the S3 bucket
    key : str
        Name of the key for the multipart upload
    part_number : int
        The unique number for this part
    upload_id : str
        The unique identifier returned on creation of the multipart upload

    Returns
    -------
    response : obj
        A requests.Response object

    """
    client = boto3.client("s3")
    try:
        response = client.upload_part(
            Body=file_obj,
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
            PartNumber=part_number,
        )
        logger.info(
            f"Uploaded part {part_number} of multipart upload {upload_id} of key {key} to bucket {bucket}"
        )
    except Exception as e:
        logger.error(
            f"Could not upload part {part_number} of multipart upload {upload_id} of key {key} to bucket {bucket}: {e}"
        )
    return response


def complete_multipart_upload(bucket, key, multipart_upload, upload_id):
    """Completes a multipart upload by assembling previously uploaded parts.

    You first initiate the multipart upload and then upload all parts
    using the UploadPart operation. After successfully uploading all
    relevant parts of an upload, you call this action to complete the
    upload. Upon receiving this request, Amazon S3 concatenates all
    the parts in ascending order by part number to create a new
    object. In the Complete Multipart Upload request, you must provide
    the parts list. You must ensure that the parts list is
    complete. This action concatenates the parts that you provide in
    the list. For each part in the list, you must provide the part
    number and the ETag value, returned after that part was uploaded.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.complete_multipart_upload

    Request Syntax
    --------------
    response = client.complete_multipart_upload(
        Bucket='string',
        Key='string',
        MultipartUpload={
            'Parts': [
                {
                    'ETag': 'string',
                    'PartNumber': 123
                },
            ]
        },
        UploadId='string',
        RequestPayer='requester',
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    {
        'Location': 'string',
        'Bucket': 'string',
        'Key': 'string',
        'Expiration': 'string',
        'ETag': 'string',
        'ServerSideEncryption': 'AES256'|'aws:kms',
        'VersionId': 'string',
        'SSEKMSKeyId': 'string',
        'BucketKeyEnabled': True|False,
        'RequestCharged': 'requester'
    }

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket
    key : str
        Name of the key for the multipart upload
    multipart_upload : dict
        MD5 hex digests and part numbers to assemble
    upload_id : str
        The unique identifier returned on creation of the multipart upload

    Returns
    -------
    response : obj
        A requests.Response object

    """
    client = boto3.client("s3")
    try:
        response = client.complete_multipart_upload(
            Bucket=bucket,
            Key=key,
            MultipartUpload=multipart_upload,
            UploadId=upload_id,
        )
        logger.info(
            f"Completed multipart upload {upload_id} for key {key} in bucket {bucket}"
        )
    except Exception as e:
        logger.error(
            f"Could not complete multipart upload {upload_id} for key {key} in bucket {bucket}: {e}"
        )
    return response


def abort_multipart_upload(bucket, key, upload_id):
    """This action aborts a multipart upload.

    After a multipart upload is aborted, no additional parts can be
    uploaded using that upload ID. The storage consumed by any
    previously uploaded parts will be freed. However, if any part
    uploads are currently in progress, those part uploads might or
    might not succeed. As a result, it might be necessary to abort a
    given multipart upload multiple times in order to completely free
    all storage consumed by all parts.

    To verify that all parts have been removed, so you don't get
    charged for the part storage, you should call the ListParts action
    and ensure that the parts list is empty.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.abort_multipart_upload

    Request Syntax
    --------------
    response = client.abort_multipart_upload(
        Bucket='string',
        Key='string',
        UploadId='string',
        RequestPayer='requester',
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    {
        'RequestCharged': 'requester'
    }

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket
    key : str
        Name of the key for the multipart upload
    upload_id : str
        The unique identifier returned on creation of the multipart upload

    Returns
    -------
    response : obj
        A requests.Response object

    """
    client = boto3.client("s3")
    try:
        response = client.abort_multipart_upload(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
        )
        logger.info(
            f"Aborted multipart upload {upload_id} for key {key} in bucket {bucket}"
        )
    except Exception as e:
        logger.error(
            f"Could not abort multipart upload {upload_id} for key {key} in bucket {bucket}: {e}"
        )
    return response


def list_parts(bucket, key, upload_id):
    """Lists the parts that have been uploaded for a specific multipart upload.

    This operation must include the upload ID, which you obtain by
    sending the initiate multipart upload request (see
    CreateMultipartUpload ). This request returns a maximum of 1,000
    uploaded parts. The default number of parts returned is 1,000
    parts. You can restrict the number of parts returned by specifying
    the max-parts request parameter. If your multipart upload consists
    of more than 1,000 parts, the response returns an IsTruncated
    field with the value of true, and a NextPartNumberMarker
    element. In subsequent ListParts requests you can include the
    part-number-marker query string parameter and set its value to the
    NextPartNumberMarker field value from the previous response.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_parts

    Request Syntax
    --------------
    response = client.list_parts(
        Bucket='string',
        Key='string',
        MaxParts=123,
        PartNumberMarker=123,
        UploadId='string',
        RequestPayer='requester',
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    {
        'AbortDate': datetime(2015, 1, 1),
        'AbortRuleId': 'string',
        'Bucket': 'string',
        'Key': 'string',
        'UploadId': 'string',
        'PartNumberMarker': 123,
        'NextPartNumberMarker': 123,
        'MaxParts': 123,
        'IsTruncated': True|False,
        'Parts': [
            {
                'PartNumber': 123,
                'LastModified': datetime(2015, 1, 1),
                'ETag': 'string',
                'Size': 123
            },
        ],
        'Initiator': {
            'ID': 'string',
            'DisplayName': 'string'
        },
        'Owner': {
            'DisplayName': 'string',
            'ID': 'string'
        },
        'StorageClass': 'STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE'|'OUTPOSTS',
        'RequestCharged': 'requester'
    }

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket
    key : str
        Name of the key for the multipart upload
    upload_id : str
        The unique identifier returned on creation of the multipart upload

    Returns
    -------
    response : obj
        A requests.Response object

    """
    client = boto3.client("s3")
    try:
        response = client.list_parts(
            Bucket=bucket,
            Key=key,
            UploadId=upload_id,
        )
        logger.info(
            f"Listed parts for multipart upload {upload_id} for key {key} in bucket {bucket}"
        )
    except Exception as e:
        logger.error(
            f"Could not list parts for multipart upload {upload_id} for key {key} in bucket {bucket}: {e}"
        )
    return response


def list_objects(bucket, prefix=None):
    """Returns some or all (up to 1,000) of the objects in a bucket.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects

    Request Syntax
    --------------
    response = client.list_objects(
        Bucket='string',
        Delimiter='string',
        EncodingType='url',
        Marker='string',
        MaxKeys=123,
        Prefix='string',
        RequestPayer='requester',
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    {
        'IsTruncated': True|False,
        'Marker': 'string',
        'NextMarker': 'string',
        'Contents': [
            {
                'Key': 'string',
                'LastModified': datetime(2015, 1, 1),
                'ETag': 'string',
                'ChecksumAlgorithm': [
                    'CRC32'|'CRC32C'|'SHA1'|'SHA256',
                ],
                'Size': 123,
                'StorageClass': 'STANDARD'|'REDUCED_REDUNDANCY'|'GLACIER'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'DEEP_ARCHIVE'|'OUTPOSTS'|'GLACIER_IR',
                'Owner': {
                    'DisplayName': 'string',
                    'ID': 'string'
                }
            },
        ],
        'Name': 'string',
        'Prefix': 'string',
        'Delimiter': 'string',
        'MaxKeys': 123,
        'CommonPrefixes': [
            {
                'Prefix': 'string'
            },
        ],
        'EncodingType': 'url'
    }    

    TODO: Update
    Parameters
    ----------
    bucket : str
        Name of the S3 bucket

    Returns
    -------
    response : obj
        A requests.Response object
    """
    client = boto3.client("s3")
    try:
        if prefix is None:
            response = client.list_objects(Bucket=bucket)
        else:
            response = client.list_objects(Bucket=bucket, Prefix=prefix)
        logger.info(f"Listed objects from bucket {bucket}")
    except Exception as e:
        logger.info(f"Could not list objects from bucket {bucket}: {e}")
    return response


def get_object(bucket, key):
    """Retrieves objects from Amazon S3.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.get_object

    Request Syntax
    --------------
    response = client.get_object(
        Bucket='string',
        IfMatch='string',
        IfModifiedSince=datetime(2015, 1, 1),
        IfNoneMatch='string',
        IfUnmodifiedSince=datetime(2015, 1, 1),
        Key='string',
        Range='string',
        ResponseCacheControl='string',
        ResponseContentDisposition='string',
        ResponseContentEncoding='string',
        ResponseContentLanguage='string',
        ResponseContentType='string',
        ResponseExpires=datetime(2015, 1, 1),
        VersionId='string',
        SSECustomerAlgorithm='string',
        SSECustomerKey='string',
        RequestPayer='requester',
        PartNumber=123,
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    {
        'Body': StreamingBody(),
        'DeleteMarker': True|False,
        'AcceptRanges': 'string',
        'Expiration': 'string',
        'Restore': 'string',
        'LastModified': datetime(2015, 1, 1),
        'ContentLength': 123,
        'ETag': 'string',
        'MissingMeta': 123,
        'VersionId': 'string',
        'CacheControl': 'string',
        'ContentDisposition': 'string',
        'ContentEncoding': 'string',
        'ContentLanguage': 'string',
        'ContentRange': 'string',
        'ContentType': 'string',
        'Expires': datetime(2015, 1, 1),
        'WebsiteRedirectLocation': 'string',
        'ServerSideEncryption': 'AES256'|'aws:kms',
        'Metadata': {
            'string': 'string'
        },
        'SSECustomerAlgorithm': 'string',
        'SSECustomerKeyMD5': 'string',
        'SSEKMSKeyId': 'string',
        'BucketKeyEnabled': True|False,
        'StorageClass': 'STANDARD'|'REDUCED_REDUNDANCY'|'STANDARD_IA'|'ONEZONE_IA'|'INTELLIGENT_TIERING'|'GLACIER'|'DEEP_ARCHIVE'|'OUTPOSTS',
        'RequestCharged': 'requester',
        'ReplicationStatus': 'COMPLETE'|'PENDING'|'FAILED'|'REPLICA',
        'PartsCount': 123,
        'TagCount': 123,
        'ObjectLockMode': 'GOVERNANCE'|'COMPLIANCE',
        'ObjectLockRetainUntilDate': datetime(2015, 1, 1),
        'ObjectLockLegalHoldStatus': 'ON'|'OFF'
    }

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket
    key : str
        Name of the key for the file

    Returns
    -------
    response : obj
        A requests.Response object

    """
    client = boto3.client("s3")
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        logger.info(f"Got key {key} from bucket {bucket}")
    except Exception as e:
        logger.info(f"Could not get key {key} from bucket {bucket}: {e}")
    return response


def download_object(download_path, bucket, s3_object):
    """Download an object from an AWS S3 bucket to a local path.

    Parameters
    ----------
    download_path : pathlib.Path()
        The local path to which to download objects
    bucket : str
        The AWS S3 bucket
    s3_object : dict
        The AWS S3 object

    Returns
    -------
    etag : str
        The ETag of the AWS S3 object

    Note that AWS S3 objects contain an ETag which is either an MD5
    sum of the file, or an MD5 sum of the concatenated MD5 sums of
    chunks of the file followed by a hypen and the number of chunks.

    See:
    https://zihao.me/post/calculating-etag-for-aws-s3-objects/
    https://botocore.amazonaws.com/v1/documentation/api/latest/reference/response.html
    """
    if "-" in s3_object["ETag"]:
        is_hyphenated = True
        md5s = []
        chunk_size = 8 * 1024 * 1024
    else:
        is_hyphenated = False
        md5 = hashlib.md5()
        chunk_size = 1024 * 1024
    key = s3_object["Key"]
    r = get_object(bucket, key)
    with open(download_path / key, "wb") as f:
        for chunk in r["Body"].iter_chunks(chunk_size=chunk_size):
            f.write(chunk)
            if is_hyphenated:
                md5s.append(hashlib.md5(chunk).digest())
            else:
                md5.update(chunk)
    if is_hyphenated:
        md5 = hashlib.md5(b"".join(md5s))
        etag = f"{md5.hexdigest()}-{len(md5s)}"
    else:
        etag = md5.hexdigest()
    return etag


def delete_object(bucket, key):
    """Removes the null version (if there is one) of an object and
    inserts a delete marker, which becomes the latest version of the
    object.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object

    Request Syntax
    --------------
    response = client.delete_object(
        Bucket='string',
        Key='string',
        MFA='string',
        VersionId='string',
        RequestPayer='requester',
        BypassGovernanceRetention=True|False,
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    {
        'DeleteMarker': True|False,
        'VersionId': 'string',
        'RequestCharged': 'requester'
    }

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket
    key : str
        Name of the key for the file

    Returns
    -------
    response : obj
        A requests.Response object

    """
    client = boto3.client("s3")
    try:
        response = client.delete_object(
            Bucket=bucket,
            Key=key,
        )
        logger.info(f"Deleted key {key} from bucket {bucket}")
    except Exception as e:
        logger.error(f"Could not delete key {key} from bucket {bucket}: {e}")
    return response


def delete_bucket(bucket):
    """Deletes the S3 bucket.

    See:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_bucket

    Request Syntax
    --------------
    response = client.delete_bucket(
        Bucket='string',
        ExpectedBucketOwner='string'
    )

    Response Syntax
    ---------------
    None

    Parameters
    ----------
    bucket : str
        Name of the S3 bucket

    Returns
    -------
    response : obj
        A requests.Response object

    """
    client = boto3.client("s3")
    try:
        response = client.delete_bucket(
            Bucket=bucket,
        )
        logger.error(f"Deleted bucket {bucket}")
    except Exception as e:
        logger.error(f"Could not delete bucket {bucket}: {e}")
    return response
