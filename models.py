from utils import format_datetime


class Message:
    def __init__(self, username, sent, text):
        self.username = username
        self.sent = sent
        self.text = text
        self.tag = None

    def get_formatted_sent(self):
        return format_datetime(self.sent)
