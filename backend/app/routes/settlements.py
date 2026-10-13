from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.settlement import MonthlySettlement

settlements_bp = Blueprint('acertos', __name__, url_prefix='/acertos')


def _buscar(month, year):
    return MonthlySettlement.query.filter_by(user_id=current_user.id, month=month, year=year).first()


@settlements_bp.route('/', methods=['GET'])
@login_required
def get_settlement():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    item = _buscar(month, year)
    if item is None:
        return jsonify({'paid': False})
    return jsonify(item.to_dict())


@settlements_bp.route('/', methods=['POST'])
@login_required
def marcar_pago():
    data = request.get_json() or {}
    month = data.get('month')
    year = data.get('year')
    amount = float(data.get('amount', 0))
    try:
        paid_date = date.fromisoformat(data.get('paid_date'))
    except Exception:
        paid_date = date.today()
    item = _buscar(month, year)
    if item is None:
        item = MonthlySettlement(user_id=current_user.id, month=month, year=year,
                          amount=amount, paid_date=paid_date)
        db.session.add(item)
    else:
        item.amount = amount
        item.paid_date = paid_date
    db.session.commit()
    return jsonify(item.to_dict())


@settlements_bp.route('/', methods=['DELETE'])
@login_required
def desmarcar_pago():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    item = _buscar(month, year)
    if item is not None:
        db.session.delete(item)
        db.session.commit()
    return jsonify({'paid': False})
