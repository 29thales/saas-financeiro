from app import db


class DailyExpense(db.Model):
    """Regra/template de um gasto que se repete todo dia (ex: café, almoço, uber)."""
    __tablename__ = 'daily_expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)          # valor padrão/sugerido
    category = db.Column(db.String(100), default='Diário')
    active = db.Column(db.Boolean, default=True)           # se False, para de ser lançado
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref='daily_expenses')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'category': self.category,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }


class DailyExpenseLog(db.Model):
    """Lançamento efetivo de um DailyExpense em um dia específico."""
    __tablename__ = 'daily_expense_logs'
    __table_args__ = (
        db.UniqueConstraint('daily_expense_id', 'date', name='uq_daily_expense_date'),
    )

    id = db.Column(db.Integer, primary_key=True)
    daily_expense_id = db.Column(db.Integer, db.ForeignKey('daily_expenses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)  # pode divergir do valor padrão naquele dia
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    daily_expense = db.relationship('DailyExpense', backref='logs')

    def to_dict(self):
        return {
            'id': self.id,
            'daily_expense_id': self.daily_expense_id,
            'name': self.daily_expense.name,
            'category': self.daily_expense.category,
            'date': self.date.isoformat(),
            'amount': self.amount,
            'created_at': self.created_at.isoformat()
        }
