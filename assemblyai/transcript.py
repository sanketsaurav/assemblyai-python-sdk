"""Transcript module."""

import json
import logging

from assemblyai.exceptions import handle_warnings
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

    def validate(self):
        """Deconflict filename and audio_url."""
        if self.filename and not self.audio_url:
            if self.filename.startswith('http'):
                self.audio_url = self.filename
                self.filename = None
            else:
                self.audio_url = self.upload(self.filename)

    def create(self):
        """Create a transcript."""
        # TODO remove model checking after api defaults to waiting for models
        self.validate()
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
        upload_url = 'https://api.assemblyai.com/upload'
        presigned_url = requests.post(upload_url, headers=self.headers).text
        url = presigned_url.split('?')[0]
        with open(filepath, 'rb') as f:
            r = requests.put(presigned_url, data=f.read())
        r.raise_for_status()
        return url
