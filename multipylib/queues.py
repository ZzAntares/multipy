import redis


class RedisQueue:
    """
    Simple queue using a Redis backend.
    """

    def __init__(self, name, namespace='queue', **kwargs):
        """
        Creates a new handler for a queue backedup in Redis. Other keyword
        arguments will be passed to the redis.Redis constructor, so you can use
        'host', 'port' and 'db' as well.

        Args:
            name (str): Name used to identify the queue.
            namespace (str): Used to namespace the queue in redis.
        """
        self.__db = redis.Redis(**kwargs)
        self.key = '{}:{}'.format(namespace, name)

    def qsize(self):
        """
        Return the size of this queue.

        Returns:
            int: Size of the queue.
        """
        return self.__db.llen(self.key)

    def empty(self):
        """
        Checks if this queue is empty or not.

        Returns:
            bool: True if empty, False otherwise.
        """
        return self.qsize() == 0

    def put(self, item):
        """
        Put a new item in this queue.

        Args:
            item (object): The item to place in the queue (unserialized).
        """
        self.__db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        """
        Retrieves and removes an item from this queue.

        Args:
            block (bool): If there are no items and this is True, it will wait
                          for an item appears to return.
            timeout (int): If blocking is True, wait this many seconds before
                           unblocking, if this is None then it waits forever.

        Returns:
            item (object): The item retrieved from the queue (unserialized).
        """
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        if item:
            return item[1]

        return item

    def get_nowait(self):
        """
        Convinience alias for 'get(block=False)' giving back an item from the
        queue or None if the queue is empty.

        Returns:
            item (object): The item retrieved from the queue (unserialized) or
                           None if the queue was empty.
        """
        return self.get(False)
