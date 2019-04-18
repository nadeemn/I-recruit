from flask import render_template, request, jsonify, Response, flash, url_for, redirect
from camera import VideoCamera
from word_training import models
from irecruit.forms import AdminloginForm, AdminForm, LoginForm, DetailsForm
from irecruit.models import Question, Admin, User, Skill
from irecruit import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required, user_logged_in
import random
import nltk
import wikipedia
from pyemd import emd
from nltk.corpus import stopwords
from nltk import download
#download('stopwords')
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
flag = 0


@app.route('/chat_retrieval')
def chat_retrieval():
    global correct_answer
    counts = request.args.get('count')
    items = Question.query.all()   # query need to be changed
    if counts == '0':
        while True:
            i = random.randint(0, len(items) - 1)
            if items[i].question_chosen == 0:
                break
        next_question = items[i]
        
        correct_answer = next_question.question_answer
        next_question.question_chosen = 0
        db.session.commit()
        results = [next_question.question, 1]
        return jsonify(result=results)
    else:
        answr = request.args.get('answer')
        print(correct_answer)
        print(answr)
        distance = similarity(answr, correct_answer)
        if distance < 3:
            while True:
                i = random.randint(0, len(items) - 1)
                if items[i].question_chosen == 0:
                    break
            next_question = items[i]
            correct_answer = next_question.question_answer
            next_question.question_chosen = 0
            db.session.commit()
            results = [next_question.question, 1]
            return jsonify(result=results)
        else:
            nouns = []
            for word, pos in nltk.pos_tag(nltk.word_tokenize(str(answr))):
                    if pos.startswith('NN'):
                        nouns.append(word)
            print(nouns)
            i = random.randint(0, len(nouns) - 1)
            words = nouns[i]
            next_question = "What do you mean by " + words
            answer = "what is " + words
            correct_answer = wikipedia.summary(answer, sentences=5)
            results = [next_question, 1]
            return jsonify(result=results)


def similarity(given_answer, db_answer):
    given_answer = given_answer.lower().split()
    db_answer = db_answer.lower().split()
    stop_words = stopwords.words('english')
    given_answer = [w for w in given_answer if w not in stop_words]
    db_answer = [w for w in db_answer if w not in stop_words]
    distance = models.wmdistance(given_answer, db_answer)
    print(distance)
    return distance


@app.route('/chat_interview')
def chat_interview():
    return render_template('chat.html', items=Question.query.all())


def gen(camera):
    global cnt
    while True:
        frame, cnt = camera.get_frame()
        print(cnt)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/", methods = ['POST', 'GET'])
@app.route("/home", methods = ['POST', 'GET'])
def home():
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You can enter your details now!', 'success')
            return redirect(url_for('details'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            return redirect(url_for('home'))
    return render_template('login1.html', title='Login', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/details", methods=['POST', 'GET'])
def details():

    if current_user.is_authenticated:
        form = DetailsForm()
        if form.validate_on_submit():
            print("hi")
            try:
                user = User(firstname=form.firstname.data, lastname=form.lastname.data, dob=form.dob.data, user_id = current_user.id)
                skills = Skill(skill1=form.skill1.data, level1=form.level1.data,
                                skill2=form.skill2.data, level2=form.level2.data,
                                skill3=form.skill3.data, level3=form.level3.data,
                                skill4=form.skill4.data, level4=form.level4.data, user_id = current_user.id)
                db.session.add(user)
                db.session.add(skills)
                db.session.commit()
                flash('Your details has been submitted! You are now able to take the test', 'success')
                return redirect(url_for('chat_interview'))
            except:
                db.session.rollback()
                flash('Your details already exist! You can\'t retake test', 'danger')
                return redirect(url_for('logout'))
    else:
        flash('You are not logged in! Please login', 'danger')
        return redirect(url_for('home'))
    return render_template('details.html', title='Details', form=form)


@app.route("/test", methods=['POST', 'GET'])
def test():
    print('')
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
    else:
        flash('You are not logged in! Please login', 'danger')
        return redirect(url_for('home'))
    return render_template('test.html', title='Test', user=user)


@app.route('/view_users')
def view_users():
    db.create_all()
    users = Admin.query.all()
    return render_template('view_users.html', users=users)


@app.route("/adminlogin", methods = ['POST', 'GET'])
def adminlogin():
    form = AdminloginForm()
    if form.validate_on_submit():
        if form.username.data == "aravindcv" and form.password.data == "password":
            global flag
            flag = 1
            db.create_all()
            flash('Admin verified!', 'success')
            return redirect(url_for('admin'))
    return render_template('adminlogin.html', title='Admin-Login', form=form)


@app.route("/admin", methods=['POST', 'GET'])
def admin():
    if flag:
        form = AdminForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = Admin(email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('User added to the database successfully', 'success')
    else:
        flash('Admin not logged in!', 'danger')
        return redirect(url_for('adminlogin'))
    return render_template('admin.html', title='Admin', form=form)

