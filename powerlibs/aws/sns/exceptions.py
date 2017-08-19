class PublisherException(Exception):
    pass


class SNSPublisherError(PublisherException):
    pass


class TopicNotFound(PublisherException):
    pass
