from datetime import datetime, timedelta
from threading import Thread
import random
import time


class Message(object):
    message: str
    date_time: datetime

    def __init__(self, message: str, date_time: datetime = None):
        if date_time is None:
            date_time = datetime.now()
        self.message = message
        self.date_time = date_time

    def __str__(self):
        return '%s: %s' % (self.date_time.strftime("%d/%m/%Y %H:%M:%S.%f"), self.message)

    def __repr__(self):
        return '<Message: date_time="%s" message="%s">' % (self.date_time, self.message)

    def __lt__(self, other):
        """Less than by Message datetime

        Args:
            other (Message): other message to compare

        Returns:
            bool: self is less than other
        """
        return self.date_time < other.date_time

    def __gt__(self, other):
        """greater than by Message datetime

        Args:
            other (Message): other message to compare

        Returns:
            bool: self is greater than other
        """
        return self.date_time > other.date_time

    def __le__(self, other):
        """less or equal than by Message datetime

        Args:
            other (Message): other message to compare

        Returns:
            bool: self is less or equal than other
        """
        return self.date_time <= other.date_time

    def __ge__(self, other):
        """greater or equal than by Message datetime

        Args:
            other (Message): other message to compare

        Returns:
            bool: self is greater or equal than other
        """
        return self.date_time >= other.date_time


class Channel(object):
    name: str
    messages: list

    def __init__(self, name: str = "one"):
        self.name = name
        self.messages = list()

    def post(self, message: str, date_time: datetime = None):
        """Post a message into this channel

        Args:
            message (str): string message
            date_time (datetime, optional): datetime the message was posted. Defaults to None (Now).

        Returns:
            Message: the posted message
        """
        m = Message(message, date_time)
        self.messages.append(m)
        self.messages.sort()
        return m

    def get_anonymous_messages(self, start: datetime, end: datetime):
        """Get anonymous messages between start and end datetime

        Args:
            start (datetime): Start datetime
            end (datetime): End datetime

        Returns:
            list: sorted list of messages
        """
        in_between_dates = []
        for message in self.messages:
            if message.date_time >= start and message.date_time <= end:
                in_between_dates.append(message)
        return sorted(in_between_dates)

    def __str__(self):
        return "Channel %s:\n" % self.name + "".join(["%s\n" % m for m in self.messages])

    def __repr__(self):
        return '<Channel %s: %d messages>' % (self.name, len(self.messages))


class User(object):
    name: str
    sended_messages: list

    def __init__(self, name: str):
        self.name = name
        self.sended_messages = list()

    def generate_secret(self, other, channel, duration: timedelta):
        """Generate secret

        Args:
            other (User): the other user
            channel (Channel): Channel where users post anonymous messages
            duration (timedelta): protocol duration
        """
        the_end = datetime.now() + duration
        while datetime.now() < the_end:
            # between 1 and 10 ms
            sleep_duration = random.randint(1, 10) * 0.001
            time.sleep(sleep_duration)

            b = random.randint(0, 1)

            self.sended_messages.append(
                channel.post(self.name if b == 0 else other.name)
            )

    def extract_secret(self, channel, start_time, end_time):
        """Extract secret from all sended messages

        Args:
            channel (Channel): Channel where users post anonymous messages
            start_time (datetime): start time of protocol
            end_time (datetime): end time of protocol

        Returns:
            str: the secret
        """
        messages = channel.get_anonymous_messages(start_time, end_time)

        bits = ""
        for message in messages:
            is_truth = (message.message == self.name and message in self.sended_messages) or (
                message.message != self.name and message not in self.sended_messages)

            bits += '0' if is_truth else '1'

        return bits


def generate_secret(user_1, user_2, channel, duration: timedelta):
    """Generate secret for both user 1 and user 2

    Args:
        user_1 (User): User 1
        user_2 (User): User 2
        channel (Channel): Channel where users post anonymous messages
        duration (timedelta): protocol duration

    Returns:
        tuple: start and end datetime
    """
    start = datetime.now()

    thread_1 = Thread(target=user_1.generate_secret,
                      args=(user_2, channel, duration))
    thread_2 = Thread(target=user_2.generate_secret,
                      args=(user_1, channel, duration))

    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()

    end = datetime.now()
    return start, end


if __name__ == "__main__":
    alice = User("Alice")
    bob = User("Bob")
    c = Channel()

    duration = timedelta(seconds=2)
    st, ed = generate_secret(alice, bob, c, duration)

    alice_secret = alice.extract_secret(c, st, ed)
    bob_secret = bob.extract_secret(c, st, ed)

    print(repr(c))
    print("Alice and Bob have the same secret :", alice_secret == bob_secret)
