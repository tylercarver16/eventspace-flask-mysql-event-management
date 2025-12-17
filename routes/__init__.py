from .main import bp as main_bp
from .booking import bp as booking_bp
from .manager import bp as manager_bp
from .predictor import bp as predictor_bp

def init_app(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(predictor_bp)