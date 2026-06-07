from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app import db
from app.models.expense import Expense

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/monthly', methods=['GET'])
@login_required
def monthly_summary():
    # Parâmetros: ?year=2026&month=6
    year = request.args.get('year', 2026, type=int)
    month = request.args.get('month', 6, type=int)

    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == year,
        extract('month', Expense.date) == month
    ).all()

    total = sum(e.amount for e in expenses)

    # Agrupa por categoria
    by_category = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0) + e.amount

    # Ordena do maior para o menor
    by_category = dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True))

    return jsonify({
        'year': year,
        'month': month,
        'total': round(total, 2),
        'count': len(expenses),
        'by_category': {k: round(v, 2) for k, v in by_category.items()},
        'expenses': [e.to_dict() for e in expenses]
    })

@reports_bp.route('/comparison', methods=['GET'])
@login_required
def monthly_comparison():
    # Compara os últimos 6 meses
    results = db.session.query(
        extract('year', Expense.date).label('year'),
        extract('month', Expense.date).label('month'),
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count')
    ).filter(
        Expense.user_id == current_user.id
    ).group_by(
        extract('year', Expense.date),
        extract('month', Expense.date)
    ).order_by(
        extract('year', Expense.date).desc(),
        extract('month', Expense.date).desc()
    ).limit(6).all()

    return jsonify([{
        'year': int(r.year),
        'month': int(r.month),
        'total': round(float(r.total), 2),
        'count': r.count
    } for r in results])

@reports_bp.route('/categories', methods=['GET'])
@login_required
def categories_summary():
    # Total gasto por categoria em todos os tempos
    results = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total'),
        func.count(Expense.id).label('count')
    ).filter(
        Expense.user_id == current_user.id
    ).group_by(
        Expense.category
    ).order_by(
        func.sum(Expense.amount).desc()
    ).all()

    return jsonify([{
        'category': r.category,
        'total': round(float(r.total), 2),
        'count': r.count
    } for r in results])

@reports_bp.route('/biggest', methods=['GET'])
@login_required
def biggest_expenses():
    # Top 5 maiores despesas
    year = request.args.get('year', 2026, type=int)
    month = request.args.get('month', 6, type=int)

    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == year,
        extract('month', Expense.date) == month
    ).order_by(Expense.amount.desc()).limit(5).all()

    return jsonify([e.to_dict() for e in expenses])