# atom_conv bulk run

### 実施方法

1. `pdbbind_v2015.tar.gz`を展開しディレクトリ`v2015/`がカレントディレクトリにある状態にしてください。

2. バッチ実行用のシェルスクリプト`bulkrun.sh`を生成します。
```
python mkbulkrun.py v2015 > bulkrun.sh
```

3. 生成したシェルスクリプト`bulkrun.sh`を実行します。
```
bash bulkrun.sh
```
※ テストでは、途中でCtrl-Cで終了しても構いません。

4. カレントディレクトリにあるすべての`*_out.npz`ファイルを結合します。
```
python concat_npz.py
```

5. このデータをPythonスクリプトに取り込みます。
```
>>> import numpy as np
>>> data = np.load('all.npz')
>>> X = data['X']
>>> print(X.shape) #shapeの確認
>>> codes = data['codes'].tolist()
>>> codes
```
ここで、shapeが(n, 90, 14, 22)であることが確認できます。 (nは実行環境によります)


### 修正のポイント

リガンドの最大限指数は`LIGAND_ATOMS = 90`を修正して対応します。それより大きなリガンドに対しては出力をしません。

