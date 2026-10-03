import unittest

from router.core import Router


def router():
    world = Router(cooldown_ms=1000)
    world.add("world", "world")
    return world


class BasicTest(unittest.TestCase):
    def test_first_message_ok(self):
        self.assertTrue(router().send("p1", "world", "world", "hi", 0, "m1"))

    def test_channel_is_registered(self):
        self.assertEqual(router().channels["world"], "world")

    def test_cooldown_is_stored(self):
        self.assertEqual(router().cooldown_ms, 1000)

    def test_scanned_starts_at_zero(self):
        self.assertEqual(router().scanned_count(), 0)


class ScopeTest(unittest.TestCase):
    def test_matching_scope_ok(self):
        self.assertTrue(router().send("p1", "world", "world", "hi", 0, "m1"))

    def test_mismatched_scope_rejected(self):
        r = router()
        r.add("guild", "guild")
        self.assertFalse(r.send("p1", "guild", "world", "hi", 0, "m1"))

    def test_scope_mismatch_does_not_start_cooldown(self):
        r = router()
        r.add("guild", "guild")
        self.assertFalse(r.send("p1", "guild", "world", "hi", 0, "m1"))
        self.assertTrue(r.send("p1", "guild", "guild", "hi", 1, "m2"))


class UnknownChannelTest(unittest.TestCase):
    def test_unknown_channel_rejected(self):
        self.assertFalse(router().send("p1", "nope", "world", "hi", 0, "m1"))

    def test_unknown_channel_does_not_start_cooldown(self):
        r = router()
        self.assertFalse(r.send("p1", "nope", "world", "hi", 0, "m1"))
        self.assertTrue(r.send("p1", "world", "world", "hi", 1, "m2"))


class EmptyMessageTest(unittest.TestCase):
    def test_empty_text_rejected(self):
        self.assertFalse(router().send("p1", "world", "world", "", 0, "m1"))

    def test_whitespace_only_rejected(self):
        self.assertFalse(router().send("p1", "world", "world", "  \t\n ", 0, "m1"))

    def test_empty_send_does_not_start_cooldown(self):
        r = router()
        self.assertFalse(r.send("p1", "world", "world", "", 0, "m1"))
        self.assertTrue(r.send("p1", "world", "world", "hi", 1, "m2"))


class CooldownTest(unittest.TestCase):
    def test_within_cooldown_rejected(self):
        r = router()
        self.assertTrue(r.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertFalse(r.send("p1", "world", "world", "yo", 999, "m2"))

    def test_exactly_at_cooldown_allowed(self):
        r = router()
        self.assertTrue(r.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertTrue(r.send("p1", "world", "world", "yo", 1000, "m2"))

    def test_failed_send_does_not_change_cooldown(self):
        r = router()
        self.assertTrue(r.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertFalse(r.send("p1", "world", "world", "", 500, "m2"))
        self.assertFalse(r.send("p1", "world", "world", "yo", 999, "m3"))
        self.assertTrue(r.send("p1", "world", "world", "yo", 1000, "m4"))

    def test_cooldown_is_per_player_and_channel(self):
        r = router()
        r.add("guild", "guild")
        self.assertTrue(r.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertTrue(r.send("p2", "world", "world", "hi", 1, "m2"))
        self.assertTrue(r.send("p1", "guild", "guild", "hi", 1, "m3"))


class DedupTest(unittest.TestCase):
    def test_same_msg_id_succeeds_once(self):
        r = router()
        self.assertTrue(r.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertFalse(r.send("p1", "world", "world", "hi", 2000, "m1"))

    def test_failed_send_does_not_consume_msg_id(self):
        r = router()
        self.assertFalse(r.send("p1", "nope", "world", "hi", 0, "m1"))
        self.assertTrue(r.send("p1", "world", "world", "hi", 0, "m1"))

    def test_replay_same_sequence_same_results(self):
        seq = [
            ("p1", "world", "world", "hi", 0, "m1"),
            ("p1", "world", "world", "yo", 500, "m2"),
            ("p1", "world", "world", "yo", 1000, "m2"),
            ("p1", "world", "world", "again", 1000, "m3"),
        ]
        first = [router().send(*args) for args in seq]
        second = [router().send(*args) for args in seq]
        self.assertEqual(first, second)


class ScanCostTest(unittest.TestCase):
    def test_scanned_not_linear_in_channel_count(self):
        r = Router(cooldown_ms=0)
        for index in range(10000):
            r.add("c-%d" % index, "world")
        for index in range(3000):
            r.send("p1", "c-9999", "world", "hi", index, "m-%d" % index)
        self.assertLessEqual(r.scanned_count(), 6000)


if __name__ == "__main__":
    unittest.main()
