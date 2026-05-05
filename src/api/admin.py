from fastapi import APIRouter, Depends
from src.api.deps import get_user_repo, get_sub_repo
from src.application.subscription import activate_premium
from src.infrastructure.db.repositories import SQLUserRepository, SQLSubscriptionRepository
from fastapi import HTTPException

router = APIRouter(prefix="/admin")


@router.post("/activate-premium/{username}")
async def admin_activate(username: str, user_repo: SQLUserRepository = Depends(get_user_repo),
                         sub_repo: SQLSubscriptionRepository = Depends(get_sub_repo)):
    user = await user_repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await activate_premium(user, user_repo, sub_repo)
    return {"status": "ok", "username": username, "is_premium": True}
