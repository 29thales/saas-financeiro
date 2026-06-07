from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.expense import Expense
from app.models.split import ExpenseSplit
from app.models.user import User

splits_bp = Blueprint('splits', __name__, url_prefix='/splits')

@splits_bp.route('/<int:expense_id>', methods=['POST'])
@login_required
def create_split(expense_id):
    # Verifica se a despesa existe e pertence ao usuário
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first()
    if not expense:
        return jsonify({'error': 'Despesa não encontrada'}), 404

    data = request.get_json()
    participants = data.get('participants', [])

    # participants é uma lista de usernames
    # ex: ["joao", "maria", "pedro"]
    if not participants:
        return jsonify({'error': 'Informe os participantes'}), 400

    # Deleta splits anteriores da despesa
    ExpenseSplit.query.filter_by(expense_id=expense_id).delete()

    # Divide igualmente entre os participantes
    amount_per_person = round(expense.amount / len(participants), 2)
    splits = []

    for username in participants:
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': f'Usuário {username} não encontrado'}), 404

        split = ExpenseSplit(
            expense_id=expense_id,
            user_id=user.id,
            amount=amount_per_person,
            paid=(user.id == current_user.id)  # quem criou já pagou
        )
        db.session.add(split)
        splits.append(split)

    db.session.commit()

    return jsonify({
        'message': f'Despesa de R${expense.amount} dividida entre {len(participants)} pessoas',
        'amount_per_person': amount_per_person,
        'splits': [s.to_dict() for s in splits]
    }), 201

@splits_bp.route('/<int:expense_id>', methods=['GET'])
@login_required
def get_splits(expense_id):
    splits = ExpenseSplit.query.filter_by(expense_id=expense_id).all()
    return jsonify([s.to_dict() for s in splits])

@splits_bp.route('/<int:split_id>/pay', methods=['PUT'])
@login_required
def mark_paid(split_id):
    split = ExpenseSplit.query.filter_by(id=split_id, user_id=current_user.id).first()
    if not split:
        return jsonify({'error': 'Split não encontrado'}), 404

    split.paid = True
    db.session.commit()
    return jsonify({'message': 'Pagamento registrado!', 'split': split.to_dict()})

@splits_bp.route('/balances', methods=['GET'])
@login_required
def get_balances():
    # Quanto o usuário atual deve para outros
    my_splits = ExpenseSplit.query.filter_by(
        user_id=current_user.id,
        paid=False
    ).all()

    # Quanto outros devem para o usuário atual
    # (despesas do usuário onde outros não pagaram)
    my_expenses = Expense.query.filter_by(user_id=current_user.id).all()
    my_expense_ids = [e.id for e in my_expenses]

    owed_to_me = ExpenseSplit.query.filter(
        ExpenseSplit.expense_id.in_(my_expense_ids),
        ExpenseSplit.user_id != current_user.id,
        ExpenseSplit.paid == False
    ).all()

    return jsonify({
        'i_owe': [s.to_dict() for s in my_splits],
        'owed_to_me': [s.to_dict() for s in owed_to_me],
        'total_i_owe': sum(s.amount for s in my_splits),
        'total_owed_to_me': sum(s.amount for s in owed_to_me)
    })