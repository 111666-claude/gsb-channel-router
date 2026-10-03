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


if __name__ == "__main__":
    unittest.main()
