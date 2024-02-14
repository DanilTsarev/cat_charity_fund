from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.project import project_crud
from app.models.charity_project import CharityProject


async def check_name_duplicate(
    room_name: str,
    session: AsyncSession,
) -> None:
    room_id = await project_crud.get_project_id_by_name(room_name, session)
    if room_id is not None:
        raise HTTPException(
            status_code=400, detail='Проект с таким именем уже существует!'
        )


async def check_project_exists(
    charity_project_id: int,
    session: AsyncSession,
) -> CharityProject:
    charity_project = await project_crud.get(charity_project_id, session)
    if charity_project is None:
        raise HTTPException(status_code=404, detail='Проект не найден!')
    return charity_project


async def check_project_is_fully_invested(
    charity_project: CharityProject,
    session: AsyncSession,
) -> CharityProject:
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!',
        )
    return charity_project


async def check_full_amount_is_less_than_invested(
    new_full_amount: int,
    project_amount_in_db: int,
    session: AsyncSession
) -> None:
    if new_full_amount is not None and new_full_amount < project_amount_in_db:
        raise HTTPException(
            status_code=422,
            detail='Установите смумму не меньше уже внесённой в проект',
        )


async def is_project_a_donating(
    charity_project: CharityProject,
    session: AsyncSession,
) -> None:
    if charity_project.invested_amount:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!',
        )
