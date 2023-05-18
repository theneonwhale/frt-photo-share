import hashlib
import io
from typing import BinaryIO

import qrcode
import cloudinary
from cloudinary.uploader import upload

from src.conf.config import settings
from src.database.models import Image


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    filters = {
        'avatar': [
            {'aspect_ratio': '1.0', 'gravity': 'face', 'width': 500, 'zoom': '1', 'crop': 'thumb'},
            {'radius': 'max'},
            {'color': 'brown', 'effect': 'outline'}
        ],
        'black_white': [{'effect': 'grayscale'}],
        'delete_bg': [{'effect': 'bgremoval'}],
        'cartoonify': [{'effect': 'cartoonify'}],
        'oil_paint': [{'effect': 'oil_paint:100'}],
        'vector': [{'effect': 'vectorize:colors:5:corners:40:detail:1.0'}],
        'sepia': [{'effect': 'sepia:100'}],
        'outline': [
            {'width': 200, 'crop': 'scale'},
            {'color': 'blue', 'effect': 'outline:20:200'},
            {'color': 'yellow', 'effect': 'outline:15:200'}
        ]
    }

    @classmethod
    def generate_name_avatar(cls, email: str):
        user_name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:14]

        return f'FRT-PHOTO-SHARE-AVATARS/{user_name}'

    @classmethod
    def get_url_for_avatar(cls, public_id, res, clipping: tuple[int, int] = (120, 120)) -> str:
        return (
            cloudinary
            .CloudinaryImage(public_id)
            .build_url(width=clipping[0], height=clipping[1], crop='fill', version=res.get('version'))
        )

    @classmethod
    def avatar_upload(cls, file: BinaryIO, email: str, clipping: tuple[int, int] = (120, 120)) -> str:
        avatar_id = cls.generate_name_avatar(email)
        upload_result = cloudinary.uploader.upload(file, public_id=avatar_id, overwrite=True)

        return cls.get_url_for_avatar(avatar_id, upload_result, clipping)

    @classmethod
    def generate_name_image(cls, email: str, filename: str):
        image_name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        image_sufix = hashlib.sha256(filename.encode('utf-8')).hexdigest()[:12]

        return f'FRT-PHOTO-SHARE-IMAGES/{image_name}-{image_sufix}'

    @classmethod
    def image_upload(cls, file, public_id: str):
        return cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)

    @classmethod
    def get_url_for_image(cls, public_id, r):
        src_url = cloudinary.CloudinaryImage(public_id).build_url(version=r.get('version'))

        return src_url

    @classmethod
    def transformation(cls, image: Image, type):
        old_link = image.link
        break_point = old_link.find('/upload/') + settings.break_point
        image_name = old_link[break_point:]
        new_link = cloudinary.CloudinaryImage(image_name).build_url(transformation=CloudImage.filters[type.value])

        return new_link

    @classmethod
    def get_qrcode(cls, image: Image):
        qr_code = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=7,
            border=4,
        )
        url = image.link
        qr_code.add_data(url)
        qr_code.make(fit=True)
        img = qr_code.make_image(fill_color="black", back_color="white")
        output = io.BytesIO()
        img.save(output)
        output.seek(0)

        return output
