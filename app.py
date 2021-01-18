from fastapi import FastAPI, Request, File, UploadFile, HTTPException, Form
from typing import Optional, List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime
from functions import *
from starlette. responses import FileResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Optional[str] = None):
#     return {"item_id": item_id, "q": q}


@app.get("/download")
def download_ppt():
    exportdir = os.path.join(os.getcwd(), "exports")
    try:
        current_dir = os.listdir(exportdir)[0]
        print(f'Current directory: {current_dir}')
        filepath = os.path.join(exportdir, current_dir, "output.pptx")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Problem finding the ppt file - {e}")
    return FileResponse(filepath, media_type="appplication/octet-stream", filename="output.pptx")

@app.get("/purge")
def purge_directory():
    exportdir = os.path.join(os.getcwd(), "exports")
    current_dir = None
    try:
        for dirs in os.listdir(exportdir):
            current_dir = os.path.join(exportdir, dirs)
            if os.path.isdir(current_dir):
                shutil.rmtree(current_dir)
                print(f'removed directory: {current_dir}')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Couldn'nt remove directory - {e}")
    return {"directory removed" : current_dir}


@app.post("/generate_ppt")
async def perform_ppt_populate(subtext: str = Form(...), platenum: str = Form(...), thefiles: List[UploadFile] = File(...)):
    cwd = os.getcwd()
    timestamp = datetime.now().strftime("%Y-%d-%mT%H-%M-%S")
    exportdir = os.path.join(cwd, "exports", timestamp)
    os.mkdir(exportdir)
    uploaddir = os.path.join(cwd, "uploads")
    # purge the exports directory prior to upload
    purge_folder(uploaddir)
    # print(f'subtext: {subtext}')
    # print(f'platenum: {platenum}')
    for fi in thefiles:
        if fi.filename.endswith('.csv'):
            csv_file = fi.filename
        save_file_to_disk(fi, uploaddir)

    plot_types_list, stats_dct = process_stats_file(csv_file, uploaddir, exportdir)
    stats_dct['timestamp'] = timestamp
    stats_dct['subtext'] = subtext
    stats_dct['platenum'] = platenum
    embed_ppt_slides('ppt_template.pptx', 'output.pptx', plot_types_list, stats_dct, cwd, timestamp)
    return {'filename' : [fi.filename for fi in thefiles]}


if __name__ == "__main__":
    uvicorn.run('app:app', port=8200, host='0.0.0.0', reload=True)
