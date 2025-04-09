from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import JSON, String, Integer

engine = create_async_engine('postgresql+asyncpg://postgres:Mb20041995@localhost:5431/swapi')
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass


class SWapiPeople(Base):
    __tablename__ = 'swapi_people'
    id: Mapped[int]  =mapped_column(Integer, primary_key=True)
    birth_year: Mapped[str]
    eye_color: Mapped[str]
    # films: Mapped[list]
    gender: Mapped[str]
    hair_color: Mapped[str]
    height: Mapped[str]
    homeworld: Mapped[str]
    mass: Mapped[str]
    name: Mapped[str]
    skin_color: Mapped[str]
    species: Mapped[str]
    # starships: Mapped[str]
    # vehicles: Mapped[str]
    # json: Mapped[dict] = mapped_column(JSON)

async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_orm():
    await engine.dispose()