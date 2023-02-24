from django.shortcuts import render
from ninja import NinjaAPI, File
from apps.test.apis import router as test
from apps.test.func import requests_call
from . import models
import json, os
from config.settings import STATIC_ROOT

# Ninja API
api = NinjaAPI()

api.add_router("/test", test)

# 메인 화면
def index(request):
    test = 1 + 1
    return render(request, "main.html", {'test' : test})

# try except러 예외처리 해야겠다
def uploadFile(request):
    if request.method == 'POST':
        title = request.POST['title']
        file = request.FILES['file']
        file_name = str(file) # 파일 이름에 () 없어야함

        # pdf 있으면 다시 저장 안하기
        if(file_name not in os.listdir(STATIC_ROOT+'media\\PDF')):
            pdf = models.FileUpload(
                title = title,
                file = file
            )
            # PDF 파일 저장
            pdf.save()
        
        # 돌려서 최종 결과물 넣어주기
        data = requests_call(file_name)

        # 1. 결과물 바로 dump해서 보여주기
        result = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)

        return render(request, "upload-file.html", context = {
            'files' : result
        }
        )
        # 2. 결과물 저장 장소에서 가져오기
        # jsonFile = getJson(file_name)
        #     return render(request, 'Core/upload-file.html', context=
        #                   {
        #                       'Convert' : jsonFile
        #                   })


    else:
        return render(request, "main.html", context = {
            'files' : None
        }
        )


def getJson(file_name):
    file_name = file_name.split('.')[0]
    file_path = STATIC_ROOT+'media\\Result\\' + file_name +".json" 
    jsonFile = open(file_path, 'r', encoding='UTF-8')
    return jsonFile