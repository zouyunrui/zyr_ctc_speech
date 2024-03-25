import os
import oss2
from flask import Blueprint, request, render_template, jsonify, current_app, session
from applications.config import BaseConfig
from applications.common.utils.http import fail_api, success_api, table_api
from applications.common.utils.rights import authorize
from applications.extensions import db
from applications.models import Photo
from applications.common.utils import upload as upload_curd
from ..system.utils.filename_util import get_filename

bp = Blueprint('adminSpeech', __name__, url_prefix='/speech')
# 初始化阿里云对象
auth = oss2.Auth(BaseConfig.ACCESS_KEY_ID, BaseConfig.ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, 'https://' + BaseConfig.ENDPOINT, BaseConfig.BUCKET_NAME)

# 指定Header。
headers = dict()
# 指定Accept-Encoding。
headers['Accept-Encoding'] = 'utf-8'

#  语音管理
@bp.get('/')
@authorize("system:speech:main")
def index():
    return render_template('system/speech/speech.html')


#  语音数据
@bp.get('/table')
@authorize("system:speech:main")
def table():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    data, count = upload_curd.get_photo(page=page, limit=limit)
    return table_api(data=data, count=count)


#   上传
@bp.get('/upload')
@authorize("system:speech:add", log=True)
def upload():
    return render_template('system/speech/speech_add.html')


#   上传接口
@bp.post('/upload')
@authorize("system:speech:add", log=True)
def upload_api():
    # 获取当前用户
    user_id = session.get('user_id')
    print(user_id)
    if 'file' in request.files:
        photo = request.files['file']
        mime = request.files['file'].content_type
        file_extension = mime.split('/')[1]
        # 生成唯一的文件名
        # filename = upload_curd.upload_one(photo, mime)
        filename = get_filename() + '.' + file_extension
        # 将文件上传到阿里云OSS
        bucket.put_object(filename, photo)

        # try:
        #     bucket.put_object(filename, photo, headers={'Content-Type': mime})
        # except oss2.exceptions.OssError:
        #     return fail_api(msg="上传失败")

        #  构造文件 URL
        #file_url = f"https://{BaseConfig.ENDPOINT}.{BaseConfig.ENDPOINT}/{filename}"
        file_url = bucket.sign_url('GET', filename, 60, slash_safe=True, headers=headers)
        upload_curd.upload_one(filename,mime,file_url)
        res = {
            "msg": "上传成功",
            "code": 0,
            "success": True,
            "data":
                {"src": file_url}
        }

        return jsonify(res)
    return fail_api()


#    图片删除
@bp.route('/delete', methods=['GET', 'POST'])
@authorize("system:speech:delete", log=True)
def delete():
    _id = request.form.get('id')
    res = upload_curd.delete_photo_by_id(_id)
    if res:
        return success_api(msg="删除成功")
    else:
        return fail_api(msg="删除失败")


# 图片批量删除
@bp.route('/batchRemove', methods=['GET', 'POST'])
@authorize("system:speech:delete", log=True)
def batch_remove():
    ids = request.form.getlist('ids[]')
    photo_name = Photo.query.filter(Photo.id.in_(ids)).all()
    upload_url = current_app.config.get("UPLOADED_PHOTOS_DEST")
    for p in photo_name:
        os.remove(upload_url + '/' + p.name)
    photo = Photo.query.filter(Photo.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()
    if photo:
        return success_api(msg="删除成功")
    else:
        return fail_api(msg="删除失败")
