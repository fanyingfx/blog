#set raw(theme: "../minimal-kiwi.tmTheme")

= 常见的三种分类

== 参数化多态
参数化多态，也被称为*泛型*，它允许代码独立于具体类型进行抽象。另外有约束的泛型称为*有界多态*

=== 参数化多态的例子
==== Haskell的 `map`
```haskell
map :: (a->b) -> [a] -> [b]
map f [] = []
map f (x:xs) = f x : map f xs
```
其中map函数无需关注`a`和`b`的具体类型
==== Rust 的 `max`
```rust
fn max<T:PartialOrd>(a:T,b:T)->T{
  if a>b {a} else {b}
}
```
这里的`T`需要实现`PartialOrd` Trait，否则无法进行比较操作

=== 单态化问题（Monomorphization）
在某些语言（如 C++ 和 Rust）中，参数化多态会在编译期生成具体的类型实例，这称为 *单态化*：
- #link("https://www.airs.com/blog/archives/53")[C++ 模板和 Linker]
- #link("https://lobste.rs/s/0jknbl/roc_rewrites_compiler_zig#c_siki17")[Matklad 讨论 Zig 处理泛型的优势]

== 特设多态
为什么叫特设多态？特设多态与参数化多态相对，它针对的是*特定类型或类型组合*的行为，而不是对任意类型抽象。例如，函数重载和操作符重载就是特设多态的典型应用。

=== 大多数语言的二元运算是特设多态
例如，加法运算 `+` 既可以用于整数 (`1 + 1`)，也可以用于浮点数 (`1.1 + 1.1`)。
通常，加法两侧的操作数类型需要一致（如 `i32` 或 `f32`）。
但某些语言支持 *隐式类型转换（Type Coercion）*，例如 `1 + 1.1` 可能会将 `1` 转换为 `1.0` 以适配浮点数计算(因为此处的`1`是字面量，所以可能编译器会直接将它作为浮点数处理)

=== Type Coercion 也是一种 *特设多态*
它允许不同但兼容的类型自动转换，在新的语言中一般会保证此时的转换是安全的，否则会要求改为显示转换的形式：
- #link("https://doc.rust-lang.org/reference/type-coercions.html")[Rust 的 Type Coercion]
- #link("https://ziglang.org/documentation/master/#Type-Coercion")[Zig 的 Type Coercion]

=== OCaml 的二元运算不是特设多态
在 OCaml 中，相同运算对于不同的类型需要不同的运算符。例如：
```ocaml
1 + 1      (* 整数加法 *)
1.1 +. 1.1 (* 浮点数加法 *)
```
此外，OCaml 的打印函数也都是独立的，如 `print_int`, `print_float`, `print_string` 等，不过也有一个支持多种类型的格式化函数 `Printf.printf` 函数。

== 子类型多态
在面向对象语言中子类型通常通过*继承*机制实现，比如C++, Java, C\#等，
不过子类型不是必须通过继承实现，其实两者并不强相关参考：#link("https://www.cmi.ac.in/~madhavan/courses/pl2006/lecturenotes/lecture-notes/node28.html")[Subtyping vs inheritance]


= 动态多态和静态多态
这是多态的另一种分类和根据发生在编译时还是运行时
== 静态多态
发生在编译期，包括
- 函数重载，运算符重载（特设多态）
- 泛型（参数化多态）
- zig的编译期鸭子类型

== 动态多态
发生在*运行时*,包括
- 子类型多态 (继承/接口)
- Trait Object (Rust)
- 手写VTable（当语言不支持以上机制，并需要动态分发时）
不过一般来说子类型多态和Trait Object也会生成VTable，不过一般继承中会将VTable嵌入对象，而Rust的Trait Object是单独的VTable，这也是Rust的Trait Object有 #link("https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility")[dyn-compatibility]限制的原因之一

=== 通过 Tagged Union实现运行时多态

除了 VTable 方案，某些语言（如 Rust、OCaml）可以使用 *Sum Type / Tagged Union* 来手动分发到不同的行为，不过这种方法存在一定的问题，如果variant大小相差比较大的时候，会有空间的浪费，还有就是扩展是需要改变原来sum type的定义，具体可参考表达式问题
- #link("https://en.wikipedia.org/wiki/Expression_problem")[表达式问题（Expression Problem）]
- #link("https://users.rust-lang.org/t/using-trait-vs-wrapping-object-in-enum/92120")[Rust: 使用 Trait Object vs Enum]

= Row Polymorphism
Row Polymorphism 是一种更灵活的多态机制，允许*扩展对象的字段*：
#link("https://jadon.io/blog/row-polymorphism/")[介绍 Row Polymorphism]