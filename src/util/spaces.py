"""
This file contains helper methods for accessing all
files in DigitalOcean Spaces (used to store files in prod).

To use this file, you will need a DigitalOcean Space,
along with a Spaces API Key and Secret, which have to
be set as environment variables having names of
SPACES_ACCESS_KEY and SPACES_SECRET_KEY respectively.

Also set your space name and space region (default nyc3)
as environment variables with names SPACES_SPACE_NAME and
SPACES_SPACE_REGION respectively.
"""
import boto3
from os import getenv as env


SPACE_NAME = env("SPACES_SPACE_NAME")
SPACE_REGION = env("SPACES_SPACE_REGION")
ACCESS = env("SPACES_ACCESS_KEY")
SECRET = env("SPACES_SECRET_KEY")


def create_client():
    return boto3.session.Session().client("s3", SPACE_REGION,
                                          endpoint_url=f"https://{SPACE_REGION}.digitaloceanspaces.com",
                                          aws_access_key_id=ACCESS, aws_secret_access_key=SECRET)


def list_files(subdir: str = ""):
    pass
