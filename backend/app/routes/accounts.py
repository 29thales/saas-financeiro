from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.account import Account

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

@accounts_bp.route('/', methods=['GET'])
@login_required
def list_accounts():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return jsonify([a.to_dict() for a in accounts])

@accounts_bp.route('/', methods=['POST'])
@login_required
def create_account():
    data = request.get_json()

    if not data.get('name') or not data.get('type'):
        return jsonify({'error': 'Nome e tipo são obrigatórios'}), 400

    account = Account(
        user_id=current_user.id,
        name=data['name'],
        type=data['type'],
        balance=data.get('balance', 0.0)
    )
    db.session.add(account)
    db.session.commit()

    return jsonify(account.to_dict()), 201

@accounts_bp.route('/<int:account_id>', methods=['PUT'])
@login_required
def update_account(account_id):
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()

    if not account:
        return jsonify({'error': 'Conta não encontrada'}), 404

    data = request.get_json()
    account.name = data.get('name', account.name)
    account.type = data.get('type', account.type)
    account.balance = data.get('balance', account.balance)
    db.session.commit()

    return jsonify(account.to_dict())

@accounts_bp.route('/<int:account_id>', methods=['DELETE'])
@login_required
def delete_account(account_id):
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()

    if not account:
        return jsonify({'error': 'Conta não encontrada'}), 404

    db.session.delete(account)
    db.session.commit()

    return jsonify({'message': 'Conta deletada com sucesso'})