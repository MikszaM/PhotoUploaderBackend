# main.py
from fastapi import FastAPI, File, UploadFile, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import asyncio
import subprocess

app = FastAPI()

CODE='1234'

UPLOAD_DIR='/media/pi/MM/Photos'
REMOTE_PATH='remote:testrclone'
CONFIG_FILE='/home/pi/.config/rclone/rclone.conf'

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_cmd(command: str) -> str:
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    print(stderr)
    return stdout


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}


async def process_file(file_location: str):
    cmd_line = (
        f"rclone --config {CONFIG_FILE} copy '{file_location}' {REMOTE_PATH}"
    )
    _ = await run_cmd(cmd_line)

@app.post("/api/upload")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    x_auth_code: str = Header(None)
):
    # Validate header
    if not x_auth_code:
        raise HTTPException(status_code=400, detail="Missing X-Auth-Code header")

    # Optionally verify code here (e.g., lookup in DB)
    if x_auth_code != CODE:
        raise HTTPException(status_code=403, detail="Invalid code")

    # Save the uploaded file
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    background_tasks.add_task(process_file, file_location)
    print("task added...")
    return JSONResponse(
        status_code=200,
        content={"message": "Upload successful", "filename": file.filename}
    )

if __name__ == "__main__":
    uvicorn.run(app, 
                host="0.0.0.0", 
                port=443,
                ssl_keyfile='/etc/letsencrypt/live/weraimati.ddns.net/privkey.pem',
                ssl_certfile='/etc/letsencrypt/live/weraimati.ddns.net/fullchain.pem'
                )