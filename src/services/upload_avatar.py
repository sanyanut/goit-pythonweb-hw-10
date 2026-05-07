import cloudinary
import cloudinary.uploader

from src.conf.config import settings

class UploadService:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )

    @staticmethod
    def upload_image(file, public_id: str) -> str:
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
