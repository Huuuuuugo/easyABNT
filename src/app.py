from typing import Annotated
from pathlib import Path

import isbnlib
import aiofiles
from fastapi import FastAPI, HTTPException, status, Form
from fastapi.responses import HTMLResponse, FileResponse

from .services import OpenlibraryService, CrossrefService
from .schemas import Monograph, JournalArticle, ProceedingsArticle
from .reference_maker import format_journal_artice, format_proceedings_artice, format_monograph

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI()


@app.get("/")
async def index_page():
    async with aiofiles.open(STATIC_DIR / "html/index.html", "r", encoding="utf8") as f:
        return HTMLResponse(await f.read())


@app.get("/static/{subfolder}/{file}")
async def static_route(subfolder: str, file: str):
    file_path = STATIC_DIR / f"{subfolder}/{file}"
    if file_path.is_file() and file_path.exists():
        return FileResponse(file_path)

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/make-reference/")
async def make_reference_component(id: Annotated[str, Form()]):
    try:
        if isbnlib.is_isbn13(id) or isbnlib.is_isbn10(id):
            id = isbnlib.canonical(id)
            res = await OpenlibraryService.get_from_isbn(id)
            if isinstance(res, Monograph):
                return HTMLResponse(format_monograph(res))

        else:
            res = await CrossrefService.get_from_doi(id)
            if isinstance(res, JournalArticle):
                return HTMLResponse(format_journal_artice(res))

            elif isinstance(res, ProceedingsArticle):
                return HTMLResponse(format_proceedings_artice(res))

    except Exception as e:
        print(f"{e.__class__.__name__}: {e}")
        return HTMLResponse("<strong>Trabalho não encontrado.</strong>")
