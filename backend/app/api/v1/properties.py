from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()


@router.get("/properties")
async def get_properties(
        current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    tenant_id = getattr(current_user, "tenant_id", None) or "default_tenant"

    try:
        from app.core.database_pool import DatabasePool
        from sqlalchemy import text

        db_pool = DatabasePool()
        await db_pool.initialize()

        async with db_pool.get_session() as session:
            query = text("""
                 SELECT id, name
                 FROM properties
                 WHERE tenant_id = :tenant_id
                 ORDER BY name ASC
             """)
            result = await session.execute(query, {"tenant_id": tenant_id})
            rows = result.fetchall()
            return [{"id": row.id, "name": row.name} for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load properties: {str(e)}")
