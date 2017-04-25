import json
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from powerlibs.aws.sns.publisher import SNSPublisher
from powerlibs.aws.sns.exceptions import SNSPublisherError


def test_topics(mock_boto_client_sns):
    with mock_boto_client_sns as mock_sns:
        sns_publisher = SNSPublisher(prefix='TEST2')

        assert len(sns_publisher.topics) == 1
        assert tuple(sns_publisher.topics.values())[0].startswith('arn:aws:region:id:TEST2__test1')
        assert mock_sns.called


def test_topic_names(mock_boto_client_sns):
    with mock_boto_client_sns as mock_sns:
        sns_publisher = SNSPublisher(prefix='TEST')
        topics = sns_publisher.topics

        assert len(topics) == 2
        assert 'TEST__test1' in topics
        assert 'TEST__test2' in topics
        assert mock_sns.called


def test_topic_name_is_sns_prefix(mock_boto_client_sns):
    with mock_boto_client_sns as mock_sns:
        sns_publisher = SNSPublisher(prefix='TEST3')
        topic = sns_publisher.get_topic_arn_by_name('TEST3')
        assert topic == 'arn:aws:region:id:TEST3__TEST3'
        assert mock_sns.called


def test_get_topic_arn_by_name(mock_boto_client_sns):
    with mock_boto_client_sns as mock_sns:
        sns_publisher = SNSPublisher(prefix='TEST')
        arn = sns_publisher.get_topic_arn_by_name('test1')

        assert arn.startswith('arn:')
        assert arn.endswith('test1')

        assert mock_sns.called


def test_publish(mock_boto_client_sns):
    with mock_boto_client_sns as mock_sns:
        sns_publisher = SNSPublisher(prefix='TEST')
        sns_publisher.publish('test1', 'message')
        arn = sns_publisher.get_topic_arn_by_name('test1')

        assert mock_sns.called
        assert mock_sns.return_value.publish.called
        mock_sns.return_value.publish.assert_called_once_with(
            TopicArn=arn,
            MessageStructure='json',
            Message=json.dumps({'default': json.dumps('message')})
        )


def test_publish_on_nonexistent_topic(mock_boto_client_sns):
    with mock_boto_client_sns as mock_sns:
        sns_publisher = SNSPublisher(prefix='TEST')
        sns_publisher.publish('test_NEW', 'message')
        arn = sns_publisher.get_topic_arn_by_name('test_NEW')

        assert mock_sns.called
        assert mock_sns.return_value.publish.called
        mock_sns.return_value.publish.assert_called_once_with(
            TopicArn=arn,
            MessageStructure='json',
            Message=json.dumps({'default': json.dumps('message')})
        )


def test_list_topics_client_error(mock_boto_client_sns):
    with mock_boto_client_sns as mock_sns:
        mock_sns.side_effect = ClientError({'Error': {'Code': 'Unknown'}}, 'list_topics')

        with pytest.raises(SNSPublisherError):
            SNSPublisher(prefix='TEST2')

        assert mock_sns.called
        assert not mock_sns.return_value.publish.called


def test_sns_publish_client_error(mock_boto_client_sns):
    with mock_boto_client_sns:
        publisher = SNSPublisher(prefix='TEST2')

        publisher.client.publish = mock.Mock(
            side_effect=ClientError({'Error': {'Code': 'Unknown'}}, 'list_topics')
        )

        with pytest.raises(SNSPublisherError):
            publisher.publish('test1', 'message')
