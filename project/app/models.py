from sqlmodel import SQLModel, Field
import uuid as uuid_pkg
from typing import Optional


class FilesBase(SQLModel):
    name: str


class Files(FilesBase, table=True):
    id: int = Field(default=None, primary_key=True)
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        index=True,
        nullable=False,
    )
    count_download: int = Field(default=0)


class FilesCreate(FilesBase):
    pass
