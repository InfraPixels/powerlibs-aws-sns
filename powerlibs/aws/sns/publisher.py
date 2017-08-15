import json
import logging
import os

import boto3
from botocore.exceptions import ClientError
from cached_property import cached_property

from .exceptions import SNSPublisherError


class SNSPublisher:
    def __init__(self, prefix, aws_access_key_id=None, aws_secret_access_key=None, aws_region=None):
        self.prefix = prefix

        self.aws_region = aws_region or os.environ.get('AWS_REGION', None)
        self.aws_access_key_id = aws_access_key_id or os.environ['AWS_ACCESS_KEY_ID']
        self.aws_secret_access_key = aws_secret_access_key or os.environ['AWS_SECRET_ACCESS_KEY']

        self.logger = logging.getLogger()
        self.topics = self.get_topics()

    @cached_property
    def client(self):
        return boto3.resource(
            'sns',
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

    def _get_arns(self, next_token=''):
        try:
            data = self.client.list_topics(NextToken=next_token)
        except ClientError as exc:
            raise SNSPublisherError(exc)

        arns = [d['TopicArn'] for d in data['Topics']]
        if 'NextToken' in data:
            arns.extend(self._get_arns(data['NextToken']))
        return arns

    def get_topics(self):
        topics = {}

        for arn in self._get_arns():
            key = arn.split(':')[-1]
            if key.startswith(self.prefix + '__'):
                topics[key] = arn

        return topics

    def create_topic(self, name):
        return_value = self.client.create_topic(Name=name)
        arn = return_value['TopicArn']
        self.logger.info('New SNS topic created. name="{}" arn="{}"'.format(name, arn))
        self.topics[name] = arn
        return arn

    def get_topic_arn_by_name(self, topic_name):
        topic_name = "{}__{}".format(self.prefix, topic_name)

        try:
            return self.topics[topic_name]
        except KeyError:
            arn = self.create_topic(topic_name)
            return arn

    def publish(self, topic, message, json_encoder_class=None, structure='json'):
        arn = self.get_topic_arn_by_name(topic)

        default_content = json.dumps(message, cls=json_encoder_class)
        message = json.dumps({'default': default_content}, cls=json_encoder_class)

        try:
            return self.client.publish(TopicArn=arn, MessageStructure=structure, Message=message)
        except ClientError as exc:
            raise SNSPublisherError("SNS Publishing error {!r}".format(exc))
