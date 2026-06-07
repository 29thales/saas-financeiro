from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.config import Config

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET'])
@login_required
def get_settings():
    configs = Config.query.filter_by(user_id=current_user.id).all()
    return jsonify({c.key: c.value for c in configs})

@settings_bp.route('/', methods=['POST'])
@login_required
def save_settings():
    data = request.get_json()
    for key, value in data.items():
        config = Config.query.filter_by(user_id=current_user.id, key=key).first()
        if config:
            config.value = str(value)
        else:
            config = Config(user_id=current_user.id, key=key, value=str(value))
            db.session.add(config)
    db.session.commit()
    return jsonify({'message': 'Configuracoes salvas!'})