import json
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from powerlibs.aws.sns.publisher import SNSPublisher
from powerlibs.aws.sns.exceptions import SNSPublisherError


def test_topics(sns_publisher):
    assert len(sns_publisher.topics) == 5

    assert 'arn:aws:region:id:TEST2__test1' in sns_publisher.topics.values()
    assert sns_publisher.mocked_client.called


def test_topic_names(sns_publisher):
    topics = sns_publisher.topics

    assert len(topics) == 5
    assert 'TEST__test1' in topics
    assert 'TEST__test2' in topics
    assert sns_publisher.mocked_client.called


def test_get_topic_arn_by_name(sns_publisher):
    arn = sns_publisher.get_topic_arn_by_name('test1')

    assert arn.startswith('arn:')
    assert arn.endswith('test1')

    assert sns_publisher.mocked_client.called


def test_publish(sns_publisher):
    sns_publisher.publish('test1', 'message')
    arn = sns_publisher.get_topic_arn_by_name('test1')

    assert sns_publisher.mocked_client.called
    assert sns_publisher.mocked_client.return_value.publish.called
    sns_publisher.mocked_client.return_value.publish.assert_called_once_with(
        TopicArn=arn,
        MessageStructure='json',
        Message=json.dumps({'default': json.dumps('message')})
    )


def test_publish_on_nonexistent_topic(sns_publisher):
    sns_publisher.publish('test_NEW', 'message')
    arn = sns_publisher.get_topic_arn_by_name('test_NEW')

    assert sns_publisher.mocked_client.called
    assert sns_publisher.mocked_client.return_value.publish.called
    sns_publisher.mocked_client.return_value.publish.assert_called_once_with(
        TopicArn=arn,
        MessageStructure='json',
        Message=json.dumps({'default': json.dumps('message')})
    )


def test_list_topics_client_error(mock_boto_client_sns):

    with mock_boto_client_sns as mock_sns:
        mock_sns.side_effect = ClientError({'Error': {'Code': 'Unknown'}}, 'list_topics')
        with pytest.raises(SNSPublisherError):
            SNSPublisher()

        assert mock_sns.called
        assert not mock_sns.return_value.publish.called


def test_sns_publish_client_error(sns_publisher):
    sns_publisher.client.publish = mock.Mock(
        side_effect=ClientError({'Error': {'Code': 'Unknown'}}, 'list_topics')
    )

    with pytest.raises(SNSPublisherError):
        sns_publisher.publish('test1', 'message')
