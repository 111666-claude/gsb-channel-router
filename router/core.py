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
        self.scanned += 1
        allowed = self.channels.get(channel)
        if allowed is None or allowed != scope:
            return False
        if not text or not text.strip():
            return False
        if msg_id in self.seen:
            return False
        key = (player, channel)
        last_ms = self.last.get(key)
        if last_ms is not None and now_ms - last_ms < self.cooldown_ms:
            return False
        self.seen.add(msg_id)
        self.last[key] = now_ms
        return True

    def scanned_count(self):
        return self.scanned
