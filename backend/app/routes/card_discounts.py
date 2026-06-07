from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.card_discount import CardDiscount

discounts_bp = Blueprint('discounts', __name__, url_prefix='/discounts')

@discounts_bp.route('/', methods=['GET'])
@login_required
def list_discounts():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    items = CardDiscount.query.filter_by(
        user_id=current_user.id,
        month=month,
        year=year
    ).all()
    total = sum(i.amount for i in items)
    return jsonify({'items': [i.to_dict() for i in items], 'total': round(total, 2)})

@discounts_bp.route('/', methods=['POST'])
@login_required
def create_discount():
    data = request.get_json()
    if not data.get('name') or not data.get('amount'):
        return jsonify({'error': 'Nome e valor obrigatorios'}), 400
    item = CardDiscount(
        user_id=current_user.id,
        name=data['name'],
        amount=data['amount'],
        month=data['month'],
        year=data['year']
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@discounts_bp.route('/<int:item_id>', methods=['DELETE'])
@login_required
def delete_discount(item_id):
    item = CardDiscount.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Nao encontrado'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Deletado'})