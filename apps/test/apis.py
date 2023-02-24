from ninja import Router
from ninja.files import UploadedFile
from config.settings import STATIC_ROOT
from apps.views import File
from apps.test.func import requests_call

router = Router()

@router.post("/upload")
def upload(request, file: UploadedFile = File(...)):
    data = file.read()
    # 파일 읽은 거 폴더에 저장하고 
    # file_loc = 'apps/static/files/storage'
    path = STATIC_ROOT+'apps\\static\\files\\storage\\'+file.name
    ouput = open(path, 'wb')
    ouput.write(data)

    # func에서 경로만 수정해주고
    return requests_call(file.name)
    # return {'name': file.name, 'len': len(data)}