from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException

from .data import (
    ACHIEVEMENTS,
    PREFECTURE_SUMMARIES,
    STAMP_HISTORY,
    STATIONS,
    USER_ACHIEVEMENTS,
    USER_PROFILE,
    Achievement,
    PrefectureSummary,
    Stamp,
    StampCreate,
    Station,
    UserProfile,
    UserProfileUpdate,
    next_stamp_id,
)

app = FastAPI(title="Michi-no-Eki API", version="0.1.0")


@app.get("/health")
def health_check():
    return {
        "service": "ok",
        "version": app.version,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }


@app.post("/auth/login")
def login(email: str, password: str):
    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password are required")
    return {"access_token": "demo-access-token", "expires_in": 3600}


@app.post("/auth/refresh")
def refresh_token(refresh_token: str):
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token is required")
    return {"access_token": "demo-access-token", "expires_in": 3600}


@app.get("/users/me", response_model=UserProfile)
def get_me():
    return USER_PROFILE


@app.patch("/users/me", response_model=UserProfile)
def update_me(payload: UserProfileUpdate):
    global USER_PROFILE
    USER_PROFILE = USER_PROFILE.model_copy(update=payload.model_dump(exclude_none=True, exclude_unset=True))
    return USER_PROFILE


@app.get("/users/{user_id}/achievements", response_model=List[Achievement])
def get_user_achievements(user_id: int):
    codes = USER_ACHIEVEMENTS.get(user_id, [])
    return [ach for ach in ACHIEVEMENTS if ach.code in codes]


@app.get("/stations", response_model=List[Station])
def list_stations(
    prefecture: str | None = None,
    tags: str | None = None,
    nearby_lat: float | None = None,
    nearby_lng: float | None = None,
    radius_km: float | None = None,
    page: int = 1,
    page_size: int = 50,
):
    stations = list(STATIONS.values())
    if prefecture:
        stations = [s for s in stations if s.prefecture == prefecture]
    if tags:
        tag_list = {tag.strip() for tag in tags.split(",") if tag.strip()}
        stations = [s for s in stations if tag_list.intersection(s.tags)]
    return stations[(page - 1) * page_size : page * page_size]


@app.get("/stations/{station_id}", response_model=Station)
def station_detail(station_id: int):
    station = STATIONS.get(station_id)
    if not station:
        raise HTTPException(status_code=404, detail="station not found")
    return station


@app.get("/prefectures", response_model=List[PrefectureSummary])
def prefecture_summaries():
    return PREFECTURE_SUMMARIES


@app.get("/prefectures/{prefecture}/stations", response_model=List[Station])
def prefecture_catalog(prefecture: str):
    return [s for s in STATIONS.values() if s.prefecture == prefecture]


@app.post("/stamps")
def create_stamp(payload: StampCreate):
    if payload.station_id not in STATIONS:
        raise HTTPException(status_code=404, detail="station not found")
    stamped_at = payload.stamped_at or datetime.now(tz=timezone.utc)
    stamp = Stamp(
        id=next_stamp_id(USER_PROFILE.id),
        user_id=USER_PROFILE.id,
        station_id=payload.station_id,
        stamped_at=stamped_at,
        source=payload.source,
        device_lat=payload.device_lat,
        device_lng=payload.device_lng,
    )
    STAMP_HISTORY.setdefault(USER_PROFILE.id, []).append(stamp)
    unlocked = [ach for ach in ACHIEVEMENTS if ach.code not in USER_ACHIEVEMENTS.get(USER_PROFILE.id, [])]
    USER_ACHIEVEMENTS.setdefault(USER_PROFILE.id, []).extend([ach.code for ach in unlocked])
    return {"stamp": stamp, "points_awarded": 10, "unlocked_achievements": unlocked}


@app.get("/users/me/stamps", response_model=List[Stamp])
def list_my_stamps(
    page: int = 1,
    page_size: int = 50,
    station_id: int | None = None,
):
    stamps = STAMP_HISTORY.get(USER_PROFILE.id, [])
    if station_id:
        stamps = [s for s in stamps if s.station_id == station_id]
    return stamps[(page - 1) * page_size : page * page_size]


@app.get("/achievements", response_model=List[Achievement])
def list_achievements():
    return ACHIEVEMENTS


@app.get("/progress/prefectures", response_model=List[PrefectureSummary])
def progress_prefectures():
    return PREFECTURE_SUMMARIES


@app.get("/progress/overall")
def progress_overall():
    total_stations = sum(summary.total_stations for summary in PREFECTURE_SUMMARIES)
    total_stamped = sum(summary.stamped_stations for summary in PREFECTURE_SUMMARIES)
    return {
        "total_stations": total_stations,
        "stamped": total_stamped,
        "completion_rate": total_stamped / total_stations if total_stations else 0,
        "total_points": USER_PROFILE.total_points,
        "total_stamps": USER_PROFILE.total_stamps,
    }
