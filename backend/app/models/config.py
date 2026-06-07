from app import db

class Config(db.Model):
    __tablename__ = 'configs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(200), nullable=False)

    user = db.relationship('User', backref='configs')

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }