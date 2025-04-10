from fastapi import FastAPI, UploadFile, HTTPException, Form, Request, Body
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from http import HTTPStatus
from pathlib import Path
import import_media as IM
from typing import Annotated
import anyio
import os
import uvicorn


app = FastAPI()


DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))
UI_DIR = Path(os.environ.get("UI_DIR", os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'ui'))))
THUMBNAIL_FONT_FILE = Path(os.environ.get("THUMBNAIL_FONT_FILE", "font.ttf"))

DATA_DIR.mkdir(parents=True, exist_ok=True)

if not THUMBNAIL_FONT_FILE.is_file():
    THUMBNAIL_FONT_FILE = None


async def save_upload_file(
    file: UploadFile,
    path: Path,
    chunk_size: int = 1024*64,
):
    try:
        async with await anyio.open_file(path, "wb") as f:
            while True:
                # Read a chunk from the uploaded file
                chunk = await file.read(chunk_size)
                if not chunk:
                    break  # End of file
                # Write the chunk to the destination file
                await f.write(chunk)
        return path
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error saving file:{str(e)}",
        )
    finally:
        # Clean up the uploaded file after processing
        await file.close()


app = FastAPI()


@app.middleware("http")
async def decode_key_middleware(request: Request, call_next):
    if request.url.path.endswith("/key.bin"):
        key = request.cookies.get("key")
        decoded_bytes = bytes.fromhex(key)

        return Response(
            content=decoded_bytes,
            media_type="application/octet-stream",
        )
    else:
        return await call_next(request)


@app.post("/api/init")
async def init(
    key: Annotated[str, Body()],
):
    async with IM.Tmp() as tmp:
        # should be DB.clear(), but clear is dangerous
        await IM.DB(key, tmp, DATA_DIR).print()


@app.put("/api/media")
async def upload_media(
    kind: Annotated[IM.MediaKind, Form()],
    file: UploadFile,
    key: Annotated[str, Form()],
    title: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    thumbnail: UploadFile | None = None,
    bitrate: Annotated[str | None, Form()] = None,
    hls_time: Annotated[int | None, Form()] = None,
    resize: Annotated[str | None, Form()] = None,
    quality: Annotated[int | None, Form()] = None,
    encoding: Annotated[str | None, Form()] = None,
    author: Annotated[str | None, Form()] = None,
    language: Annotated[str | None, Form()] = None,
    toc_title: Annotated[str | None, Form()] = None,
    max_ctl: Annotated[int | None, Form()] = None,
):
    async with IM.Tmp() as tmp:
        dir = tmp.dir()

        file_path = await save_upload_file(file, dir / file.filename)
        thumbnail_path = await save_upload_file(
            thumbnail, dir / thumbnail.filename) if thumbnail else None

        await IM.import_media(
            kind=kind,
            file=file_path,
            key=key,
            title=title,
            description=description,
            thumbnail=thumbnail_path,
            thumbnail_font=THUMBNAIL_FONT_FILE,
            bitrate=bitrate,
            hls_time=hls_time,
            resize=resize,
            quality=quality,
            encoding=encoding,
            author=author,
            language=language,
            toc_title=toc_title,
            max_ctl=max_ctl,
            # Other options
            root_dir=DATA_DIR,
            tmp=tmp,
        )


@app.delete("/api/media")
async def delete_media(
    key: Annotated[str, Body()],
    uids: Annotated[list[str], Body()],
):
    async with IM.Tmp() as tmp:
        await IM.DB(key, tmp, DATA_DIR).remove(uids)


@app.patch("/api/media")
async def update_media(
    key: Annotated[str, Form()],
    uid: Annotated[str, Form()],
    title: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    thumbnail: UploadFile | None = None,
):
    async with IM.Tmp() as tmp:
        async with IM.DB(key, tmp, DATA_DIR) as db:
            record = next((r for r in db if r['uid'] == uid), None)

            if record is None:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

            if title:
                record['title'] = title

            if description:
                record['description'] = description

            if thumbnail:
                path_1 = await save_upload_file(
                    thumbnail, tmp.file(thumbnail.filename))
                path_2 = tmp.file(".webp")
                await IM.Cmd.image_to_thumbnail(path_1, path_2)
                path_3 = DATA_DIR / record['thumbnail']
                await IM.Cmd.encrypt_file(path_2, path_3, key, record['iv'])


@app.patch("/api/note")
async def update_note(
    key: Annotated[str, Body()],
    uid: Annotated[str, Body()],
    content: Annotated[str, Body()],
):
    async with IM.Tmp() as tmp:
        async with IM.DB(key, tmp, DATA_DIR) as db:
            record = next((r for r in db if r['uid'] == uid), None)

            if record is None:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

            pt_path = tmp.file()
            pt_path.write_text(content)
            await IM.Cmd.encrypt_file(
                pt_path, DATA_DIR / record['file'], key, record['iv'])


@app.put("/api/note")
async def create_note(
    key: Annotated[str, Form()],
    title: Annotated[str, Form()],
    content: Annotated[str, Form()],
    description: Annotated[str | None, Form()] = None,
    thumbnail: UploadFile | None = None,
):
    async with IM.Tmp() as tmp:
        pt_path = tmp.file('.md')
        pt_path.write_text(content)

        thumbnail_path = await save_upload_file(
            thumbnail, tmp.file(thumbnail.filename)) if thumbnail else None

        await IM.NoteImporter(
            file=pt_path,
            key=key,
            tmp=tmp,
            title=title,
            description=description,
            thumbnail=thumbnail_path,
            thumbnail_font=THUMBNAIL_FONT_FILE,
            root_dir=DATA_DIR,
        ).consume()


# Serve static files at last
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")
app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run(app)
