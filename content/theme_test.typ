#set raw(theme: "../minimal-kiwi.tmTheme")

= Minimal Kiwi 主题测试

这是一个由 VSCode `` `Minimal Kiwi-light-theme.json` `` 转换而来的 tmTheme 配色测试。

== Typst

```typ
#let greet(name) = {
  // 打个招呼
  [Hello, #name!]
}

#greet("World")

#set text(size: 12pt)
This is *bold*, _italic_, and `raw`.
```

== Python

```py
import math
from typing import List

MAX: int = 100  # 常量

def fibonacci(n: int) -> List[int]:
    """返回前 n 个斐波那契数。"""
    seq = [0, 1]
    for i in range(2, n):
        seq.append(seq[i - 1] + seq[i - 2])
    return seq[:n]

print(fibonacci(10))
```

== Rust

```rs
use std::collections::HashMap;

fn main() {
    let mut scores: HashMap<&str, i32> = HashMap::new();
    scores.insert("Sunface", 42);
    scores.insert("kiwi", 7);

    for (name, score) in &scores {
        println!("{name}: {score}");
    }
}
```

== JavaScript / TypeScript

```ts
interface User {
  id: number;
  name: string;
}

class Greeter {
  constructor(private user: User) {}

  greet(): string {
    return `Hello, ${this.user.name}!`;
  }
}

const g = new Greeter({ id: 1, name: "Typst" });
console.log(g.greet());
```

== Shell

```sh
#!/usr/bin/env bash
set -euo pipefail

echo "Building..."
for f in src/*.typ; do
  echo "-> $f"
  typst compile "$f"
done
```

== SQL

```sql
SELECT id, name, created_at
FROM users
WHERE active = true
ORDER BY created_at DESC
LIMIT 10;
```

== JSON

```json
{
  "name": "minimal-kiwi",
  "type": "light",
  "colors": {
    "editor.background": "#FFFFFF",
    "editor.foreground": "#413E3C"
  }
}
```
