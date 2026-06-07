from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.fixed_expense import FixedExpense

fixed_bp = Blueprint('fixed', __name__, url_prefix='/fixed')

@fixed_bp.route('/', methods=['GET'])
@login_required
def list_fixed():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    query = FixedExpense.query.filter_by(user_id=current_user.id)
    if month:
        query = query.filter_by(month=month)
    if year:
        query = query.filter_by(year=year)
    items = query.order_by(FixedExpense.name).all()
    total = sum(i.amount for i in items)
    return jsonify({'items': [i.to_dict() for i in items], 'total': round(total, 2)})

@fixed_bp.route('/', methods=['POST'])
@login_required
def create_fixed():
    data = request.get_json()
    if not data.get('name') or not data.get('amount'):
        return jsonify({'error': 'Nome e valor obrigatorios'}), 400
    item = FixedExpense(
        user_id=current_user.id,
        name=data['name'],
        amount=data['amount'],
        month=data['month'],
        year=data['year']
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@fixed_bp.route('/<int:item_id>', methods=['PUT'])
@login_required
def update_fixed(item_id):
    item = FixedExpense.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Nao encontrado'}), 404
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.amount = data.get('amount', item.amount)
    db.session.commit()
    return jsonify(item.to_dict())

@fixed_bp.route('/<int:item_id>', methods=['DELETE'])
@login_required
def delete_fixed(item_id):
    item = FixedExpense.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Nao encontrado'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Deletado'})

@fixed_bp.route('/copy', methods=['POST'])
@login_required
def copy_from_previous():
    """Copia despesas fixas do mês anterior para o mês atual."""
    data = request.get_json()
    month = data['month']
    year = data['year']

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1

    previous = FixedExpense.query.filter_by(
        user_id=current_user.id,
        month=prev_month,
        year=prev_year
    ).all()

    if not previous:
        return jsonify({'error': 'Nenhuma despesa no mes anterior'}), 404

    # Verifica se já existe para o mês atual
    existing = FixedExpense.query.filter_by(
        user_id=current_user.id,
        month=month,
        year=year
    ).first()

    if existing:
        return jsonify({'error': 'Mes atual ja possui despesas fixas'}), 400

    for p in previous:
        new = FixedExpense(
            user_id=current_user.id,
            name=p.name,
            amount=p.amount,
            month=month,
            year=year
        )
        db.session.add(new)

    db.session.commit()
    return jsonify({'message': f'{len(previous)} despesas copiadas do mes anterior!'})