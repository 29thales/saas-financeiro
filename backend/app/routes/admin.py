from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Decorator que bloqueia quem não for admin
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Acesso negado'}), 403
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at).all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'created_at': u.created_at.strftime('%d/%m/%Y')
    } for u in users])

@admin_bp.route('/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    data = request.get_json()

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já cadastrado'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username já existe'}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'user')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': f'Usuário {user.username} criado com sucesso!'}), 201

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    if user.role == 'admin':
        return jsonify({'error': 'Não é possível deletar um administrador'}), 400

    try:
        from app.models.split import ExpenseSplit
        from app.models.expense import Expense

        # Deleta splits do usuário
        ExpenseSplit.query.filter_by(user_id=user_id).delete()

        # Deleta splits das despesas do usuário
        expenses = Expense.query.filter_by(user_id=user_id).all()
        for e in expenses:
            ExpenseSplit.query.filter_by(expense_id=e.id).delete()

        # Deleta despesas do usuário
        Expense.query.filter_by(user_id=user_id).delete()

        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuário deletado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500