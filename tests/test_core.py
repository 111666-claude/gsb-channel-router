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
        world = router()
        world.add("guild", "guild")
        self.assertFalse(world.send("p1", "guild", "world", "hi", 0, "m1"))

    def test_scope_check_per_channel(self):
        world = router()
        world.add("guild", "guild")
        self.assertTrue(world.send("p1", "guild", "guild", "hi", 0, "m1"))
        self.assertFalse(world.send("p1", "world", "guild", "hi", 0, "m2"))


class UnknownChannelTest(unittest.TestCase):
    def test_unknown_channel_rejected(self):
        self.assertFalse(router().send("p1", "nope", "world", "hi", 0, "m1"))

    def test_unknown_channel_rejected_even_with_matching_scope(self):
        self.assertFalse(router().send("p1", "world2", "world", "hi", 0, "m1"))


class EmptyMessageTest(unittest.TestCase):
    def test_empty_text_rejected(self):
        self.assertFalse(router().send("p1", "world", "world", "", 0, "m1"))

    def test_whitespace_only_text_rejected(self):
        self.assertFalse(router().send("p1", "world", "world", "   \t\n ", 0, "m1"))

    def test_text_with_surrounding_whitespace_ok(self):
        self.assertTrue(router().send("p1", "world", "world", "  hi  ", 0, "m1"))


class CooldownTest(unittest.TestCase):
    def test_second_send_within_cooldown_rejected(self):
        world = router()
        self.assertTrue(world.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertFalse(world.send("p1", "world", "world", "yo", 999, "m2"))

    def test_send_exactly_at_cooldown_ok(self):
        world = router()
        self.assertTrue(world.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertTrue(world.send("p1", "world", "world", "yo", 1000, "m2"))

    def test_cooldown_is_per_player(self):
        world = router()
        self.assertTrue(world.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertTrue(world.send("p2", "world", "world", "yo", 1, "m2"))

    def test_cooldown_is_per_channel(self):
        world = router()
        world.add("guild", "guild")
        self.assertTrue(world.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertTrue(world.send("p1", "guild", "guild", "yo", 1, "m2"))

    def test_failed_send_does_not_start_cooldown(self):
        world = router()
        self.assertFalse(world.send("p1", "world", "world", "", 0, "m1"))
        self.assertTrue(world.send("p1", "world", "world", "hi", 1, "m2"))


class DedupTest(unittest.TestCase):
    def test_same_msg_id_succeeds_once(self):
        world = router()
        self.assertTrue(world.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertFalse(world.send("p1", "world", "world", "hi", 0, "m1"))

    def test_failed_send_result_is_replayed(self):
        world = router()
        self.assertFalse(world.send("p1", "nope", "world", "hi", 0, "m1"))
        self.assertFalse(world.send("p1", "nope", "world", "hi", 0, "m1"))

    def test_replay_does_not_change_cooldown(self):
        world = router()
        self.assertTrue(world.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertFalse(world.send("p1", "world", "world", "hi", 0, "m1"))
        self.assertTrue(world.send("p1", "world", "world", "yo", 1000, "m2"))

    def test_repeated_sequence_gives_same_results(self):
        def run():
            world = router()
            return [
                world.send("p1", "world", "world", "hi", 0, "m1"),
                world.send("p1", "world", "world", "yo", 1, "m2"),
                world.send("p1", "world", "world", "yo", 1000, "m3"),
                world.send("p1", "world", "world", "yo", 1000, "m3"),
            ]

        self.assertEqual(run(), run())


class CostTest(unittest.TestCase):
    def test_scanned_does_not_grow_with_channel_count(self):
        world = router()
        for index in range(10000):
            world.add("c-%d" % index, "world")
        for index in range(100):
            world.send("p1", "c-9999", "world", "hi", index * 1000, "m-%d" % index)
        self.assertLessEqual(world.scanned_count(), 200)


if __name__ == "__main__":
    unittest.main()
