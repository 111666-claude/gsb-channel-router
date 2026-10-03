# channel-router

频道路由：作用域校验、每人冷却、空消息拒绝与消息去重，只用 Python 标准库。

```
python3 -m router.cli --sample scope
python3 -m router.cli --sample cooldown
python3 -m router.cli --sample empty
python3 -m router.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **作用域**：发言作用域必须等于频道允许的作用域，不匹配返回 false。
- **未知频道**：没有登记过的频道一律拒绝。
- **空消息**：去掉空白后为空的文本返回 false。
- **冷却**：同一玩家同一频道距上次发言不足 `cooldown_ms` 时返回 false，
  正好等于 `cooldown_ms` 可以发言。
- **去重**：同一个 `msg_id` 只成功一次。
- **不变量**：失败发送不改变冷却计时；同一串发送序列重复执行结果相同。
- **代价**：`send` 不许遍历全部频道，`scanned_count` 不随频道数线性增长。
- **规模**：1 万个频道、每秒 10 万次发送，单次摊还 O(1)。

## 输出契约（不改格式）

```
ok=..
second=..
scanned=..
```

## 目录

```
router/core.py   作用域、冷却、空消息与去重
router/cli.py    命令行入口
tests/           unittest 用例
```
