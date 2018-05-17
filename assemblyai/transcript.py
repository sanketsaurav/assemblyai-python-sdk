"""Transcript module."""

import json
import logging
from uuid import uuid4

from assemblyai.exceptions import handle_warnings
from boto3.s3.transfer import S3Transfer
import boto3
import botocore
import requests


class Transcript(object):
    """Transcript object."""

    def __init__(self, client, filename=None, audio_url=None, model=None):
        self.api = client.api
        self.audio_url = audio_url
        self.confidence = None
        self.dict = None
        self.filename = filename
        self.headers = client.headers
        self.id = None
        self.model = model
        self.segments = None
        self.speaker_count = None
        self.status = None
        self.text = None
        self.text_raw = None
        self.warning = None

    def __repr__(self):
        return 'Transcript(id=%s, status=%s, text=%s)' % (
            self.id, self.status, self.text)

    def props(self):
        return [i for i in self.__dict__.keys() if i[:1] != '_']

    def reset(self, id=None):
        if id:
            # self.api = client.api
            self.audio_url = None
            self.confidence = None
            self.dict = None
            self.filename = None
            # self.headers = client.headers
            self.id = id
            self.model = None
            self.segments = None
            self.speaker_count = None
            self.status = None
            self.text = None
            self.text_raw = None
            self.warning = None

    def create(self):
        # TODO remove model checking after api defaults to waiting for models
        if self.filename and not self.audio_url:
            self.audio_url = self.upload(self.filename)
        if self.model:
            self.model = self.model.get()
        if self.model and self.model.status != 'trained':
            self.status = 'waiting for model'
        else:
            data = {}
            data['audio_src_url'] = self.audio_url
            if self.model:
                data['model_id'] = self.model.id
            payload = json.dumps(data)
            url = self.api + '/transcript'
            response = requests.post(url, data=payload, headers=self.headers)
            self.warning = handle_warnings(response, 'transcript')
            response = response.json()['transcript']
            self.id, self.status = response['id'], response['status']
            logging.debug('Transcript %s %s' % (self.id, self.status))
        return self

    def check_model(self):
        # TODO remove model checking after api defaults to waiting for models
        self.model = self.model.get()
        if self.model.status == 'trained' and not self.id:
            self = self.create()
        elif self.model.status != 'trained':
            self.status = 'waiting for model'

    def get(self, id=None):
        """Get a transcript."""
        self.reset(id)
        if self.model:
            self.check_model()
        if self.id:
            url = self.api + '/transcript/' + str(self.id)
            response = requests.get(url, headers=self.headers)
            self.warning = handle_warnings(response, 'transcript')
            response = response.json()['transcript']
            self.dict = response
            self.id, self.status = response['id'], response['status']
            # if self.status == 'completed':
            self.text_raw = response['text']
            self.text = response['text_formatted']
            self.confidence = response['confidence']
            self.segments = response['segments']
            self.speaker_count = response['speaker_count']
        logging.debug('Transcript %s %s' % (self.id, self.status))
        return self

    def upload(self, filepath):
        """Upload a file."""
        client = boto3.client('s3')
        # , aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        transfer = S3Transfer(client)
        # filename = filepath.split('/')[-1]
        s3_bucket = 'chappy-temp'  # target.split('/')[0]
        s3_path = str(uuid4())
        if '.' in filepath:
            type = filepath.split('.')[-1].strip().strip('/').strip()
            s3_path = '.'.join([s3_path, type])
        # '/'.join(target.split('/')[1:] + [filename])
        transfer.upload_file(filepath, s3_bucket, s3_path)
        # get url
        s3 = boto3.client('s3')
        config = s3._client_config
        config.signature_version = botocore.UNSIGNED
        params = {'Bucket': s3_bucket, 'Key': s3_path}
        url = boto3.resource('s3', config=config).meta.client.generate_presigned_url(
            'get_object', ExpiresIn=0, Params=params)
        # self.upload = s3_path
        return url
