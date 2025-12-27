# API 仕様 (ドラフト)

本書はスタンプラリーアプリの初期 API 方針を示すドラフトです。認証は JWT（Bearer トークン）を前提とし、`Authorization: Bearer <token>` ヘッダーを必須とします。

## 認証
- **POST /auth/login**
  - 入力: email, password
  - 出力: access_token, expires_in
- **POST /auth/refresh**
  - 入力: refresh_token
  - 出力: access_token

## ユーザープロフィール
- **GET /users/me**
  - 認証必須。ログイン中ユーザーのプロフィール、統計（獲得スタンプ数、達成率、累積ポイント）を返す。
- **PATCH /users/me**
  - 入力: display_name, avatar_url, bio
  - 出力: 更新後ユーザープロフィール。
- **GET /users/{user_id}/achievements**
  - 指定ユーザーの解放済み実績リスト。pagination 対応。

## 道の駅一覧・詳細
- **GET /stations**
  - クエリ: `prefecture`, `tags`, `nearby_lat`, `nearby_lng`, `radius_km`, `page`, `page_size`。
  - 出力: 道の駅リスト（id, name, prefecture, coordinates, tags, 最新スタンプ数）。
- **GET /stations/{station_id}**
  - 出力: 道の駅詳細、営業時間/設備メモ、最新スタンプ統計。
- **GET /prefectures**
  - 出力: 都道府県ごとの道の駅サマリ (prefecture, total_stations, stamped_stations, completion_rate)。
- **GET /prefectures/{prefecture}/stations**
  - 出力: 指定都道府県の道の駅カタログ。ユーザーが取得済みかどうか（stamped: true/false）を含む。

## スタンプ登録
- **POST /stamps**
  - 認証必須。入力: `station_id`, `stamped_at` (任意。未指定はサーバー時刻)、`source` (gps/manual/campaign)、`device_lat`, `device_lng`。
  - バリデーション: 半径チェック（例: 1km 以内）、重複押印のクールダウン（例: 10 分）。
  - 出力: 新規スタンプ記録、付与ポイント、解放された実績一覧。
- **GET /users/me/stamps**
  - 認証必須。自身のスタンプ履歴を返す。クエリ: page, page_size, station_id, date_from, date_to。

## 達成率 / 実績
- **GET /achievements**
  - 出力: 実績マスター一覧 (code, title, description, criteria, points)。
- **GET /progress/prefectures**
  - 認証必須。都道府県ごとの達成率とスタンプ済み数を返す。
- **GET /progress/overall**
  - 認証必須。全体達成率、累計スタンプ数、残り未訪問数を返す。

## ヘルスチェック
- **GET /health**
  - 出力: service: "ok", version, timestamp。

## エラーレスポンス方針
- 4xx: リクエストエラー（バリデーション、認証、権限）。
- 5xx: サーバーエラー。
- フォーマット例:
  ```json
  { "error": { "code": "validation_error", "message": "latitude is required" } }
  ```

## 実装指針メモ
- OpenAPI (FastAPI) で自動ドキュメント生成し、`docs/` に静的エクスポートする。
- DB は SQLAlchemy + Alembic でマイグレーション管理。
- 位置情報は PostGIS の `ST_DWithin` を利用した近傍検索を想定。
- 認証ミドルウェアで JWT 検証、RBAC 拡張を可能にする設計を行う。
