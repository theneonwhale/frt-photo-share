from cloudinary import CloudinaryImage
import cloudinary
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
        {'aspect_ratio': "1.0", 'gravity': "face", 'width': 500, 'zoom': '2', 'crop': "thumb"},
        {'radius': "max"},
        {'color': "brown", 'effect': "outline"}
        ],
        'black_white': [{'effect': "grayscale"}],
        'delete_bg': [{'effect': "bgremoval"}],
        'cartoonify': [{'effect': "cartoonify"}],
        "oil_paint": [{'effect': "oil_paint:100"}],
        'vector': [{'effect': 'vectorize:colors:5:corners:40:detail:1.0'}],
        'sepia': [{'effect': "sepia:100"}],
        'outline': [
            {'width': 200, 'crop': "scale"},
            {'color': "blue", 'effect': "outline:20:200"},
            {'color': "yellow", 'effect': "outline:15:200"}
        ]
    }


cloud_image = CloudImage()
# u2 =cloudinary.utils.cloudinary_url("test2_kwhfn6", transformation=cloud_image.filters['avatar'])
# u3 =cloudinary.utils.cloudinary_url("cld-sample-5", transformation=cloud_image.filters['bg'])
