from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.validators import (
    check_full_amount_is_less_than_invested,
    check_name_duplicate,
    check_project_exists,
    check_project_is_fully_invested,
    is_project_a_donating,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.project import project_crud
from app.models.donation import Donation
from app.schemas.project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
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
    """Доступ: SuperUser.

    Создание нового проекта."""
    await check_name_duplicate(charity_project.name, session)
    new_project = await project_crud.create(charity_project, session)
    new_project = await make_donation(new_project, Donation, session)
    return new_project


@router.get(
    '/',
    response_model_exclude_none=True,
    response_model=List[CharityProjectDB],
)
async def get_all_projects(session: AsyncSession = Depends(get_async_session)):
    """Доступ: All Users.

    Возвращает список всех проектов."""
    charity_projects = await project_crud.get_multi(session)
    return charity_projects


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Доступ: SuperUser.

    Нельзя модифицировать закрытые проекты,
    изменять даты создания и закрытия проектов,
    нельзя установить требуемую сумму меньше уже внесённой."""
    charity_project = await check_project_exists(project_id, session)
    charity_project = await check_project_is_fully_invested(
        charity_project, session
    )
    if obj_in.name:
        await check_name_duplicate(obj_in.name, session)
    if not obj_in.full_amount:
        charity_project = await project_crud.update(
            charity_project, obj_in, session
        )
        return charity_project
    await check_full_amount_is_less_than_invested(
        obj_in.full_amount, charity_project.invested_amount, session
    )
    charity_project = await project_crud.update(
        charity_project, obj_in, session
    )
    charity_project = await make_donation(charity_project, Donation, session)
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Доступ: SuperUser.

    Удаляет проект. Нельзя удалить проект,
    в который уже были инвестированы средства,
    его можно только закрыть."""
    charity_project = await check_project_exists(project_id, session)
    await is_project_a_donating(charity_project, session)
    charity_project = await project_crud.remove(charity_project, session)
    return charity_project
