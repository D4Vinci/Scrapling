---
title: "Scrapling のテキスト型と属性型を自分のコードで使う"
description: "Parser の外でも TextHandler、TextHandlers、AttributesHandler を使えます。Python の基底型、JSON 用メソッド、読み取り専用の属性を学びます。"
---

# Scrapling の独自の型を使う {#using-scraplings-custom-types}

> Scrapling のために作った型は、ライブラリの外でも使えます。コードをコピーするより、直接使うほうが便利です :)

### 現在のすべての型は個別にインポートできます {#all-current-types-can-be-imported-alone-like-below}
```python
from scrapling.core.custom_types import TextHandler, AttributesHandler

somestring = TextHandler('{}')
parsed = somestring.json()
somedict_1 = AttributesHandler({'a': 1})
somedict_2 = AttributesHandler(a=1)
```

`TextHandler` は Python の `str` のサブクラスなので、文字列用の標準的な操作やメソッドをすべて使えます。
`parsed` は辞書の `{}` であり、文字列の `'{}'` ではありません。インスタンスの確認には `isinstance(somestring, TextHandler)`、クラスの確認には `issubclass(TextHandler, str)` を使います。

`AttributesHandler` は `collections.abc.Mapping` のサブクラスです。変更できない読み取り専用の型で、操作をそこから継承します。渡したデータには `_data` 属性でアクセスできますが、その型も読み取り専用の `types.MappingProxyType` です。`collections.abc.Mapping` よりわずかに高速です。

Python を使い始めたばかりなら、次のように考えると簡単です。標準の `dict` の操作やメソッドは、データを変更するものを除き、`AttributesHandler` でも使えます。

`AttributesHandler` のデータを変更したい場合は、まず `dict` 関数などで辞書に変換し、元のオブジェクトの外で変更してください。
