# atom_conv bulk run

### 実施方法

1. `pdbbind_v2015.tar.gz`を展開しディレクトリ`v2015/`がカレントディレクトリにある状態にしてください。

2. 指定したディレクトリをまとめてデータ化します。
```
python bulkrun.py v2015
```

※ テストでは、途中でCtrl-Cで終了しても構いません。

3. カレントディレクトリにあるすべての`*_out.npz`ファイルを結合します。
```
python concat_npz.py
```

4. このデータをPythonスクリプトに取り込みます。
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

