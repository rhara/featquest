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

4. INDEXファイルからyの値を読み込み、出力のデータセットに加えます（データの中の学習データXと正答yは当然対応します）。
```
python add_y.py all.npz v2015/INDEX_general_PL_data.2015 Xy.npz
```

5. このデータをPythonスクリプトに取り込みます。
```
>>> import numpy as np
>>> data = np.load('Xy.npz')
>>> X = data['X']
>>> y = data['y']
>>> print(X.shape) #shapeの確認
>>> print(y.shape)
>>> codes = data['codes'].tolist()
>>> print(codes)
```
ここで、shapeがX=(n, 90, 14, 22), y=(n,)であることが確認できます。 (nは実行環境によります)


### 修正のポイント

リガンドの最大限指数は`LIGAND_ATOMS = 90`を修正して対応します。それより大きなリガンドに対しては出力をしません。

