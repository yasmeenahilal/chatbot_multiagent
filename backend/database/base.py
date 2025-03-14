from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine # to handle async function and api need async engine
from config.settings import Config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
# This is basic engine but we need async engine to handle async function
# engine = create_engine(
#     url = Config.DATABASE_URL,
#     echo = True
# )

engine = AsyncEngine(
    create_engine(
        url = Config.DATABASE_URL,
        echo = True
    )
)

async def init_db():
    async with engine.begin() as conn:
        # statement = text("SELECT 'helo';")
        # result = await conn.execute(statement)
        # print(result.all())
        from model.user import User

        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session()-> AsyncSession:
    Session = sessionmaker(
        bind = engine,
        class_ = AsyncSession,
        expire_on_commit = False
    )
    
    async with Session() as session:
        yield session