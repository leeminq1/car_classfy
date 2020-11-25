from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://test:test@localhost',27017)
db = client.dbsparta


# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('login.html')


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        register_info = request.form
        username = register_info['username']
        # hashed_password=bcrypt.hashpw(register_info['password'].encode('utf-8'),bcrypt.gensalt())
        password = register_info['password']
        doc = {
            "name": username,
            "password": password,
        }
        db.login.insert_one(doc)
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        register_info = request.form
        username = register_info['username']
        password = register_info['password']
        login_list= list(db.login.find({}, {'_id': False}))


        for i in range(len(login_list)):
            if username==login_list[i]['name']:
                if password==login_list[i]['password']:
                    return render_template('index.html')



#
# API 역할을 하는 부분
@app.route('/api/download', methods=['GET'])
def data_download():
    # 1. db에서 mystar 목록 전체를 검색합니다. ID는 제외하고 like 가 많은 순으로 정렬합니다.
    # 참고) find({},{'_id':False}), sort()를 활용하면 굿!
    # 2. 성공하면 success 메시지와 함께 stars_list 목록을 클라이언트에 전달합니다.
    car_list = list(db.cardb.find({}, {'_id': False}))
    return jsonify({'result': 'success', 'msg': car_list})


@app.route('/api/upload', methods=['POST'])
def data_upload():
    name_receive = request.form['name_receive']
    number_receive = request.form['number_receive']
    location_receive = request.form['location_receive']
    car_class_receive = request.form['car_class_receive']
    car_commnet_receive = request.form['car_commnet_receive']
    # 이거 하고 mogo db 저장해야함.
    doc = {
        "name": name_receive,
        "number": number_receive,
        "location": location_receive,
        "class": car_class_receive,
        "comment": car_commnet_receive,
    }
    db.cardb.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '차량 등록완료'})

@app.route('/api/updata', methods=['POST'])
def data_update():
    print(1)
    number_receive=request.form['number_give']
    new_location=request.form['new_location_give']
    current_location = db.cardb.find_one({'number': number_receive})['location']
    db.cardb.update_one({'number': number_receive}, {'$set': {'location': new_location}})

    return jsonify({'result': 'success', 'msg':current_location+"에서"+new_location+"으로 장소이동" })

# @app.route('/api/delete', methods=['POST'])
# def delete_star():
#     # 1. 클라이언트가 전달한 name_give를 name_receive 변수에 넣습니다.
#     # 2. mystar 목록에서 delete_one으로 name이 name_receive와 일치하는 star를 제거합니다.
#     # 3. 성공하면 success 메시지를 반환합니다.
#     name_receive = request.form['name_give']
#     db.mystar.delete_one({'name': name_receive})
#     return jsonify({'result': 'success', 'msg': '삭제가 완료되었습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
