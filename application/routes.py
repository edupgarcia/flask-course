from application import app, db, api
from flask import flash, redirect, render_template, request, json, Response, url_for, session
from application.forms import LoginForm, RegisterForm
from application.models import User, Course, Enrollment
from flask_restplus import Resource

# courseData = [
#     {"course_id": "1111", "title": "PHP 111", "description": "Intro to PHP",
#         "credits": "3", "term": "Fall, Spring"},
#     {"course_id": "2222", "title": "Java 1",
#         "description": "Intro to Java Programming", "credits": "4", "term": "Spring"},
#     {"course_id": "3333", "title": "Adv PHP 201",
#         "description": "Advanced PHP Programming", "credits": "3", "term": "Fall"},
#     {"course_id": "4444", "title": "Angular 1",
#         "description": "Intro to Angular", "credits": "3", "term": "Fall, Spring"},
#     {"course_id": "5555", "title": "Java 2",
#         "description": "Advanced Java Programming", "credits": "4", "term": "Fall"}
# ]


# API Area begin

@api.route("/api/user/", "/api/user/<idx>")
class UserAPI(Resource):
    def get(self, idx=None):
        if idx:
            return User.objects(user_id=idx).first().to_json()
        else:
            return User.objects().to_json()

    def post(self):
        data = api.payload
        user_id = User.objects.count() + 1

        user = User(
            user_id=user_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password']
        )
        user.set_password(data['password'])
        user.save()
        return User.objects(user_id=user.user_id).first().to_json()

    def put(self, idx):
        data = api.payload
        user = User.objects(user_id=idx).update(**data)
        return User.objects(user_id=idx).first().to_json() 
    
    def delete(self, idx):
        user = User.objects(user_id=idx).first()
        user.delete()
        return ({"message": f"User {idx} was deleted"}, 200)

# API Area end

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('username'):
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.objects(email=email).first()
        if user and user.check_password(password):
            # if request.form.get('email') == "test@uta.com":
            flash(f"{user.first_name} you are succeedfully logged in!", "success")
            session['user_id'] = user.user_id
            session['username'] = user.first_name
            return redirect(url_for('index'))
        else:
            flash("Sorry, something went wrong.", "danger")
    return render_template("login.html", title="Login", form=form, login=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term=None):
    if term == None:
        term = "Spring 2019"
    classes = Course.objects.order_by("+course_id")
    return render_template("courses.html", courseData=classes, courses=True, term=term)


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get('username'):
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            user_id=User.objects.count() + 1,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        user.save()
        flash(f"{user.first_name} you are succeedfully registered!", "success")
        return redirect(url_for('index'))

    return render_template("register.html", title="Register", form=form, register=True)


@app.route("/enrollment", methods=["GET", "POST"])
def enrollment():
    if not session.get('username'):
        return redirect(url_for('login'))

    course_id = request.form.get('course_id')
    course_title = request.form.get('title')
    user_id = session.get('user_id')

    if course_id:
        if Enrollment.objects(user_id=user_id, course_id=course_id).first():
            flash(f"You are already enrolled in {course_title}", "warning")
        else:
            Enrollment(
                user_id=user_id,
                course_id=course_id
            ).save()
            flash(f"You are now enrolled in {course_title}", "success")

    classes = list(
        User.objects.aggregate(
            *[
                {
                    '$lookup': {
                        'from': 'enrollment',
                        'localField': 'user_id',
                        'foreignField': 'user_id',
                        'as': 'r1'
                    }
                }, {
                    '$unwind': {
                        'path': '$r1',
                        'includeArrayIndex': 'r1_id',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$lookup': {
                        'from': 'course',
                        'localField': 'r1.course_id',
                        'foreignField': 'course_id',
                        'as': 'r2'
                    }
                }, {
                    '$unwind': {
                        'path': '$r2',
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$match': {
                        'user_id': user_id
                    }
                }, {
                    '$sort': {
                        'course_id': 1
                    }
                }
            ]
        )
    )

    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes)


# @app.route("/api/")
# @app.route("/api/<idx>")
# def api(idx=None):
#     if (idx == None):
#         jdata = courseData
#     else:
#         jdata = courseData[int(idx)]

#     return Response(json.dumps(jdata), mimetype="application/json")


@app.route("/user")
def user():

    # User(
    #     user_id=1,
    #     first_name="Christian",
    #     last_name="Hur",
    #     email="christian@uta.com",
    #     password="abc1234"
    # ).save()

    # User(
    #     user_id=2,
    #     first_name="Mary",
    #     last_name="Jane",
    #     email="mary.jane@uta.com",
    #     password="password123"
    # ).save()

    users = User.objects.all()

    return render_template("user.html", users=users)
