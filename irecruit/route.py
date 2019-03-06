from flask import render_template, url_for, request, jsonify
from irecruit.models import Question
from irecruit import app, db
import random



@app.route('/chat_retrieval')
def chat_retrieval():
    answr = request.args.get('answer')
    items = Question.query.all()
    while True:
        i = random.randint(0, len(items) - 1)
        if (items[i].question_chosen == 0):
            break

    if(answr):
        reply = items[i]
        reply.question_chosen = 1
        db.session.commit()
        return jsonify(result=reply.question)

@app.route('/')
def chat_interview():
    return render_template('chat.html', items=Question.query.all())
