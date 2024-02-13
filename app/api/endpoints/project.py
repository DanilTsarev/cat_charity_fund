from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.validators import check_name_duplicate
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.project import project_crud
from app.models.donation import Donation
from app.schemas.project import (
    CharityProjectCreate,
    CharityProjectDB,
)
from app.services.investment_service import make_donation

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):

    await check_name_duplicate(charity_project.name, session)
    new_project = await project_crud.create(charity_project, session)
    new_project = await make_donation(new_project, Donation, session)
    return new_project