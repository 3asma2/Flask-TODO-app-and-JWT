from flask import Flask,request,jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token, get_jwt
)
from datetime import timedelta

DATABASE_URI = 'sqlite:///todoapp.db'
# DATABASE_URI = 'postgres://postgres:asmaa@localhost:5432/flaskapp'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)

app.config['JWT_SECRET_KEY'] = "asmaatest123456789"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'Task("{self.title}")'


class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'User("{self.username}")'

@app.route('/register', methods=['POST', 'GET'])
def registeration():
    if request.method == "GET":
        return jsonify({
            "status": "Please Register"
        })
    elif request.method == "POST":
        data = json.loads(request.data)
        username = data['username']
        password = data['password']
        user = User(
            username=username,
            password=password,
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({
            "data": f"{username} is added"
        })


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return jsonify({
            'status': 'Please Login',
        })
    elif request.method == 'POST':
        data = json.loads(request.data)
        username = data['username']
        password = data['password']
        user = User.query.filter_by(username=username).first()
        if user.password == password:
            access_token = create_access_token(identity=username)
            return jsonify({
                'status': 'success',
                'data': {
                    'access_token': access_token
                }})
        return jsonify({
            'msg': "username or password is incorrect"
        })


@app.route('/',methods=['GET'])
@jwt_required()
def getall():
    username = get_jwt_identity()
    todoapp = Task.query.all()
    result =[]
    for task in todoapp :
        dict= {}
        dict["id"] = task.id
        dict["title"] = task.title
        dict["created_at"] = task.created_at
        result.append(dict)
    return jsonify({
        'data':result
    })

@app.route('/add',methods=['GET','POST'])
@jwt_required()
def addnew():
    username = get_jwt_identity()
    data = json.loads(request.data)
    todotittle = data['title']
    addnew = Task(
        title = todotittle,
    )
    db.session.add(addnew)
    db.session.commit()
    return jsonify({
        'data':f'{todotittle} is done'
    })

@app.route('/todo/<int:id>',methods=['PUT', 'GET', 'DELETE'])
@jwt_required()
def mod_task(id):
    username = get_jwt_identity()
    todo = Task.query.filter_by(id=id).first()
    if request.method == 'GET':
        dict = {}
        dict['id'] = todo.id
        dict['title'] = todo.title

        return jsonify({
            "data": dict
        })
    if request.method == 'PUT':
        data = json.loads(request.data)
        todo.title = data['title']

        db.session.commit()
        return jsonify({
            'data':'updating is done'
        })
    if request.method == 'DELETE':
        db.session.delete(todo)
        db.session.commit()

        return jsonify({
            "data": "deleting is done"
        })


db.create_all()
app.run(host='127.0.0.1',port=5000,debug=True)