from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.project import project_crud


async def check_name_duplicate(
        room_name: str,
        session: AsyncSession,
) -> None:
    # Замените вызов функции на вызов метода.
    room_id = await project_crud.get_project_id_by_name(room_name, session)
    if room_id is not None:
        raise HTTPException(
            status_code=422,
            detail='Проект с таким именем уже существует!',
        )
