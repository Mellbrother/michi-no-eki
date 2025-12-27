from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel


class UserProfile(BaseModel):
    id: int
    display_name: str
    email: str
    avatar_url: str | None = None
    bio: str | None = None
    total_points: int
    total_stamps: int
    prefecture_completion_rate: float


class UserProfileUpdate(BaseModel):
    display_name: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    total_points: int | None = None
    total_stamps: int | None = None
    prefecture_completion_rate: float | None = None


class Station(BaseModel):
    id: int
    name: str
    prefecture: str
    latitude: float
    longitude: float
    tags: List[str] = []
    opened_at: str | None = None
    latest_stamp_count: int | None = None
    description: str | None = None
    facilities: List[str] = []


class PrefectureSummary(BaseModel):
    prefecture: str
    total_stations: int
    stamped_stations: int
    completion_rate: float


class Achievement(BaseModel):
    code: str
    title: str
    description: str
    criteria: str
    points: int


class Stamp(BaseModel):
    id: int
    user_id: int
    station_id: int
    stamped_at: datetime
    source: str
    device_lat: float | None = None
    device_lng: float | None = None


class StampCreate(BaseModel):
    station_id: int
    stamped_at: datetime | None = None
    source: str = "gps"
    device_lat: float | None = None
    device_lng: float | None = None


USER_PROFILE = UserProfile(
    id=1,
    display_name="旅人太郎",
    email="taro@example.com",
    avatar_url=None,
    bio="47都道府県制覇を目指しています。",
    total_points=120,
    total_stamps=8,
    prefecture_completion_rate=0.17,
)

STATIONS: Dict[int, Station] = {
    1: Station(
        id=1,
        name="道の駅 みちの里",
        prefecture="北海道",
        latitude=43.06417,
        longitude=141.34694,
        tags=["地元野菜", "温泉"],
        opened_at="2001-07-15",
        latest_stamp_count=254,
        description="広い駐車場と地元食材の直売所が人気。",
        facilities=["駐車場", "トイレ", "レストラン"],
    ),
    2: Station(
        id=2,
        name="道の駅 青葉の森",
        prefecture="青森県",
        latitude=40.82207,
        longitude=140.74736,
        tags=["キャンプ", "景観"],
        opened_at="2010-04-20",
        latest_stamp_count=98,
        description="青々とした森に囲まれた休憩スポット。",
        facilities=["キャンプ場", "売店"],
    ),
}

PREFECTURE_SUMMARIES: List[PrefectureSummary] = [
    PrefectureSummary(prefecture="北海道", total_stations=15, stamped_stations=4, completion_rate=0.27),
    PrefectureSummary(prefecture="青森県", total_stations=9, stamped_stations=2, completion_rate=0.22),
]

ACHIEVEMENTS: List[Achievement] = [
    Achievement(
        code="first_stamp",
        title="初めてのスタンプ",
        description="最初の道の駅スタンプを獲得",
        criteria="スタンプを1つ取得",
        points=10,
    ),
    Achievement(
        code="hokkaido_collector",
        title="北海道コレクター",
        description="北海道内の道の駅スタンプを5つ集める",
        criteria="北海道のスタンプ5個",
        points=30,
    ),
]

USER_ACHIEVEMENTS: Dict[int, List[str]] = {1: ["first_stamp"]}

STAMP_HISTORY: Dict[int, List[Stamp]] = {
    1: [
        Stamp(
            id=1,
            user_id=1,
            station_id=1,
            stamped_at=datetime(2024, 4, 1, 10, 0, tzinfo=timezone.utc),
            source="gps",
            device_lat=43.06,
            device_lng=141.34,
        ),
    ]
}


def next_stamp_id(user_id: int) -> int:
    history = STAMP_HISTORY.setdefault(user_id, [])
    return (history[-1].id + 1) if history else 1
