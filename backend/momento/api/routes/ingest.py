"""Ingest API routes"""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, UploadFile, Query
from fastapi.responses import JSONResponse

from ..deps import verify_api_key
from ....store import ingest_rounds_batch, ingest_from_csv, ingest_from_json

router = APIRouter(prefix="/ingest")


@router.post("")
async def ingest_rounds(
    rounds: List[dict],
    source: Optional[str] = Query(None, description="Source override"),
    api_key: str = Depends(verify_api_key)
):
    count = ingest_rounds_batch(rounds, source)
    return {"message": f"Ingested {count} rounds", "count": count}


@router.post("/file")
async def ingest_file(
    file: UploadFile = File(...),
    source: Optional[str] = Query(None, description="Source override"),
    api_key: str = Depends(verify_api_key)
):
    import tempfile
    import os
    
    suffix = os.path.splitext(file.filename)[1]
    
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
    
    try:
        if suffix == ".csv":
            count = ingest_from_csv(tmp_path, source)
        elif suffix == ".json":
            count = ingest_from_json(tmp_path, source)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"Unsupported file type: {suffix}"}
            )
        
        return {"message": f"Ingested {count} rounds from file", "count": count, "filename": file.filename}
    finally:
        os.unlink(tmp_path)


@router.post("/batch")
async def batch_ingest(
    files: List[UploadFile] = File(...),
    source: Optional[str] = Query(None, description="Source override"),
    api_key: str = Depends(verify_api_key)
):
    import tempfile
    import os
    
    total_count = 0
    results = []
    
    for file in files:
        suffix = os.path.splitext(file.filename)[1]
        
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            if suffix == ".csv":
                count = ingest_from_csv(tmp_path, source)
            elif suffix == ".json":
                count = ingest_from_json(tmp_path, source)
            else:
                results.append({"filename": file.filename, "error": f"Unsupported file type: {suffix}"})
                continue
            
            total_count += count
            results.append({"filename": file.filename, "count": count})
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})
        finally:
            os.unlink(tmp_path)
    
    return {
        "message": f"Ingested {total_count} total rounds from {len(files)} files",
        "total_count": total_count,
        "results": results
    }