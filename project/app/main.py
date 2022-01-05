from fastapi import Depends, FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from botocore.exceptions import ClientError
from starlette.responses import RedirectResponse
import io
import os
import uuid as uuid_pkg
import boto3
import logging
from typing import List
from app.db import get_session, init_db
from app.models import Files, FilesCreate

app = FastAPI()


@app.post("/upload/")
async def create_upload_files(file: UploadFile = File(...),session: AsyncSession = Depends(get_session)):
    client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get("AWSAccessKeyId"),
        aws_secret_access_key=os.environ.get("AWSSecretKey")
    )
    file_type = get_file_type(file.filename)
    file_read = await file.read()
    file_data = Files(name=file.filename)
    session.add(file_data)
    await session.commit()
    await session.refresh(file_data)
    try:
        client.upload_fileobj(io.BytesIO(file_read), 'hhd1vt4hk4ifebrv', '%s.%s' % (file_data.uuid,file_type))
    except ClientError as e:
        logging.error(e)
        return False

    return file_data

@app.get("/download/{uuid}/")
async def download_file(uuid:uuid_pkg.UUID, session: AsyncSession = Depends(get_session)):
    client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get("AWSAccessKeyId"),
        aws_secret_access_key=os.environ.get("AWSSecretKey")
    )
    result = await session.execute(select(Files).filter(Files.uuid == uuid))
    file = result.scalar_one_or_none()
    filename = None
    if file is None:
        return None
    for item in file:
        if item[0] == 'count_download':
            count_download = item[1]
        if item[0] == 'name': 
            filename = item[1]
        if item[0] == 'uuid':
            uuid = item[1]
    q = update(Files).where(Files.uuid == uuid)
    q = q.values(count_download=count_download+1)
    #q.execution_options(synchronize_session="fetch")
    await session.execute(q)
    await session.commit()
    file_type = get_file_type(filename)
    return RedirectResponse(client.generate_presigned_url('get_object',
                                     Params={'Bucket': 'hhd1vt4hk4ifebrv', 'Key':'%s.%s' % (uuid,file_type) },
                                     ExpiresIn=60))


@app.get("/upload/")
async def upload_file():
    content = """
<body>
    <form action="/upload/" enctype="multipart/form-data" method="post">
        <input name="file" type="file" >
        <input type="submit">
    </form>
</body>
    """
    return HTMLResponse(content=content)



@app.get("/", response_model=list[Files])
async def index(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Files))
    files = result.scalars().all()
    return [Files(name=file.name, uuid=file.uuid, count_download=file.count_download, id=file.id) for file in files]


def get_file_type(filename):
    split_data = filename.split('.')
    len_split_data = len(split_data)
    type = split_data[len_split_data-1]
    return type