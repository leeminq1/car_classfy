from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://test:test@localhost',27017)
db = client.dbsparta


# HTML 화면 보여주기
# main home login
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# login 시에 index로 이동
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 회원가입
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # DB에 저장
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 2)  # 로그인 2시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 아래 bottom 으로 이동하기 위한 render templates
# index에서 각각의 항목으로 이동
# Jinja로 보낸거 받을 때는 <> 안에 다가 Jinja에서 보낸값 써주면 서버에서 변수로 사용가능한듯
@app.route('/list/<username>')
def getlist(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        sort_list = list(db.cardb.find({'last_user': username}, {'_id': False}))
        total_usecar = len(sort_list)
        return render_template('list.html', user_info=user_info, total_usecar=total_usecar, sort_list=sort_list)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 아래 bottom 으로 이동하기 위한 render templates
@app.route('/register')
def register_car():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        print("register_car실행")
        return render_template('register.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 아래 bottom 으로 이동하기 위한 render templates
@app.route('/location')
def location_car():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 여기는 index.html에서 받아올 때
@app.route('/api/download', methods=['GET'])
def data_download():
    car_list = list(db.cardb.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'msg': car_list})


# 여기는 list.html에서 사용자에 맞는 사용차량을 받아올때
@app.route('/api/downloadlist', methods=['GET'])
def data_download_list():
    username_receive = request.args.get("username_give")
    print(username_receive)
    car_list = list(db.cardb.find({'last_user': username_receive}, {'_id': False}))
    if car_list:
        return jsonify({'result': 'success', 'msg': car_list})
    else:
        return jsonify({'result': 'fail', 'msg': "조회할 차량이 없습니다."})

# 여기는 register.html에서 modal에서 차량정보를 불러올 때 사용한다.
@app.route('/api/modallist', methods=['GET'])
def modal_list():
    number_receive = request.args.get("number_give")
    print(number_receive)
    car_list = list(db.cardb.find({'number': number_receive}, {'_id': False}))
    if car_list:
        return jsonify({'result': 'success', 'msg': car_list})
    else:
        return jsonify({'result': 'fail', 'msg': "조회할 차량이 없습니다."})



@app.route('/api/findlocationlist', methods=['POST'])
def find_car_location_list():
    # list에서 가져오는 차량찾기 기능
    serarch_option_receive = request.form['serarch_option_receive']
    if serarch_option_receive == '1':
        print("차종으로검색")
        name_receive = request.form['name_receive']
        name_receive = name_receive.upper()
        sort_list = list(db.cardb.find({'name': name_receive}, {'_id': False}))
        if sort_list:
            return jsonify({'result': 'success', 'msg': sort_list})
        else:
            return jsonify({'result': 'fail', 'msg': "잘못 또는 미등록 차종명입니다."})


    elif serarch_option_receive == '2':
        print("관리번호로 검색")
        number_receive = request.form['number_receive']
        # 숫자만 받아와서 N 랑 /를 붙여준다. EX) 12 12 231 이거를 N12/12-231로 만들어준다.
        number_full = f'N{number_receive[0:2]}/{number_receive[2:4]}-{number_receive[4:]}'
        sort_list = list(db.cardb.find({'number': number_full}, {'_id': False}))
        if sort_list:
            return jsonify({'result': 'success', 'msg': sort_list})
        else:
            return jsonify({'result': 'fail', 'msg': "잘못 또는 미등록 관리번호입니다."})

    elif serarch_option_receive == '3':
        real_number_receive = request.form['real_number_receive']
        # 숫자만 받아와서 N 랑 /를 붙여준다. EX) 12 12 231 이거를 N12/12-231로 만들어준다.
        sort_list = list(db.cardb.find({'car_temp_number': str(real_number_receive)}, {'_id': False}))
        if sort_list:
            print("임판으로 검색하고 결과를 찾음")
            return jsonify({'result': 'success', 'msg': sort_list})
        else:
            print("임판으로 검색하고 결과를 못찾음")
            return jsonify({'result': 'fail', 'msg': "잘못 또는 미등록 임시번호입니다."})

    elif serarch_option_receive == '4':
        print("임시번호차량만 조회")
        sort_list = list(db.cardb.find({'car_temp_select': "Y"}, {'_id': False}))
        if sort_list:
            return jsonify({'result': 'success', 'msg': sort_list})
        else:
            return jsonify({'result': 'fail', 'msg': "임시번호 차량이 없습니다."})


@app.route('/api/carfind', methods=['POST'])
def car_find():
    number_receive = request.form['number_receive']
    print(number_receive)
    number_full = f'N{number_receive[0:2]}/{number_receive[2:4]}-{number_receive[4:]}'
    print(number_full)
    try:
        current_location = db.cardb.find_one({'number': number_full})['location']
    except:
        current_location = None

    if current_location is not None:
        current_location = current_location;
        return jsonify({'result': 'success', 'msg': current_location})
    else:
        return jsonify({'result': 'success', 'msg': "잘못 또는 미등록 관리번호입니다."})


@app.route('/api/list', methods=['GET'])
def list_download():
    # 1. db에서 mystar 목록 전체를 검색합니다. ID는 제외하고 like 가 많은 순으로 정렬합니다.
    # 참고) find({},{'_id':False}), sort()를 활용하면 굿!
    # 2. 성공하면 success 메시지와 함께 stars_list 목록을 클라이언트에 전달합니다.
    car_list = list(db.cardb.find({}, {'_id': False}).sort("name", 1))
    return jsonify({'result': 'success', 'msg': car_list})


@app.route('/api/upload', methods=['POST'])
def data_upload():
    name_receive = request.form['name_receive']
    number_receive = request.form['number_receive']
    location_receive = request.form['location_receive']
    car_class_receive = request.form['car_class_receive']
    car_commnet_receive = request.form['car_commnet_receive']
    car_admin_receive = request.form['car_admin_receive']
    car_region_receive = request.form['car_region_receive']
    car_temp_select_receive = request.form['car_temp_select_receive']
    car_temp_number_receive = request.form['car_temp_number_receive']
    temp_number_start_receive = request.form['temp_number_start_receive']
    temp_number_end_receive = request.form['temp_number_end_receive']

    region_list = ["로비근처", "신규주차장", "제동시험동", "소뱅크", "엔진조립동", "PG", "기타연구소내", "연구소외"]
    location_area = ''
    if location_receive == "1":
        location_area = region_list[0]
    elif location_receive == "2":
        location_area = region_list[1]
    elif location_receive == "3":
        location_area = region_list[2]
    elif location_receive == "4":
        location_area = region_list[3]
    elif location_receive == "5":
        location_area = region_list[4]
    elif location_receive == "6":
        location_area = region_list[5]
    elif location_receive == "7":
        location_area = region_list[6]
    elif location_receive == "8":
        location_area = region_list[7]

    # 이거 하고 mogo db 저장해야함.
    doc = {
        "name": name_receive,
        "number": number_receive,
        "location": location_area,
        "class": car_class_receive,
        "comment": car_commnet_receive,
        "location_number": location_receive,
        "car_admin": car_admin_receive,
        "car_region": car_region_receive,
        "car_temp_select": car_temp_select_receive,
        "car_temp_number": car_temp_number_receive,
        "temp_number_start": temp_number_start_receive,
        "temp_number_end": temp_number_end_receive
    }
    db.cardb.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '차량 등록완료'})


@app.route('/api/updata', methods=['POST'])
def data_update():
    number_receive = request.form['number_give']
    new_location = request.form['new_location_give']
    user_name = request.form['user_id_give']

    time = datetime.now()
    time = time.strftime('%Y년 %m월 %d일 %H시 %M분')
    current_location = db.cardb.find_one({'number': number_receive})['location']
    print(new_location, user_name, time)
    region_list = ["로비근처", "신규주차장", "제동시험동", "소뱅크", "엔진조립동", "PG", "기타연구소내", "연구소외"]
    location_area = ''
    if new_location == "1":
        location_area = region_list[0]
    elif new_location == "2":
        location_area = region_list[1]
    elif new_location == "3":
        location_area = region_list[2]
    elif new_location == "4":
        location_area = region_list[3]
    elif new_location == "5":
        location_area = region_list[4]
    elif new_location == "6":
        location_area = region_list[5]
    elif new_location == "7":
        location_area = region_list[6]
    elif new_location == "8":
        location_area = region_list[7]

    db.cardb.update_one({'number': number_receive}, {
        '$set': {'location': location_area, 'location_number': new_location, 'last_user': user_name,
                 'last_time': time}, })

    return jsonify({'result': 'success', 'msg': "이동완료"})

# modal update
@app.route('/api/modalupdate', methods=['POST'])
def modal_update():
    name_receive = request.form['name_receive'].upper()
    number_receive = request.form['number_receive'].upper()
    car_admin_receive = request.form['car_admin_receive']
    car_region_receive = request.form['car_region_receive']
    car_temp_select_receive = request.form['car_temp_select_receive'].upper()
    car_temp_number_receive = request.form['car_temp_number_receive']
    temp_number_start_receive = request.form['temp_number_start_receive']
    temp_number_end_receive = request.form['temp_number_end_receive']
    comment_receive = request.form['comment_receive']

    db.cardb.update_one({'number': number_receive},
                {'$set': {'name': name_receive, 'number': number_receive, 'car_admin': car_admin_receive,
                 'car_region': car_region_receive,'car_temp_select': car_temp_select_receive,
                          'car_temp_number': car_temp_number_receive,'temp_number_start': temp_number_start_receive,
                          'temp_number_end': temp_number_end_receive,'comment': comment_receive}})

    return jsonify({'result': 'success', 'msg': "수정완료"})



@app.route('/api/modaldelete', methods=['POST'])
def modal_delete():
    # 1. 클라이언트가 전달한 name_give를 name_receive 변수에 넣습니다.
    # 2. mystar 목록에서 delete_one으로 name이 name_receive와 일치하는 star를 제거합니다.
    # 3. 성공하면 success 메시지를 반환합니다.
    number_receive = request.form['number_receive']
    db.cardb.delete_one({'number': number_receive})
    return jsonify({'result': 'success', 'msg': '삭제가 완료되었습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
