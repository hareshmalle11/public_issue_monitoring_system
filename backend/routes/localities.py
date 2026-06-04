from fastapi import APIRouter, HTTPException
from services.supabase_client import SupabaseRestError, supabase

router = APIRouter()

@router.get("")
def list_localities() -> list[str]:
    try:
        # Fetch active localities from database
        rows = supabase.select("localities", params={"is_active": "eq.true", "order": "locality_name.asc"})
        return [row["locality_name"] for row in rows]
    except SupabaseRestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error fetching localities: {exc}") from exc
