import os

from flask import current_app, session
import requests
from sqlalchemy import desc
from applications.extensions import db
from applications.extensions.init_upload import photos
from applications.models import Photo
from applications.schemas import PhotoOutSchema
from applications.common.curd import model_to_dicts


def get_photo(page, limit):
    photo = Photo.query.order_by(desc(Photo.create_time)).paginate(page=page, per_page=limit, error_out=False)
    count = Photo.query.count()
    data = model_to_dicts(schema=PhotoOutSchema, data=photo.items)
    return data, count


def get_file_size(url):
    response = requests.head(url)
    if 'Content-Length' in response.headers:
        size = int(response.headers['Content-Length'])
        return size
    return None


def upload_one(filename, mime, file_url):
    # filename = photos.save(photo)
    # 获取当前用户
    user_id = session.get('user_id')
    print(user_id)
    size = get_file_size(file_url)
    if size is not None:
        photo = Photo(user_id=user_id, name=filename, href=file_url, mime=mime, size=size)
        db.session.add(photo)
        db.session.commit()
    return file_url


def delete_photo_by_id(_id):
    photo_name = Photo.query.filter_by(id=_id).first().name
    photo = Photo.query.filter_by(id=_id).delete()
    db.session.commit()
    upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
    os.remove(upload_url + '/' + photo_name)
    return photo
