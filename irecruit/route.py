from flask import render_template, request, jsonify, Response
from camera import VideoCamera
from irecruit.models import Question
from irecruit import app, db
import random


#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')


@app.route('/chat_retrieval')
def chat_retrieval():
    answr = request.args.get('answer')
    items = Question.query.all()

    while True:
        i = random.randint(0, len(items) - 1)
        if (items[i].question_chosen == 0):
            break

    if(answr):

        #nouns = []
        #for word, pos in nltk.pos_tag(nltk.word_tokenize(str(answr))):
            #if(pos.startswith('NN')):
                #nouns.append(word)
        #print(nouns)
        #i = random.randint(0, len(nouns) - 1)
        #words = nouns[i]
        #question = "What do you mean by " + words
        reply = items[i]
        reply.question_chosen = 1
        db.session.commit()
        return jsonify(result=reply.question)


@app.route('/')
def chat_interview():
    return render_template('chat.html', items=Question.query.all())


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')
