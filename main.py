from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io, traceback

app = FastAPI()

# Allow browser calls from anywhere (development). For production lock this to your domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    try:
        input_bytes = await file.read()
        input_image = Image.open(io.BytesIO(input_bytes)).convert("RGBA")
        output_image = remove(input_image)  # rembg (U2-Net) does the magic
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Processing failed")
