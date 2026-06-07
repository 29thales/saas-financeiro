import os
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.expense import Expense
from app.models.account import Account
from app.services.file_parser import parse_csv, parse_pdf_bradesco
from datetime import datetime

uploads_bp = Blueprint('uploads', __name__, url_prefix='/uploads')

@uploads_bp.route('/csv/', methods=['POST'])
@uploads_bp.route('/csv/<int:account_id>', methods=['POST'])
@login_required
def upload_csv(account_id=None):
    # Conta opcional
    account = None
    if account_id and account_id > 0:
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()

    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    filename = file.filename.lower()

    if filename.endswith('.csv'):
        expenses_data, errors = parse_csv(file)
    elif filename.endswith('.pdf'):
        year = request.args.get('year', datetime.now().year, type=int)
        expenses_data, errors = parse_pdf_bradesco(file, year)
    else:
        return jsonify({'error': 'Apenas arquivos CSV ou PDF sao aceitos'}), 400

    if expenses_data is None:
        return jsonify({'error': errors}), 400

    saved = []
    for data in expenses_data:
        expense = Expense(
            account_id=account.id if account else None,
            user_id=current_user.id,
            description=data['description'],
            amount=data['amount'],
            category=data.get('category', 'Outros'),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        )
        db.session.add(expense)
        saved.append(data)

    db.session.commit()

    return jsonify({
        'message': f'{len(saved)} despesas importadas com sucesso!',
        'imported': saved,
        'errors': errors
    }), 201
