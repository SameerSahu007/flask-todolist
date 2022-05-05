
from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user,  logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.db'
app.config['SECRET_KEY'] = 'b7f2083968e25168f4088c9aa4d7fd1a38b47dff3354fdd95494cca8fe259d7a'
db = SQLAlchemy(app)
login_manager = LoginManager()

db.init_app(app);
@app.before_first_request
def create_table():
    db.create_all();

class User(db.Model, UserMixin):
    id  = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String, nullable=False, unique =True)
    password_hash = db.Column(db.String, nullable = False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

login_manager.init_app(app)
login_manager.login_view = 'register'
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Task(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable = False)
    tasklist = db.Column(db.String(100), unique = False, nullable=False)

    def __repr__(self):
        return f"Task: {self.tasklist}"

@app.route('/', methods=['POST', 'GET'])
@login_required
def home():
    if request.method =='POST':
        task = request.form['inputtask']
        user = Task(tasklist = task, userid = current_user.get_id())
        db.session.add(user)
        db.session.commit()
    
    tasklist = Task.query.filter_by(userid = current_user.get_id())
    
    user = User.query.filter_by(id = current_user.get_id()).first()

    return render_template('index.html',tasklist = tasklist, username = user.username)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    
    task  =  Task.query.filter_by(id = id ).first();
    db.session.delete(task)
    db.session.commit()


    return redirect('/')   

@app.route('/login', methods =['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username = username).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')
        else :
            return ('Wrong Credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # if User.query.filter_by(username = username):
        #     print(User.query.filter_by(username = username))
        #     return('Username is already taken')



        user = User(username = username)
        user.set_password(password)
        db.session.add(user);
        db.session.commit()
        return redirect('/login')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
