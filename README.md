## 概要

nature remoのAPIでデータを取得してgoogleスプレッドシートに書き込むスクリプト

## 処理の流れ

cloud scheduler -> cloud Pub/Sub -> cloud function(ここで、index.pyのスクリプトを仕様) -> google spreadsheet

## nature remo について

API仕様

https://developer.nature.global/


Access tokensの取得

https://home.nature.global/

## Pythonからgoogle spread sheetへの書き込みについて

https://qiita.com/akabei/items/0eac37cb852ad476c6b9