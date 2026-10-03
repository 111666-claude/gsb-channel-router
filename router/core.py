"""频道路由：作用域校验、每人冷却、空消息拒绝与消息去重。

缺陷：不校验频道作用域、冷却不生效、空消息放行、未知频道放行、
每次发送扫描全部频道。
"""


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
        self.scanned += len(self.channels)
        self.seen.add(msg_id)
        self.last[(player, channel)] = now_ms
        return True

    def scanned_count(self):
        return self.scanned
