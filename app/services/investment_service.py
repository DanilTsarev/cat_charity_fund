from datetime import datetime
from typing import Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.abstract_base import AbstractBase


async def make_donation(
    obj_in: AbstractBase, model_db: AbstractBase, session: AsyncSession
) -> AbstractBase:
    source_db_all = await session.execute(
        select(model_db)
        .where(model_db.fully_invested == False)  # noqa
        .order_by(model_db.create_date)
    )
    source_db_all = source_db_all.scalars().all()
    for source_db in source_db_all:
        obj_in, source_db = await distribute_donation(obj_in, source_db)
        session.add(obj_in)
        session.add(source_db)
    await session.commit()
    await session.refresh(obj_in)
    return obj_in


async def distribute_donation(
    obj_in: AbstractBase,
    obj_db: AbstractBase
) -> Set[AbstractBase]:
    calc_obj_in = obj_in.full_amount - obj_in.invested_amount
    calc_obj_db = obj_db.full_amount - obj_db.invested_amount
    if calc_obj_in > calc_obj_db:
        obj_in.invested_amount += calc_obj_db
        obj_db = await close_donation_or_project(obj_db)
    elif calc_obj_in == calc_obj_db:
        obj_in = await close_donation_or_project(obj_in)
        obj_db = await close_donation_or_project(obj_db)
    else:
        obj_db.invested_amount += calc_obj_in
        obj_in = await close_donation_or_project(obj_in)
    return obj_in, obj_db


async def close_donation_or_project(obj_db: AbstractBase) -> AbstractBase:
    obj_db.invested_amount = obj_db.full_amount
    obj_db.fully_invested = True
    obj_db.close_date = datetime.now()
    return obj_db
