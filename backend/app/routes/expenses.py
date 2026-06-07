from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.expense import Expense
from app.models.account import Account

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses_bp.route('/', methods=['GET'])
@login_required
def list_expenses():
    category = request.args.get('category')
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Expense.query.filter_by(user_id=current_user.id)

    if category:
        query = query.filter_by(category=category)
    if account_id:
        query = query.filter_by(account_id=account_id)
    if start_date:
        query = query.filter(Expense.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Expense.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

    expenses = query.order_by(Expense.date.desc()).all()
    return jsonify([e.to_dict() for e in expenses])


@expenses_bp.route('/', methods=['POST'])
@login_required
def create_expense():
    data = request.get_json()

    if not data.get('description') or not data.get('amount'):
        return jsonify({'error': 'Descricao e valor sao obrigatorios'}), 400

    account_id = data.get('account_id') or None

    if account_id:
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            return jsonify({'error': 'Conta nao encontrada'}), 404

    expense = Expense(
        account_id=account_id,
        user_id=current_user.id,
        description=data['description'],
        amount=data['amount'],
        category=data.get('category', 'Outros'),
        date=datetime.strptime(data['date'], '%Y-%m-%d').date()
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.to_dict()), 201


@expenses_bp.route('/<int:expense_id>', methods=['PUT'])
@login_required
def update_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first()
    if not expense:
        return jsonify({'error': 'Despesa nao encontrada'}), 404

    data = request.get_json()
    expense.description = data.get('description', expense.description)
    expense.amount = data.get('amount', expense.amount)
    expense.category = data.get('category', expense.category)
    if data.get('date'):
        expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date()

    db.session.commit()
    return jsonify(expense.to_dict())


@expenses_bp.route('/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first()
    if not expense:
        return jsonify({'error': 'Despesa nao encontrada'}), 404

    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Despesa deletada com sucesso'})
