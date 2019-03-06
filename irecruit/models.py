from irecruit import db


class Question(db.Model):
    question_id = db.Column(db.VARCHAR(10), primary_key=True)
    question = db.Column(db.VARCHAR(500), unique=True)
    question_answer = db.Column(db.VARCHAR(500), unique=True)
    question_level = db.Column(db.VARCHAR(20))
    question_chosen = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Question('{self.question}')"
