import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.models.database import User, RecommendationHistory
from app.models.schemas import HomeRequest, PartyRequest, JewelryRequest, RecommendationResponse
from app.services.gemini_service import generate

router = APIRouter(tags=["Planners"])

def save_result(db: Session, user: User, planner: str, request_data: dict, result: dict, source: str):
    result["source"] = source
    history = RecommendationHistory(user_id=user.id, planner_type=planner, request_json=json.dumps(request_data), result_json=json.dumps(result))
    db.add(history); db.commit(); db.refresh(history)
    result["history_id"] = history.id
    return result

@router.post("/generate-home", response_model=RecommendationResponse)
def generate_home(payload: HomeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result, source = generate("home", payload.model_dump())
    return save_result(db, user, "home", payload.model_dump(), result, source)

@router.post("/generate-party", response_model=RecommendationResponse)
def generate_party(payload: PartyRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result, source = generate("party", payload.model_dump())
    return save_result(db, user, "party", payload.model_dump(), result, source)

@router.post("/generate-jewelry", response_model=RecommendationResponse)
async def generate_jewelry(payload: str = Form(...), image: UploadFile | None = File(None), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        data = JewelryRequest.model_validate_json(payload).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid jewelry payload: {exc}")
    image_bytes = None
    mime = None
    if image:
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image uploads are allowed")
        image_bytes = await image.read()
        if len(image_bytes) > 8 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image must be 8 MB or smaller")
        mime = image.content_type
    result, source = generate("jewelry", data, image_bytes, mime)
    return save_result(db, user, "jewelry", data, result, source)

@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(RecommendationHistory).filter(RecommendationHistory.id == recommendation_id, RecommendationHistory.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"id": item.id, "planner": item.planner_type, "request": json.loads(item.request_json), "result": json.loads(item.result_json), "created_at": item.created_at}

@router.get("/history")
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(RecommendationHistory).filter(RecommendationHistory.user_id == user.id).order_by(RecommendationHistory.created_at.desc()).all()
    return [{"id": r.id, "planner": r.planner_type, "created_at": r.created_at, "summary": json.loads(r.result_json).get("summary", "")} for r in rows]
