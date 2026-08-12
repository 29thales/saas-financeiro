from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from app import db
from app.models.daily_expense import DailyExpense, DailyExpenseLog

daily_bp = Blueprint('daily', __name__, url_prefix='/daily-expenses')


# ---------- Templates (regras de gasto recorrente) ----------

@daily_bp.route('/templates', methods=['GET'])
@login_required
def list_templates():
    only_active = request.args.get('active')
    query = DailyExpense.query.filter_by(user_id=current_user.id)
    if only_active == 'true':
        query = query.filter_by(active=True)
    items = query.order_by(DailyExpense.name).all()
    return jsonify([i.to_dict() for i in items])


@daily_bp.route('/templates', methods=['POST'])
@login_required
def create_template():
    data = request.get_json()
    if not data.get('name') or data.get('amount') is None:
        return jsonify({'error': 'Nome e valor sao obrigatorios'}), 400

    item = DailyExpense(
        user_id=current_user.id,
        name=data['name'],
        amount=data['amount'],
        category=data.get('category', 'Diário'),
        active=data.get('active', True)
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@daily_bp.route('/templates/<int:template_id>', methods=['PUT'])
@login_required
def update_template(template_id):
    item = DailyExpense.query.filter_by(id=template_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Nao encontrado'}), 404

    data = request.get_json()
    item.name = data.get('name', item.name)
    item.amount = data.get('amount', item.amount)
    item.category = data.get('category', item.category)
    if 'active' in data:
        item.active = data['active']

    db.session.commit()
    return jsonify(item.to_dict())


@daily_bp.route('/templates/<int:template_id>', methods=['DELETE'])
@login_required
def delete_template(template_id):
    item = DailyExpense.query.filter_by(id=template_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Nao encontrado'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Regra deletada com sucesso'})


# ---------- Lançamentos (ocorrência em um dia específico) ----------

@daily_bp.route('/generate', methods=['POST'])
@login_required
def generate_today():
    """Cria o lançamento do dia (ou de uma data específica) para cada regra ativa,
    pulando as que já foram lançadas nesse dia."""
    data = request.get_json(silent=True) or {}
    target_date = data.get('date')
    target_date = datetime.strptime(target_date, '%Y-%m-%d').date() if target_date else date.today()

    templates = DailyExpense.query.filter_by(user_id=current_user.id, active=True).all()

    already = {
        log.daily_expense_id
        for log in DailyExpenseLog.query.filter_by(user_id=current_user.id, date=target_date).all()
    }

    created = []
    for t in templates:
        if t.id in already:
            continue
        log = DailyExpenseLog(
            daily_expense_id=t.id,
            user_id=current_user.id,
            date=target_date,
            amount=t.amount
        )
        db.session.add(log)
        created.append(log)

    db.session.commit()
    return jsonify({
        'message': f'{len(created)} lançamento(s) criado(s) para {target_date.isoformat()}',
        'items': [c.to_dict() for c in created]
    }), 201


@daily_bp.route('/', methods=['GET'])
@login_required
def list_logs():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = DailyExpenseLog.query.filter_by(user_id=current_user.id)
    if start_date:
        query = query.filter(DailyExpenseLog.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(DailyExpenseLog.date <= datetime.strptime(end_date, '%Y-%m-%d').date())

    logs = query.order_by(DailyExpenseLog.date.desc()).all()
    total = sum(l.amount for l in logs)
    return jsonify({'items': [l.to_dict() for l in logs], 'total': round(total, 2)})


@daily_bp.route('/<int:log_id>', methods=['PUT'])
@login_required
def update_log(log_id):
    log = DailyExpenseLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    if not log:
        return jsonify({'error': 'Lançamento nao encontrado'}), 404

    data = request.get_json()
    if data.get('amount') is not None:
        log.amount = data['amount']
    if data.get('date'):
        log.date = datetime.strptime(data['date'], '%Y-%m-%d').date()

    db.session.commit()
    return jsonify(log.to_dict())


@daily_bp.route('/<int:log_id>', methods=['DELETE'])
@login_required
def delete_log(log_id):
    log = DailyExpenseLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    if not log:
        return jsonify({'error': 'Lançamento nao encontrado'}), 404

    db.session.delete(log)
    db.session.commit()
    return jsonify({'message': 'Lançamento deletado com sucesso'})
