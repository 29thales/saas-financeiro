from app import db

class MonthlySettlement(db.Model):
    __tablename__ = 'monthly_settlements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    paid_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'paid': True,
            'month': self.month,
            'year': self.year,
            'amount': self.amount,
            'paid_date': self.paid_date.isoformat()
        }
