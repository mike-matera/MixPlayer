"""
Models for the MixPlayer
"""

import binascii
import datetime
import logging
import struct
import tempfile
import urllib.parse

import requests
from google.cloud import storage

bucket_name = "erratic-pleasure.appspot.com"
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)


class CachedImage:
    """This is a model the represents a GCS cached image."""

    def __init__(self, url):
        global bucket
        # The old versions used crc32 incorrectly creating broken filenames.
        # This hack makes current versions generate compatible names.
        raw = binascii.crc32(url.encode())
        signed = struct.unpack("i", struct.pack("I", raw & 0xFFFFFFFF))
        image_name = f"cached_images/image-{signed[0]:08x}"

        blob = bucket.get_blob(image_name)
        if blob is None:
            with tempfile.NamedTemporaryFile() as tf:
                r = requests.get(url, allow_redirects=True)
                tf.write(r.content)
                tf.flush()

                blob = bucket.blob(image_name)
                blob.upload_from_filename(tf.name)
                blob.make_public()

        self.url = f"https://storage.googleapis.com/{blob.bucket.name}/{image_name}"


class MixFile:
    """This is a model that represents a GCS mix file."""

    def __init__(self, blob):
        self.blob = blob

        # In case metadata has extra spaces.
        metadata = {k.strip(): v for k, v in self.blob.metadata.items()}
        assert "Image" in metadata, "No Image tag"
        assert "Date" in metadata, "No Date tag"

        self.title = metadata.get("Title", self.blob.name)
        self.comment = metadata.get("Comment", "")
        self.date = datetime.datetime.strptime(metadata["Date"], "%Y-%m-%d")
        self.image = CachedImage(metadata["Image"])
        self.url = f"https://storage.googleapis.com/{bucket.name}/{urllib.parse.quote(self.blob.name)}"
        self.permalink = f"mix/{urllib.parse.quote(self.title)}"

    @staticmethod
    def all(filter=None):
        for blob in bucket.list_blobs():
            if blob.name.startswith("mixes/") and blob.content_type in [
                "audio/mp3",
                "audio/mpeg",
            ]:
                try:
                    m = MixFile(blob)
                    if filter is None or m.title == filter:
                        yield m
                except Exception as e:
                    logging.warning(f"""Failed to load mix "{blob.name}" reason: {e}""")
