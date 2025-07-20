from fastapi import UploadFile, HTTPException
import io

import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


async def upload_file(file: UploadFile):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="File name is required")

        file_content = await file.read()

        file_stream = io.BytesIO(file_content)

        blob = cloudinary.uploader.upload(
            file=file_stream,
            public_id=file.filename,
            resource_type="raw",
            folder="uploads",
            type="upload",
        )

        return blob.get("secure_url")

    except Exception as e:
        print(f"Exception in upload_file: {e}")
        raise HTTPException(status_code=500, detail="Error uploading file")
