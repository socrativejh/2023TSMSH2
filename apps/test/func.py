import requests
import json
import os
import re
from config.settings import STATIC_ROOT
from config.settings import env



# 테이블 안 (주로 비고 위)에 있는 쓸데없는 문자열이 key값으로 추출되는 것을 방지하기 위함
def delete_unnecessary_string(file_path):
    # 먼저 pdf 파일 nanonets로 돌려서 만들어진 json파일을 load
    try:
        with open(file_path, 'r',encoding='cp949') as file:
            data = json.load(file)
    except:
        pass

    try:
        with open(file_path, 'r',encoding='utf-8') as file:
            data = json.load(file)
    except:
        pass

    try:
        with open(file_path, 'r',encoding='euc-kr') as file:
            data = json.load(file)
    except:
        pass

    total_page_num = len(data['result'])
    table_num = []
    for i in range(total_page_num):
        table_num.append(len(data['result'][i]['prediction']))

    # page 별로
    for i in range(total_page_num):
        # table 별로
        for j in range(table_num[i]):
            # table 별 총 cell 개수 구하기
            cell_num = len(data['result'][i]['prediction'][j]['cells'])
            # 먼저 '비고'의 row, col 값을 구한다
            for x in range(cell_num):
                if("비 고" in data['result'][i]['prediction'][j]['cells'][x]['text'] or "비고" in data['result'][i]['prediction'][j]['cells'][x]['text']):
                    find_word_row = data['result'][i]['prediction'][j]['cells'][x]['row']
                    find_word_col = data['result'][i]['prediction'][j]['cells'][x]['col']
                    break
                
            # 나머지 중에서 '비고'와 같은 적은 row값 같은 col값을 가진 것을 '@@@'으로 바꾸어준다
            for x in range(cell_num):
                try:
                    if(data['result'][i]['prediction'][j]['cells'][x]['row'] < find_word_row
                        and data['result'][i]['prediction'][j]['cells'][x]['col'] == find_word_col):
                        data['result'][i]['prediction'][j]['cells'][x]['text'] = '@@@'
                except:
                    print("비고 is not extracted in this table")
    return data

def get_architect_info(file_path):
    # 쓸데없는 문자열을 @@@으로 바꾸어준 데이터를 가져온다
    data = delete_unnecessary_string(file_path)
    
    # 파일의 page 개수, 각 page 별 table 개수 저장
    total_page_num = len(data['result'])
    table_num = []
    for i in range(total_page_num):
        table_num.append(len(data['result'][i]['prediction']))

    col_num = []
    extracted_text = []
    result_dictionary = {}

    # 각 테이블마다 몇개의 col 개수가 있는지 확인
    for i in range(total_page_num):
        for j in range(table_num[i]):
            max_col = 0
            cell_num = len(data['result'][i]['prediction'][j]['cells'])
            for k in range(cell_num):
                if (max_col < data['result'][i]['prediction'][j]['cells'][k]['col']):
                    max_col = data['result'][i]['prediction'][j]['cells'][k]['col']
            col_num.append(max_col)

    # text 뽑아서 dic형태로 만들기
    # page 별로
    for i in range(total_page_num):
        page = "page: " + str(i)
        page_dictionary = {page : []}
        # table 별로
        for j in range(table_num[i]):
            table = "table: " + str(j)
            table_dictionary = {table: []}
            # table 별 총 cell 개수 구하기
            cell_num = len(data['result'][i]['prediction'][j]['cells'])
            # 사전에 구해둔 col의 개수만큼 for-loop 돌린다.
            # col별로 text extract해서 저장할 것이기 때문에
            for k in range(col_num[j]):
                extracted_text = []
                # 각 cell 별로 검사하면서 col 값이 같으면 list에 저장한다.
                for x in range(cell_num):
                    if(data['result'][i]['prediction'][j]['cells'][x]['col'] == k + 1): # 원문 json에서는 col값이 1부터 시작하기 때문에 k + 1
                        if(data['result'][i]['prediction'][j]['cells'][x]['text'] == "@@@"): # 미리 처리해 둔 값은 그냥 pass
                            pass
                        else:
                            extracted_text.append(data['result'][i]['prediction'][j]['cells'][x]['text'].replace("\n"," ")) # col 별로 text 저장
                # table 별로 col 들로 부터 추출된 text 저장
                table_dictionary[table].append(extracted_text)
            # page 별로 table 들로 부터 추출된 text 저장
            page_dictionary[page].append(table_dictionary)
        result_dictionary.update(page_dictionary)

    return result_dictionary


############################################################################################
######### 평균적인 index_value값 구하기 #####################################################
def get_index_value(file_path):
    try:
        with open(file_path, 'r',encoding='cp949') as file:
            data2 = json.load(file)
    except UnicodeDecodeError as e:
        pass

    try:
        with open(file_path, 'r',encoding='utf-8') as file:
            data2 = json.load(file)
    except UnicodeDecodeError as e:
        pass
    
    try:
        with open(file_path, 'r',encoding='euc-kr') as file:
            data2 = json.load(file)
    except UnicodeDecodeError as e:
        pass
    
    # col값을 기준으로 정리된 데이터 가져오기
    data = get_architect_info(file_path)

    # 파일의 page 개수, 각 page 별 table 개수 저장
    total_page_num = len(data2['result'])
    table_num = []

    # key값에 꼭 포함시켜야하는 단위 정의
    units = ['m2','hr','m3','mmAq','kg','kcal','Hz','Ph','V',
                    'min','대','Kg / h','kW X EA','kPa','set','m² / h','Ph - V - Hz','번호',
                    'kw','$','Lit','mm',
                    '#','cm2','cm'
    ]

    # page당 table개수 구하기
    for i in range(total_page_num):
        table_num.append(len(data2['result'][i]['prediction']))

    # 비어있는 list 미리 지워주기 (index oot of range error 나지 않게끔)
    for i in range(total_page_num):
        page_string = "page: " + str(i)
        for j in range(table_num[i]):
            table_string = "table: " + str(j)
            x = 0
            for k in range(len(data[page_string][j][table_string])):
                if  len(data[page_string][j][table_string][x]) == 0:
                    del data[page_string][j][table_string][x]
                else :
                    x = x + 1
    result_list = []
    # page 
    for i in range(total_page_num):
        page_string = "page: " + str(i)
        page_result = []
        # table 단위로 동일한 index_value가지게 한다
        for j in range(table_num[i]):
            table_string = "table: " + str(j)
            index_value_list = []
            for k in range(len(data[page_string][j][table_string])):
                for unit in units:
                        try:
                            # 해당 단위가 있는 위치를 구한다 (for문 range에 넣어야하므로 +1)
                            unit_index = data[page_string][j][table_string][k].index(unit) + 1
                            index_value_list.append(unit_index)
                        except:
                            pass
            # **가장 많이** 나온 값(단위의 위치)를 index_value로 정한다
            # 단위의 위치를 구하는 이유는 보통 단위에서 key값이 잘리기 때문에 key값에 들어가야할 단위가 value에
            # 포함되지 않게 하기 위함이다
            count_list = [] 
            for x in index_value_list:
                count_list.append(index_value_list.count(x))
    
            if(len(count_list)!=0):
                page_result.append(index_value_list[count_list.index(max(count_list))])
            else:
                page_result.append(0)
        result_list.append(page_result)
    return result_list

############################################################################################
############################################################################################


# row로 정리하되 index(col)값은 dic의 key값으로 들어가게끔 가공
def data_processing(file_path):
    try:
        with open(file_path, 'r',encoding='cp949') as file:
            data2 = json.load(file)
    except UnicodeDecodeError as e:
        pass

    try:
        with open(file_path, 'r',encoding='utf-8') as file:
            data2 = json.load(file)
    except UnicodeDecodeError as e:
        pass
    
    try:
        with open(file_path, 'r',encoding='euc-kr') as file:
            data2 = json.load(file)
    except UnicodeDecodeError as e:
        pass
    
    # col값을 기준으로 정리된 데이터 가져오기
    data = get_architect_info(file_path)

    # table 기준으로 index_value 구해놓은거 가져오기
    index_value_list = get_index_value(file_path)

    # 파일의 page 개수, 각 page 별 table 개수 저장
    total_page_num = len(data2['result'])
    table_num = []
    for i in range(total_page_num):
        table_num.append(len(data2['result'][i]['prediction']))
  
    result_dictionary = {}

    # 비어있는 list 미리 지워주기 (index oot of range error 나지 않게끔)
    for i in range(total_page_num):
        page_string = "page: " + str(i)
        for j in range(table_num[i]):
            table_string = "table: " + str(j)
            x = 0
            for k in range(len(data[page_string][j][table_string])):
                if  len(data[page_string][j][table_string][x]) == 0:
                    del data[page_string][j][table_string][x]
                else :
                    x = x + 1
    # page 
    for i in range(total_page_num):
        page_string = "page: " + str(i)
        page_dictionary = {page_string : []}
        # table
        for j in range(table_num[i]):
            table_string = "table: " + str(j)
            table_dictionary = {table_string: []}
            index_value = index_value_list[i][j]

            # col개수
            # 맨 처음 한번 돌려서 row마다 각각의 col값이 들어가게 하기 위함
            # row만큼 [{"기호": },{"기호": },{"기호": }...] 이렇게 미리 dic를 만들어 놓기 위해서
            for k in range(1):
                row_dictionary = {}
                col_string = ""
                # 단위 처리 (띄어쓰기): key값 만들기
                # col값에 숫자가 있으면 거기서 자르기 (정확한 key값을 만들기 위해)
                hasNumber = lambda stringVal: any(elem.isdigit() for elem in stringVal)
                not_null_value = 0
                small_amount_check = [0,1,2]
                if(index_value == 0):
                    units = ['m2','hr','m3','mmAq','kg','kcal','Hz','Ph','V',
                            'min','대','Kg / h','kW X EA',
                            'kw','$','Lit',
                            '#','cm2','cm'
                    ]

                    for unit in units:
                            try:
                                unit_index = data[page_string][j][table_string][k].index(unit) + 1
                            except:
                                unit_index = -1
                                pass

                    # key값을 구하기 위한 index_value구하기 (IndexError: list index out of range 방지)
                    if(len(data[page_string][j][table_string][k]) in small_amount_check):
                        index_value = len(data[page_string][j][table_string][k])
                    else:    
                        # 단위는 주로 3번째까지 나오기 때문에 이렇게 작성함
                        index_value = 3
                        # col이 index 2이하에만 있는 경우도 있다 (숫자값이 있는 순서가 오면 거기까지를 index_value로 본다)
                        for y in range(2):
                            if(hasNumber(data[page_string][j][table_string][k][y+1])):
                                index_value = y+1
                                break

                    # 단위는 꼭 key값으로 포함시키기                
                    if(unit_index > index_value):
                        index_value = unit_index
                
                # col_string 만들기(key값)
                for x in range(index_value):
                        if(data[page_string][j][table_string][k][x] == ""):
                            pass
                        elif(data[page_string][j][table_string][k][x] == "비고" or data[page_string][j][table_string][k][x] == "비 고"):
                            col_string = "비고"
                            break
                        elif("기호" in data[page_string][j][table_string][k][x] or "기 호" in data[page_string][j][table_string][k][x]):
                            col_string = "기호"
                            break
                        else:
                            # 값이 있는 경우가 처음이면 괄호 없애주고
                            if(not_null_value == 0):
                                replace_string = data[page_string][j][table_string][k][x]
                                if(replace_string.count("(") %2 == 1):
                                    replace_string = replace_string.replace("(","")
                                if(replace_string.count(")") %2 == 1):
                                    replace_string = replace_string.replace(")","")
                                col_string += replace_string + " "
                            # 값이 있는 경우가 처음이 아니면 괄호 없애주고 (있는 경우가 있음) 그 후에 제대로된 괄호를 더해준다
                            else:
                                replace_string = data[page_string][j][table_string][k][x].replace("(","").replace(")","")
                                col_string += " ( " + replace_string + " ) "
                            not_null_value = not_null_value + 1
                
                # 마지막으로 col_string 정리하기
                if(col_string != ""):
                    if("비고" in col_string):
                        col_string = "비고"
                    elif("기호" in col_string):
                        col_string = "기호"
                    col_string = re.sub('[^A-Za-z0-9가-힣(]', '', col_string[0]) + col_string[1:]
                    col_string = col_string.strip() # 맨앞이나 뒤에 띄어쓰기 없애기
                else:
                    col_string = col_string.strip() # 맨앞이나 뒤에 띄어쓰기 없애기

                # text 처리: value값 만들기
                if(col_string != ''): # col_string값이 빈값이면 추가하지 않음
                    print("data:",)
                    if(len(data[page_string][j][table_string][k]) == len(data[page_string][j][table_string][1])):
                        # row 개수만큼 dictionary만들기 위해 하는 것 (1번만 돌려서 미리 dic만들기)
                        if(len(data[page_string][j][table_string][k]) > index_value):
                            for x in range(index_value, len(data[page_string][j][table_string][k])):
                                try:
                                    row_dictionary = {}
                                    # 값이 소수지만 소수점이 찍히지 않은 경우 수동으로 찍어줌
                                    try:
                                        if(data[page_string][j][table_string][k][x][0] == '0' and len(data[page_string][j][table_string][k][x]) > 1):
                                            data[page_string][j][table_string][k][x] = data[page_string][j][table_string][k][x][0] + '.' + data[page_string][j][table_string][k][x][1:]
                                            data[page_string][j][table_string][k][x] = data[page_string][j][table_string][k][x].replace("..",".")
                                            row_dictionary[col_string] = data[page_string][j][table_string][k][x]
                                        else:
                                            row_dictionary[col_string] = data[page_string][j][table_string][k][x]   
                                    except IndexError as e:
                                        print(e)
                                        row_dictionary[col_string] = data[page_string][j][table_string][k][x]
                                    table_dictionary[table_string].append(row_dictionary) # dictionary 추가
                                except:
                                    print("no input in first time making dictionary")
                                    row_dictionary = {}
                                    row_dictionary[col_string] = ""
                                    table_dictionary[table_string].append(row_dictionary) # dictionary 추가
                        else:
                            row_dictionary = {}
                            row_dictionary[col_string] = ""
                            table_dictionary[table_string].append(row_dictionary) # dictionary 추가
                    else:
                        if(len(data[page_string][j][table_string][1]) > index_value):
                            for x in range(index_value, len(data[page_string][j][table_string][k])):
                                    row_dictionary = {}
                                    try:
                                        if(data[page_string][j][table_string][k][x][0] == '0' and len(data[page_string][j][table_string][k][x]) > 1):
                                            data[page_string][j][table_string][k][x] = data[page_string][j][table_string][k][x][0] + '.' + data[page_string][j][table_string][k][x][1:]
                                            data[page_string][j][table_string][k][x] = data[page_string][j][table_string][k][x].replace("..",".")
                                            row_dictionary[col_string] = data[page_string][j][table_string][k][x]
                                        else:
                                            row_dictionary[col_string] = data[page_string][j][table_string][k][x]        
                                    except IndexError as e:
                                        print(e)
                                        row_dictionary[col_string] = data[page_string][j][table_string][k][x]                
                                    table_dictionary[table_string].append(row_dictionary) # dictionary 추가
                                    x = x + 1
                            for x in range(len(data[page_string][j][table_string][k]), len(data[page_string][j][table_string][1])):
                                row_dictionary = {}
                                row_dictionary[col_string] = ""
                                table_dictionary[table_string].append(row_dictionary) # dictionary 추가
                        else:
                            row_dictionary = {}
                            row_dictionary[col_string] = ""
                            table_dictionary[table_string].append(row_dictionary) # dictionary 추가


            # 미리 만들어진 dictionary에 key:value쌍이 추가되듯이 나머지 값이 들어감 (값 예시 -> "직경" : "20")
            for k in range(1, len(data[page_string][j][table_string])):
                row_dictionary = {}
                col_string = ""

                # col이 index 2이하에만 있는 경우도 있다
                # col값에 숫자가 있으면 거기서 자르기 (정확한 key값을 만들기 위해)
                hasNumber = lambda stringVal: any(elem.isdigit() for elem in stringVal)
                not_null_value = 0
                small_amount_check = [0,1,2]

                # get_index_value()로 따로 index_value가 구해지지 않은 경우 이전처럼 하나씩 직접 구해줌
                if(index_value == 0):
                    units = ['m2','hr','m3','mmAq','kg','kcal','Hz','Ph','V',
                            'min','대','Kg / h','kW X EA',
                            'kw','$','Lit',
                            '#','cm2','cm'
                    ]
                    check = 0
                    try:
                        word_location = data[page_string][j][table_string][k].index("명칭")
                        try:
                            blank_location = data[page_string][j][table_string][k].index("",word_location)
                            index_value = blank_location + 1
                        except ValueError as e:
                            index_value = word_location + 1
                        check = 1
                    except:
                        pass
                    try:
                        word_location_2 = data[page_string][j][table_string][k].index("설치 장소")
                        try:
                            blank_location_2 = data[page_string][j][table_string][k].index("",word_location_2)
                            index_value = blank_location_2 + 1
                        except ValueError as e:
                            index_value = word_location_2 + 1
                        check = 1
                    except:
                        pass

                    for unit in units:
                            try:
                                unit_index = data[page_string][j][table_string][k].index(unit) + 1
                            except:
                                unit_index = -1
                                pass

                    if(check == 0):
                        # key값을 구하기 위한 index_value구하기 (IndexError: list index out of range 방지)
                        if(len(data[page_string][j][table_string][k]) in small_amount_check):
                            index_value = len(data[page_string][j][table_string][k])
                        else:    
                            index_value = 3
                            if(len(data[page_string][j][table_string][k]) == 3):
                                for y in range(2):
                                    if(hasNumber(data[page_string][j][table_string][k][y+1])):
                                        index_value = y+1
                                        break
                            elif(len(data[page_string][j][table_string][k]) == 4):
                                for y in range(3):
                                    if(hasNumber(data[page_string][j][table_string][k][y+1])):
                                        index_value = y+1
                                        break
                            else:
                                for y in range(4):
                                    if(hasNumber(data[page_string][j][table_string][k][y+1])):
                                        index_value = y+1
                                        break

                    # 단위는 꼭 key값으로 포함시키기                
                    if(unit_index > index_value):
                        index_value = unit_index

                # col_string 구하기
                for x in range(index_value):
                    # key값에 말도안되는 문장이 들어가는 것을 방지하기 위함 (아래와 같은 조사나 특수문자가 들어가면 pass)
                        lang_for_delete = ['는','을','를','로','부터','*']
                        delete_the_lang = 0
                        if(data[page_string][j][table_string][k][x] == ""):
                            pass
                        elif("비고" in data[page_string][j][table_string][k][x] or "비 고" in data[page_string][j][table_string][k][x]):
                            col_string = "비고"
                            break
                        elif("기호" in data[page_string][j][table_string][k][x] or "기 호" in data[page_string][j][table_string][k][x]):
                            col_string = "기호"
                            break
                        else:
                            for lang in lang_for_delete:
                                if(lang in data[page_string][j][table_string][k][x]):
                                    delete_the_lang = 1
                                    break
                            if(delete_the_lang == 0):
                                # 값이 있는 경우가 처음이면 그냥 더해주고
                                if(not_null_value == 0):
                                    replace_string = data[page_string][j][table_string][k][x]
                                    if(replace_string.count("(") %2 == 1):
                                        replace_string = replace_string.replace("(","")
                                    if(replace_string.count(")") %2 == 1):
                                        replace_string = replace_string.replace(")","")
                                    col_string += replace_string + " "
                                # 값이 있는 경우가 처음이 아니면 괄호 없애주고 (있는 경우가 있음) 그 후에 제대로된 괄호를 더해준다
                                else:
                                    replace_string = data[page_string][j][table_string][k][x].replace("(","").replace(")","")
                                    col_string += " ( " + replace_string + " ) "
                                not_null_value = not_null_value + 1
                # 마지막으로 col_string 정리하기 (맨 앞에 특수문자 방지)
                if(col_string != ""):
                    if("비고" in col_string):
                        col_string = "비고"
                    elif("기호" in col_string):
                        col_string = "기호"
                    col_string = re.sub('[^A-Za-z0-9가-힣(]', '', col_string[0]) + col_string[1:]
                    col_string = col_string.strip() # 맨앞이나 뒤에 띄어쓰기 없애기
                else:
                    col_string = col_string.strip() # 맨앞이나 뒤에 띄어쓰기 없애기

                # text 처리: value값 만들기
                if(col_string != ''): # col_string값이 빈값이면 추가하지 않음
                    if(len(data[page_string][j][table_string][k]) > index_value):
                        for x in range(index_value, len(data[page_string][j][table_string][k])):
                            # data[page_string][j][table_sting][k][x]가 아예 없는 경우 (indexError) error가 나는 것을 방지하기 위한 try except
                            try:
                                # data[page_string][j][table_sting][k][x]는 있지만 값이 null인 경우 0번째나 len을 구하려고 할때 error가 나서 아예 null값이라도 들어가지 못하는 경우를 방지하기 위한 try except
                                try:
                                    # 값이 소수지만 소수점이 찍히지 못한 경우 수동으로 찍어준다
                                    if(data[page_string][j][table_string][k][x][0] == '0' and len(data[page_string][j][table_string][k][x]) > 1):
                                            data[page_string][j][table_string][k][x] = data[page_string][j][table_string][k][x][0] + '.' + data[page_string][j][table_string][k][x][1:]
                                            data[page_string][j][table_string][k][x] = data[page_string][j][table_string][k][x].replace("..",".")
                                            table_dictionary[table_string][x-index_value][col_string] = data[page_string][j][table_string][k][x] # 만들어둔 dictionary에 key:value쌍이 추가
                                    else:
                                        table_dictionary[table_string][x-index_value][col_string] = data[page_string][j][table_string][k][x] # 만들어둔 dictionary에 key:value쌍이 추가
                                except:
                                    table_dictionary[table_string][x-index_value][col_string] = data[page_string][j][table_string][k][x] # 만들어둔 dictionary에 key:value쌍이 추가
                            except:
                                print("no value is detected\n")
                    else:
                        try:
                            table_dictionary[table_string][x-index_value][col_string] = ""
                        except:
                            print("no value is detected\n")

            
            # table마다의 dictionary가 다 만들어지면 page_dictionary에 추가해준다
            page_dictionary[page_string].append(table_dictionary)

        # page 마다의 dictionary가 다 만들어지면 최종적으로 result_dictionary에 update해준다
        result_dictionary.update(page_dictionary)
    
    # 결론적으로 row를 기준으로 정리되고 col값은 각 row의 data의 key값으로 들어간다.
    return result_dictionary

# 원본 table의 비어 있는 row 지워주기
def data_processing_2(file_path):
    #1차 가공된 data가져오기
    data = data_processing(file_path)

    # 파일 내 page 개수
    total_page_num = len(data)
   
    for x in range(total_page_num):
        page = "page: " + str(x)
        # page 당 table 개수
        table_num = len(data[page]) 
        for y in range(table_num):
            table = "table: " + str(y)
            # table 당 row 개수
            length = len(data[page][y][table])
            j = 0
            # row 전체가 비어있다면 해당 dictionary 자체 삭제
            for i in range(length):
                not_null_count = 0
                for value in data[page][y][table][j].values():
                    if(value != ''):
                        not_null_count = not_null_count + 1
                        j = j + 1
                        break
                if(not_null_count == 0):
                    del data[page][y][table][j]

    # 가공 완료된 데이터 return (최종 결과물)          
    return data 

def requests_call(input_file_name):

    url = f"https://app.nanonets.com/api/v2/OCR/Model/{env('MODEL_ID')}/LabelFile/"

    ############## 수정 ##########################
    file_path = STATIC_ROOT+'media\\PDF\\'+ input_file_name  # request 받은 파일 저장하는 폴더명 수정
    ##############################################

    file_name = input_file_name.split(".")[0]
    
    ############## 수정 ##########################
    result_file_path = STATIC_ROOT+'media\\JSON\\' + file_name +".json" # nanonets 결과물 저장되어 있는 폴더 경로 수정
    ##############################################
    print(result_file_path)

    # 아직 해당 pdf에 대해서 nanonets를 돌린 적이 없을 때 nanonets 돌리기
    if(os.path.isfile(result_file_path) == False):  
        print("Running nanonets...")
        data = {'file': open(file_path, 'rb')}
        response = requests.post(url, auth=requests.auth.HTTPBasicAuth(f"{env('API_KEY')}", ''), files=data)
        result = json.loads(response.text)
        json_object = json.dumps(result,indent=4,ensure_ascii=False)
        with open(result_file_path,'w',encoding='utf-8') as outfile:
            outfile.write(json_object)  

    # for one file
    print("Processing extracted data...")
    architect_info = data_processing_2(result_file_path)
    request_call = {}
    request_call.update(architect_info)
    request_call = {**request_call}

    # script_dir = os.path.dirname(__file__)

    ############## 수정 ##########################
    save_file_path = STATIC_ROOT+'media\\Result\\' + file_name +".json" # 가공된 결과물 저장하기 위한 파일 경로 수정
    ##############################################

    with open(save_file_path, 'w',encoding='utf-8') as json_file:
            json.dump(request_call, json_file,sort_keys=True, indent=4, ensure_ascii=False)

    return request_call