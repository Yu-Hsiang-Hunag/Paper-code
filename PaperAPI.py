import datetime, time, keyboard, json, pymysql, os, re, math, configparser, subprocess, requests
from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory, render_template, jsonify
#from flask_api import status
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)
app_router = ''
#Connect to DB
db = pymysql.connect(host = "localhost", user = "root", passwd = "garbagedogisme", db = "Test")
cursor = db.cursor()

#Drop Table
# sql = ("DROP TABLE IF EXISTS Naming_Convention_List, FE_Name, Element_Info")
# cursor.execute(sql)
# db.commit()
# db.close()

#Create Table
#Connect to DB
db = pymysql.connect(host = "localhost", user = "root", passwd = "garbagedogisme", db = "Test")
cursor = db.cursor()
sql = """CREATE TABLE IF NOT EXISTS `Naming_Convention_List`(
    naming_convention_list VARCHAR(1000),
    list_ID INT(10)
)"""
cursor.execute(sql)
db.commit()

sql = """CREATE TABLE IF NOT EXISTS `FE_Name`(
    FE_name VARCHAR(1000),
    ProjectName VARCHAR(1000),
    list_ID INT(10),
    Element_parameters text,
    Element_location text,
    Label_name text,
    Label text,
    Category VARCHAR(1000),
    Type VARCHAR(1000),
    Element_Function VARCHAR(1000),
    Location VARCHAR(1000),
    Description VARCHAR(100),
    Manufacture VARCHAR(1000),
    Process_number VARCHAR(100),
    Status INT(10),
    CreateTime VARCHAR(1000)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
cursor.execute(sql)
db.commit()

sql = """CREATE TABLE IF NOT EXISTS `Element_Info`(
    ID INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    Project_id VARCHAR(100),
    Nick_Name VARCHAR(1000),
    Element_location_parameter VARCHAR(10000),
    Element_Category VARCHAR(1000),
    Element_Function VARCHAR(1000),
    Element_Type VARCHAR(1000),
    Element_Location VARCHAR(1000),
    Element_Description text,
    Element_Manufacture VARCHAR(1000),
    Element_Property VARCHAR(1000),
    Element_Process_Number VARCHAR(1000),
    Cost text,
    Time text,
    Owner VARCHAR(1000)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci"""
cursor.execute(sql)
db.commit()
db.close()

# For obtaing time
tz_utc = datetime.timezone(datetime.timedelta(hours = int(time.timezone / -3600)))  # system timezone
tz_utc_0 = datetime.timezone(datetime.timedelta(hours = 0))  # system timezone
tz_utc_8 = datetime.timezone(datetime.timedelta(hours = 8))  # system timezone

#Setup API
@app.route('/setup', methods=['POST'])
@cross_origin()
def name_setup():
    db = db = pymysql.connect(host='127.0.0.1', user='root',password='garbagedogisme',database='Test')
    cursor = db.cursor()
    request_data = request.get_json()
    # JSON keys and values
    keys = list(request_data.keys())
    values = list(request_data.values())
    # target of JSON data, delete the empty data
    target_keys = []
    target_values = list(filter(None, values)) # fileter the empty data, filter means python list that delete the empty data
    
    # iniitialize the loop parameters
    i = 0
    j = 0
    # The loop for checking the parameters, tatget_keys means the naming conveniton stored in database
    while j < len(target_values):
        if values[i] != '':
            if int(values[i].strip('')) == j + 1: # translate string into integer
                target_keys.append(keys[i])
                j = j + 1
            i = i + 1
        else:
            i = i + 1
        if i == len(values):
            i = 0
    print("target_keys", target_keys)
    LID = 1 # The first list ID which is sequential number from 1
    # sql command for querying the naming convention list table exsit or not
    sql = ("SELECT * FROM Naming_Convention_List")
    cursor.execute(sql)
    check_first = cursor.fetchall()
    # if function to check the response is empty or not
    if check_first == ():
        print("Check Naming Convention List exsit or not")
        sql = ("INSERT INTO Naming_Convention_List(naming_convention_List, list_ID) VALUES(%s, %s)")
        val = (str(target_keys), LID)
        cursor.execute(sql, val)
        db.commit()
        db.close()
        return jsonify({"list ID": LID}), 200 # retrun data format is JSON
    
    # if function for checking the latest list_ID
    sql_list_ID = ("SELECT list_ID FROM Naming_Convention_List order by list_ID desc limit 1")
    cursor.execute(sql_list_ID)
    latest_list_ID = int(str(cursor.fetchall()).strip("'(),"))
    # While loop function status
    State = True
    while (State):
        if(FindNamingConvention(target_keys, LID) == True): # Compare the properties between database and input. (FindNamingConvention function)
            return jsonify({"Naming covention exsit": True, "list ID": LID}), 200 # retrun data format is JSON
        else:
            LID = LID + 1
        if LID > latest_list_ID:
            sql = ("INSERT INTO Naming_Convention_List(naming_convention_list, list_ID) VALUES(%s, %s)")
            val = (str(target_keys), LID)
            cursor.execute(sql, val)
            db.commit()
            db.close()
            return jsonify({"Naming covention exsit2": False, "list ID": LID}), 200 # retrun data format is JSON
    
    
#Registration API
@app.route('/registration', methods=['POST'])
def registration():
    # 連線資料庫
    db = db = pymysql.connect(host='127.0.0.1', user='root',password='ifc725ntt',database='Test')
    cursor = db.cursor()
    # API接收的JSON資料
    request_data = request.get_json()
    Project_id = request_data['ProjectName']
    Element_location = ','.join(str(v) for v in request_data['Element_location'])
    # Project_user_id = request_data['Project_user_id']
    Element_parameters = json.dumps(request_data['Element_parameters'])
    Label_name = ','.join(str(v) for v in request_data['Label_name'])
    Label = ','.join(str(v) for v in request_data['Label'])
    Category = request_data['Category']
    Function = request_data['Function']
    Location = request_data['Location']
    Type = request_data['Type']
    Process_Number = request_data['Process_Number']
    Description = request_data['Description']
    Manufacture = request_data['Manufacture']
    list_ID = request_data['list_ID']
    # data which user post to API 
    keys = list(request_data.keys())
    values = list(request_data.values())
    d = datetime.datetime.now().astimezone(tz_utc_8).strftime
    Create_time = d('%Y') + '/' + d('%m') + '/' + d('%d')+'/' + d('%H') + ':' + d('%M') + ':' + d('%S') + '.' + d('%f')

    # searching naming convention
    sql = ("SELECT naming_convention_list FROM Naming_Convention_List WHERE list_ID = '%s'"%(list_ID))
    cursor.execute(sql)
    sql_data = cursor.fetchall()
    sql_data = str(sql_data).strip('()",')
    sql_data = eval(sql_data)

    FE_Name = ''
    # the first loop is naming convention in database
    for i in range(len(sql_data)):
        # the second loop is check the value of key that project participants key-in. so, compare the keys with naming convention
        for j in range(len(keys)):
            # check the property is the naming convention, the value of key should not be empty.
            if sql_data[i] == keys[j] and values[j] == '':
                return "The property" + values[j] + "should not be empty"
            # project participants input "key" is in the naming convention.
            elif sql_data[i] == keys[j]:
                # if the value of key is not empty, FE_Name = the value of key add "." | list first is 0, but actual list size is the last position of i + 1
                if i + 1 == len(sql_data):
                    FE_Name = FE_Name + values[j]
                    print("last key FE_name", FE_Name)
                    # check the sequential number of FE name
                    sql = ("SELECT FE_name FROM FE_Name WHERE FE_name like '%s'"%("%"+FE_Name+"%"))
                    cursor.execute(sql)

                    sequential_number_FE_Name = cursor.fetchall()
                    if sequential_number_FE_Name == ():
                        FE_Name = FE_Name + ".1"
                        print("Function", Function)
                        sql = ("INSERT INTO FE_Name(FE_name, ProjectName, list_ID, Element_parameters, Element_location, Label_name, Label, Category, \
                        Type, Element_Function, Location, Manufacture, Status, CreateTime, Process_number, Description) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                        val = (FE_Name, Project_id, list_ID, Element_parameters, Element_location, Label_name, Label, Category, Type, Function, Location, Manufacture, 1, Create_time, Process_Number, Description)
                        cursor.execute(sql, val)
                        db.commit()
                        db.close()
                    else:
                        se_n = str(sequential_number_FE_Name[-1])
                        chr = "(),'"
                        se_n = ''.join(x for x in se_n if x not in chr)
                        se_n = se_n.split(".")[-1]
                        FE_Name = FE_Name + "." + str(int(se_n)+1)
                        sql = ("INSERT INTO FE_Name(FE_name, ProjectName, list_ID, Element_parameters, Element_location, Label_name, Label, Category, \
                        Type, Element_Function, Location, Manufacture, Status, CreateTime, Process_number, Description) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                        val = (FE_Name, Project_id, list_ID, Element_parameters, Element_location, Label_name, Label, Category, Type, Function, Location, Manufacture, 1, Create_time, Process_Number, Description)
                        cursor.execute(sql, val)
                        db.commit()
                        db.close()
                else :
                    FE_Name = FE_Name + values[j] + '.'
            elif j == int(len(keys)) and sql_data[i] != keys[j]:
                return "It is needed the" + sql_data[i] + "to name the elements"
            
            if keys[j] == 'Location':
                print(values[j]=='')
    print("Functional element name", FE_Name)

    # add sequential number
    
    return jsonify({"FE name": FE_Name})

# query API
@app.route('/query', methods=['POST'])
def query():
    db = db = pymysql.connect(host='127.0.0.1', user='root',password='ifc725ntt',database='Test')
    cursor = db.cursor()
    request_data = request.get_json()
    # JSON keys and values
    keys = list(request_data.keys())
    values = list(request_data.values())
    # target of JSON data, delete the empty data
    target_keys = []
    target_values = list(filter(None, values)) # fileter the empty data, filter means python list that delete the empty data
    
    # iniitialize the loop parameters
    i = 0
    j = 0
    while j < len(target_values):
        if values[i] != '':
            if int(values[i].strip('')) == j + 1: # translate string into integer
                target_keys.append(keys[i])
                j = j + 1
            i = i + 1
        else:
            i = i + 1
        if i == len(values):
            i = 0
    LID = 1 # The first list ID which is sequential number from 1
    # sql command for querying the naming convention list table exsit or not
    sql = ("SELECT * FROM Naming_Convention_List")
    cursor.execute(sql)
    check_first = cursor.fetchall()
    # if function to check the response is empty or not
    if check_first == ():
        return jsonify({"Naming covention exsit": "Naming Convention List table is empty"}) # retrun data format is JSON
    
    # if function for checking the latest list_ID
    sql_list_ID = ("SELECT list_ID FROM Naming_Convention_List order by list_ID desc limit 1")
    cursor.execute(sql_list_ID)
    latest_list_ID = int(str(cursor.fetchall()).strip("'(),"))
    # While loop function status
    State = True
    while (State):
        if(FindNamingConvention(target_keys, LID) == True): # Compare the properties between database and input. (FindNamingConvention function)
            return jsonify({"Naming covention exsit": True, "list ID": LID}) # retrun data format is JSON
        else:
            LID = LID + 1
        if LID > latest_list_ID:
            return jsonify({"Naming covention exsit": False}) # retrun data format is JSON

# update API
@app.route('/update', methods=['POST'])
def update():
    # 連線資料庫
    db = db = pymysql.connect(host='127.0.0.1', user='root',password='ifc725ntt',database='Test')
    cursor = db.cursor()
    # API接收的JSON資料
    request_data = request.get_json()
    Project_id = request_data['ProjectName']
    FE_Name = request_data['FE_name']
    Element_location = ','.join(str(v) for v in request_data['Element_location'])
    # Project_user_id = request_data['Project_user_id']
    Element_parameters = json.dumps(request_data['Element_parameters'])
    Label_name = ','.join(str(v) for v in request_data['Label_name'])
    Label = ','.join(str(v) for v in request_data['Label'])
    Category = request_data['Category']
    Function = request_data['Function']
    Location = request_data['Location']
    Type = request_data['Type']
    Manufacture = request_data['Manufacture']
    Process_Number = request_data['Process_Number']
    Description = request_data['Description']
    keys = list(request_data.keys())
    values = list(request_data.values())
    # target of JSON data, delete the empty data
    target_keys = []
    target_values = []
    for i in range(len(keys)):
        if values[i] != '':
            target_keys.append(keys[i])
            target_values.append(values[i])
    # search sql
    sql = ("SELECT list_ID FROM FE_Name WHERE FE_name = '%s'"%(FE_Name))
    cursor.execute(sql)
    sql_list_ID = cursor.fetchall()
    print("sql list ID 1", sql_list_ID)
    sql_list_ID = str(sql_list_ID).strip(",()")
    print("sql list ID 2", sql_list_ID)

    sql = ("SELECT naming_convention_list FROM Naming_Convention_List WHERE list_ID = '%s'"%(int(sql_list_ID)))
    cursor.execute(sql)
    naming_convention_list = cursor.fetchall()
    naming_convention_list = eval(str(naming_convention_list).strip('",()'))
    print("Namign Convention List", naming_convention_list)
    print("Type of Naming_Convention_List", type(naming_convention_list))
    if len(target_keys) == 2:
        print("Empty")
        sql = ("UPDATE FE_Name SET Status = '%s' WHERE FE_name = '%s' and ProjectName = '%s'"%(0, FE_Name, Project_id))
        cursor.execute(sql)
        db.commit()
        return "Delete the element"
    else:
        print("Not empty")
        FE_Name_Length = FE_Name.split(".")
        print("FE_Name_Length", FE_Name_Length)
        if len(FE_Name_Length) == len(naming_convention_list) + 1:
            FE_Name_New = FE_Name + ".1"
            sql = ("UPDATE FE_Name SET FE_name = %s, Element_parameters = %s, Element_location = %s, Label_name = %s, Label = %s, Category = %s,\
            Type = %s, Element_Function = %s, Location = %s, Manufacture = %s, Process_number = %s, Description = %s WHERE ProjectName = %s and FE_name = %s")
            val = (FE_Name_New, Element_parameters, Element_location, Label_name, Label, Category, Type, Function, Location, Manufacture, Process_Number, Description, Project_id, FE_Name)
            cursor.execute(sql, val)
            db.commit()
            print("FE_Name_New", FE_Name_New)
            return jsonify({"FE name":FE_Name_New})
        else:
            FE_Name_list = FE_Name.split(".")
            FE_Name_New = ''
            for i in range(len(FE_Name_list)):
                if i == 0:
                    FE_Name_New = FE_Name_list[i]
                elif i != len(FE_Name_list) - 1:
                    FE_Name_New = FE_Name_New + "." + FE_Name_list[i]
                else:
                    FE_Name_New = FE_Name_New + "." + str(int(FE_Name_list[i]) + 1)
            sql = ("UPDATE FE_Name SET FE_name = %s, Element_parameters = %s, Element_location = %s, Label_name = %s, Label = %s, Category = %s,\
            Type = %s, Element_Function = %s, Location = %s, Manufacture = %s, Process_number = %s, Description = %s WHERE ProjectName = %s and FE_name = %s")
            val = (FE_Name_New, Element_parameters, Element_location, Label_name, Label, Category, Type, Function, Location, Manufacture, Process_Number, Description, Project_id, FE_Name)
            cursor.execute(sql, val)
            db.commit()
            print("FE_Name_New", FE_Name_New)
            return jsonify({"FE name":FE_Name_New})

@app.route('/synchronization', methods=['POST'])
def synchronization():
    db = db = pymysql.connect(host='127.0.0.1', user='root',password='ifc725ntt',database='Test')
    cursor = db.cursor()
    # API接收JSON資料
    request_data = request.get_json()
    Target_IP = request_data['Target_IP']
    Add_Parameter = request_data['Add_parameter']
    FE_Name = request_data['FE_name']
    Project_id = request_data['ProjectName']
    Element_location = ','.join(str(v) for v in request_data['Element_location'])
    Element_parameters = json.dumps(request_data['Element_parameters'])
    Label_name = ','.join(str(v) for v in request_data['Label_name'])
    Label = ','.join(str(v) for v in request_data['Label'])
    Category = request_data['Category']
    Function = request_data['Function']
    Location = request_data['Location']
    Type = request_data['Type']
    Process_Number = request_data['Process_Number']
    Description = request_data['Description']
    Manufacture = request_data['Manufacture']
    list_ID = request_data['list_ID']
    
    Res = requests.post("http://"+ Target_IP + ":9101/receive_synchronization",json = request_data)
    print(Res.text)
    Res = str(Res.text)
    print(Res)
    Syn_FE_Name = Add_Parameter + "." + FE_Name
    sql = ("UPDATE FE_Name SET FE_name = %s, Element_parameters = %s, Element_location = %s, Label_name = %s, Label = %s, Category = %s,\
            Type = %s, Element_Function = %s, Location = %s, Manufacture = %s, Process_number = %s, Description = %s WHERE ProjectName = %s and FE_name = %s")
    val = (Syn_FE_Name, Element_parameters, Element_location, Label_name, Label, Category, Type, Function, Location, Manufacture, Process_Number, Description, Project_id, FE_Name)
    cursor.execute(sql, val)
    db.commit()

    return jsonify({"FE name": Syn_FE_Name})

@app.route('/receive_synchronization', methods=['POST'])
@cross_origin()
def receive_synchronization():
    db = db = pymysql.connect(host='127.0.0.1', user='root',password='garbagedogisme',database='Test')
    cursor = db.cursor()
    request_data = request.get_json()
    Add_Parameter = request_data['Add_parameter']
    FE_Name = request_data['FE_name']
    Project_id = request_data['ProjectName']
    Element_location = ','.join(str(v) for v in request_data['Element_location'])
    Element_parameters = json.dumps(request_data['Element_parameters'])
    Label_name = ','.join(str(v) for v in request_data['Label_name'])
    Label = ','.join(str(v) for v in request_data['Label'])
    Category = request_data['Category']
    Function = request_data['Function']
    Location = request_data['Location']
    Type = request_data['Type']
    Process_Number = request_data['Process_Number']
    Description = request_data['Description']
    Manufacture = request_data['Manufacture']
    list_ID = request_data['list_ID']
    Syn_FE_Name = Add_Parameter + "." + FE_Name
    print("request_data", request_data)
    d = datetime.datetime.now().astimezone(tz_utc_8).strftime
    Create_time = d('%Y') + '/' + d('%m') + '/' + d('%d')+'/' + d('%H') + ':' + d('%M') + ':' + d('%S') + '.' + d('%f')

    sql = ("INSERT INTO FE_Name(FE_name, ProjectName, list_ID, Element_parameters, Element_location, Label_name, Label, Category, \
           Type, Element_Function, Location, Manufacture, Status, CreateTime, Process_number, Description) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    val = (Syn_FE_Name, Project_id, list_ID, Element_parameters, Element_location, Label_name, Label, Category, Type, Function, Location, Manufacture, 1, Create_time, Process_Number, Description)
    cursor.execute(sql, val)
    db.commit()
    return jsonify({"FE name":Syn_FE_Name})

def FindNamingConvention(target_keys, LID):
    db = db = pymysql.connect(host='127.0.0.1', user='root',password='ifc725ntt',database='Test')
    cursor = db.cursor()
    # print("FindNamingConvention function target_keys", target_keys)
    sql = ("SELECT naming_convention_list FROM Naming_Convention_List WHERE list_ID = '%s'"%(LID))
    cursor.execute(sql)
    sql_naming_convention_list = cursor.fetchall() # print => (("['Location', 'Type', 'Function', 'Category']",),)
    sql_naming_convention_list = str(sql_naming_convention_list).strip('"(),()') # delete the symbol
    sql_naming_convention_list = eval(sql_naming_convention_list) # string to list
    
    if len(target_keys) != len(sql_naming_convention_list): 
        return False
    for i in range(len(sql_naming_convention_list)):
        if sql_naming_convention_list[i] == target_keys[i]:
            continue
        else:
            return False
    return True


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 9101, debug=True)


