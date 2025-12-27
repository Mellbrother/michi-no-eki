# アーキテクチャ概要

## 全体像
- モバイルアプリ（React Native/Expo）で現在地取得・スタンプ押印・都道府県別の達成状況閲覧を提供。
- FastAPI ベースのバックエンドが認証、スタンプ履歴、道の駅メタデータを管理。
- データベースは PostgreSQL を想定し、スタンプ・ユーザー・道の駅・実績を正規化して保持。
- CI/CD（GitHub Actions）で lint / test を自動実行し、将来的にビルド・デプロイを追加予定。

## 主要コンポーネント
- **モバイルクライアント**: 位置情報取得、スタンプ押印 UI、プロフィール/達成率画面、オフラインキャッシュ。
- **API サーバー**: ユーザー管理、道の駅検索、スタンプ登録、都道府県別カタログと達成率集計 API を提供。
- **データベース層**: PostgreSQL。地理情報拡張 (PostGIS) を検討し、道の駅座標で距離検索を可能にする。
- **ジョブ/バッチ**: 達成率再計算、実績ロック解除処理、データ同期。

## データモデル草案
- **users**: id, display_name, email, avatar_url, bio, total_points, created_at.
- **stations**: id, name, prefecture, latitude, longitude, tags, opened_at.
- **stamps**: id, user_id, station_id, stamped_at, source (gps / manual / campaign).
- **achievements**: id, code, title, description, criteria, points.
- **user_achievements**: id, user_id, achievement_id, unlocked_at.
- **prefecture_stats (派生ビュー)**: prefecture, total_stations, stamped_stations, completion_rate.

## セキュリティ・品質
- JWT 認証 (OAuth 2.0 Password / Social Login を将来的に追加)。
- 入力バリデーションは Pydantic スキーマで統一。
- lint: Ruff / ESLint、test: pytest / Jest を標準とする。

## 今後の拡張
- Push 通知、オフラインモード強化、PWA 対応。
- オープンデータ連携による道の駅情報自動更新。
- 画像アップロード（スタンプ画像やプロフィール）。
