"""命令行入口：跑频道路由样例。"""

import argparse

from .core import Router


def main(argv=None):
    parser = argparse.ArgumentParser(prog="channel-router", description="频道路由")
    parser.add_argument("--sample", default="scope", help="scope / cooldown / empty / scan")
    args = parser.parse_args(argv)
    if args.sample == "scope":
        router = Router(cooldown_ms=0)
        router.add("guild", "guild")
        print("ok=%s" % str(router.send("p1", "guild", "world", "hi", 0, "m1")).lower())
    elif args.sample == "cooldown":
        router = Router(cooldown_ms=5000)
        router.add("world", "world")
        router.send("p1", "world", "world", "hi", 0, "m1")
        print("second=%s" % str(router.send("p1", "world", "world", "yo", 1, "m2")).lower())
    elif args.sample == "empty":
        router = Router(cooldown_ms=0)
        router.add("world", "world")
        print("ok=%s" % str(router.send("p1", "world", "world", "", 0, "m1")).lower())
    elif args.sample == "scan":
        router = Router(cooldown_ms=0)
        for index in range(3000):
            router.add("c-%d" % index, "world")
        for index in range(3000):
            router.send("p1", "c-2999", "world", "hi", index, "m-%d" % index)
        print("scanned=%d" % router.scanned_count())
    else:
        raise SystemExit("需要 --sample scope|cooldown|empty|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
