from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    return redirect(url_for('views.login_page'))

@views_bp.route('/login')
def login_page():
    return render_template('login.html')

@views_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@views_bp.route('/contas')
@login_required
def contas():
    return render_template('contas.html')

@views_bp.route('/despesas')
@login_required
def despesas():
    return render_template('despesas.html')

@views_bp.route('/divisao')
@login_required
def divisao():
    return render_template('divisao.html')

@views_bp.route('/relatorios')
@login_required
def relatorios():
    return render_template('relatorios.html')

@views_bp.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        return redirect(url_for('views.dashboard'))
    return render_template('admin.html')

@views_bp.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('configuracoes.html')

@views_bp.route('/balanco')
@login_required
def balanco():
    return render_template('balanco.html')