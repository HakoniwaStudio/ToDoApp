
# ToDoApp - 理想のToDoリスト

モジュラー設計に基づいたマルチプラットフォーム対応ToDoアプリケーション

## プロジェクト構成

```
app/
├── backend/              # Python (FastAPI) バックエンド
│   ├── core/            # コアプログラム（モジュール管理システム）
│   ├── modules/         # 機能モジュール
│   ├── database/        # データベース関連
│   ├── api/             # APIエンドポイント
│   ├── main.py          # アプリケーションエントリーポイント
│   ├── config.py        # 設定管理
│   └── requirements.txt # 依存関係
├── frontend/
│   ├── mobile/          # React Native (iOS/Android)
│   ├── desktop/         # Electron (Windows/Mac)
│   └── web/             # React Web
└── docs/                # ドキュメント
```

## 技術スタック

### バックエンド
- **FastAPI**: 高速なWebフレームワーク
- **SQLAlchemy**: ORM（データベース操作）
- **SQLite**: データベース（開発環境）
- **Pydantic**: データバリデーション

### フロントエンド（予定）
- **React Native**: モバイルアプリ
- **Electron**: デスクトップアプリ
- **React**: Webアプリ

## セットアップ手順

### 1. 仮想環境の作成

```bash
cd app/backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを必要に応じて編集

### 4. データベースの初期化

アプリケーション起動時に自動的にSQLiteデータベースが作成されます。

### 5. アプリケーションの起動

```bash
# 開発サーバーの起動
python main.py

# または
uvicorn main:app --reload
```

サーバーは `http://localhost:8000` で起動します。

## API エンドポイント

### 基本エンドポイント
- `GET /` - アプリケーション情報
- `GET /health` - ヘルスチェック

### タスク管理 (`/api/v1/tasks`)
- `POST /` - タスク作成
- `GET /` - タスク一覧取得（フィルタリング可能）
- `GET /{task_id}` - 特定タスク取得
- `PUT /{task_id}` - タスク更新
- `DELETE /{task_id}` - タスク削除

### サブタスク管理
- `POST /{task_id}/subtasks` - サブタスク追加
- `GET /{task_id}/subtasks` - サブタスク一覧取得

### 優先度管理
- `PUT /{task_id}/priority` - 優先度設定
- `GET /{task_id}/priority` - 優先度取得

### 期限管理
- `PUT /{task_id}/deadline` - 期限設定
- `DELETE /{task_id}/deadline` - 期限削除
- `GET /overdue/list` - 期限切れタスク一覧
- `GET /upcoming/list` - 近日期限タスク一覧

### API ドキュメント
起動後、以下のURLでインタラクティブなAPIドキュメントを確認できます：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## モジュール構造

### コアシステム
- **ModuleManager**: モジュール間通信の仲介役
- **BaseModule**: すべてのモジュールの基底クラス

### 実装済みモジュール
1. **TaskCRUDModule**: タスクのCRUD操作
2. **PriorityManagerModule**: 優先度管理
3. **DeadlineManagerModule**: 期限管理

### モジュール間通信の例

```python
# モジュールAがモジュールBの機能を使う
result = module_manager.call_module(
    "module_b_name",
    "action_name",
    {"param1": "value1"}
)
```

## データベーススキーマ

### tasks テーブル
- タスクの基本情報（タイトル、説明、優先度、期限、ステータス、進捗率）
- 階層構造のサポート（親タスク・サブタスク）

### categories テーブル
- カテゴリ情報（名前、色）

### tags テーブル
- タグ情報

### reminders テーブル
- リマインダー情報

## 今後の実装予定

- [ ] カテゴリ・タグ機能
- [ ] リマインダー機能
- [ ] 進捗管理の強化
- [ ] ユーザー認証
- [ ] データ同期機能
- [ ] フロントエンドアプリケーション

## 開発者向け情報

### 新しいモジュールの作成

1. `backend/modules/`に新しいモジュールファイルを作成
2. `BaseModule`を継承
3. `initialize()`と`execute()`メソッドを実装
4. `ModuleManager`に登録

```python
from backend.core.base_module import BaseModule

class NewModule(BaseModule):
    def __init__(self):
        super().__init__("new_module")
    
    def initialize(self) -> bool:
        # 初期化処理
        return True
    
    def execute(self, action: str, params: dict) -> Any:
        # アクション実行
        pass
```

## ライセンス

MIT License
