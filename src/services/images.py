import hashlib
from typing import BinaryIO

from cloudinary import CloudinaryImage
import cloudinary
# from cloudinary.api import resource as res
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from src.conf.config import settings


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    filters = {'avatar': [
        {'aspect_ratio': '1.0', 'gravity': 'face', 'width': 500, 'zoom': '2', 'crop': 'thumb'},
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

    @staticmethod
    def generate_name_avatar(email: str):
        user_name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:14]
        return f'FRT-PHOTO-SHARE-AVATARS/{user_name}'
    
    @staticmethod
    def get_url_for_avatar(public_id, res, clipping: tuple[int, int] = (120, 120)):
            src_url = (
                cloudinary
                .CloudinaryImage(public_id)
                .build_url(width=clipping[0], height=clipping[1], crop='fill', version=res(public_id).get('version'))
                )

    @staticmethod
    def avatar_upload(file: BinaryIO, email: str, clipping: tuple[int, int] = (120, 120)) -> str:
        avatar_id = CloudImage.generate_name_avatar(email)
        # the public_id parameter is set according to the name of the current user and the FRT-PHOTO-SHARE folder:
        upload_result = cloudinary.uploader.upload(file.file, public_id=avatar_id, overwrite=True)

        return CloudImage.get_url_for_avatar(avatar_id, upload_result, clipping)

    @staticmethod
    def generate_name_image(email: str):
        image_name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        return f'FRT-PHOTO-SHARE-IMAGES/{image_name}'

    @staticmethod
    def image_upload(file, public_id: str):
        return cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)

    @staticmethod
    def get_url_for_image(public_id, r):
        src_url = cloudinary.CloudinaryImage(public_id).build_url(version=r.get('version'))
        return src_url


cloud_image = CloudImage()
# u2 =cloudinary.utils.cloudinary_url('test2_kwhfn6', transformation=cloud_image.filters['avatar'])
# u3 =cloudinary.utils.cloudinary_url('cld-sample-5', transformation=cloud_image.filters['bg'])
