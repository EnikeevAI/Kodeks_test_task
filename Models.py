from config import db


class Vacancies(db.Model):
    __tablename__ = 'vacancies'

    id = db.Column(db.Integer, primary_key=True)
    key_skills = db.Column(db.String(300))
    vacancy_name = db.Column(db.String(100))
    salary_from = db.Column(db.Integer)
    salary_to = db.Column(db.Integer)
    description = db.Column(db.String(2000))
    vacancy_link = db.Column(db.String(50))

