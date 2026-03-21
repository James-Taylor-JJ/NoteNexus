from fastapi import FastAPI

from api.routes_notes_class import router as notes_router
from api.routes_datasets_class import router as datasets_router
from api.routes_search_class import router as search_router
from api.routes_tags_class import router as tags_router

app = FastAPI(
    title="NoteNexus API",
    version="0.1.0",
    description="FastAPI layer for notes, datasets, search, and tags.",
)

app.include_router(notes_router)
app.include_router(datasets_router)
app.include_router(search_router)
app.include_router(tags_router)


@app.get("/")
def root():
    return {"message": "NoteNexus API is running"}