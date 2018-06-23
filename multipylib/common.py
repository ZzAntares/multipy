class QueueFinished:
    """
    When no more messages are going to be sent to the queue, the other end will
    receive an instance of this class as a sentinel value.
    """
    pass
