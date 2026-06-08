import os
from app import create_app, db
from app.models.user import User
from app.models.account import Account
from app.models.expense import Expense
from app.models.fixed_expense import FixedExpense
from app.models.config import Config
from app.models.card_discount import CardDiscount
from app.models.camila_expense import CamilaExpense

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados inicializado!")
    app.run(host='0.0.0.0', port=5000, debug=False)