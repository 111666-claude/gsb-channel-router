"""频道路由：作用域校验、每人冷却、空消息拒绝与消息去重。"""


class Router:
    def __init__(self, cooldown_ms):
        self.cooldown_ms = cooldown_ms
        self.channels = {}
        self.last = {}
        self.seen = set()
        self.scanned = 0

    def add(self, channel, scope):
        self.channels[channel] = scope

    def send(self, player, channel, scope, text, now_ms, msg_id):
        if msg_id in self.seen:
            return False

        allowed = self.channels.get(channel)
        key = (player, channel)
        previous = self.last.get(key)
        self.scanned += 1

        if allowed is None:
            return False
        elif allowed != scope:
            return False
        elif not str(text).strip():
            return False
        elif previous is not None and now_ms - previous < self.cooldown_ms:
            return False

        self.last[key] = now_ms
        self.seen.add(msg_id)
        return True

    def scanned_count(self):
        return self.scanned
