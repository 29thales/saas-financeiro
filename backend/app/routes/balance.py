from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.fixed_expense import FixedExpense
from app.models.expense import Expense
from app.models.card_discount import CardDiscount
from sqlalchemy import extract

balance_bp = Blueprint('balance', __name__, url_prefix='/balance')

@balance_bp.route('/', methods=['GET'])
@login_required
def get_balance():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    fixed = FixedExpense.query.filter_by(
        user_id=current_user.id, month=month, year=year
    ).all()
    total_fixed = sum(f.amount for f in fixed)

    card_expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).all()
    total_card = sum(e.amount for e in card_expenses)

    discounts = CardDiscount.query.filter_by(
        user_id=current_user.id, month=month, year=year
    ).all()
    total_discounts = sum(d.amount for d in discounts)

    card_liquido = total_card - total_discounts
    total_geral = total_fixed + card_liquido
    cada_um_paga = total_geral / 2
    thales_deve = cada_um_paga - total_fixed
    camila_deve = cada_um_paga - card_liquido

    if thales_deve > 0.01:
        result = {'who': 'thales', 'message': 'Thales deve para Camila', 'amount': round(thales_deve, 2)}
    elif camila_deve > 0.01:
        result = {'who': 'camila', 'message': 'Camila deve para Thales', 'amount': round(camila_deve, 2)}
    else:
        result = {'who': 'none', 'message': 'Estao quites!', 'amount': 0}

    return jsonify({
        'total_fixed': round(total_fixed, 2),
        'total_card': round(total_card, 2),
        'total_discounts': round(total_discounts, 2),
        'card_liquido': round(card_liquido, 2),
        'total_geral': round(total_geral, 2),
        'cada_um_paga': round(cada_um_paga, 2),
        'thales_total': round(total_fixed, 2),
        'camila_total': round(card_liquido, 2),
        'result': result
    })