"""StudyTask 应用工厂。"""

from pathlib import Path

from flask import Flask, render_template

from . import db
from .config import Config


def create_app(config=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)

    database = Path(app.config["DATABASE"])
    database.parent.mkdir(parents=True, exist_ok=True)
    app.config["DATABASE"] = str(database)

    from .views.tasks import bp

    app.register_blueprint(bp)
    app.teardown_appcontext(db.close_db)

    register_error_handlers(app)

    with app.app_context():
        db.init_db()

    return app


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(error):
        message = getattr(error, "description", None) or "请求参数不合法。"
        return render_template("error.html", code=400, title="请求有误", message=message), 400

    @app.errorhandler(404)
    def not_found(error):
        message = getattr(error, "description", None) or "您访问的页面不存在。"
        return render_template("error.html", code=404, title="页面不存在", message=message), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            render_template(
                "error.html",
                code=405,
                title="请求方式不被支持",
                message="该操作只接受表单提交，请从页面上的按钮重新操作。",
            ),
            405,
        )

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("internal error: %s", error)
        return (
            render_template(
                "error.html",
                code=500,
                title="服务器开小差了",
                message="数据保存失败或服务暂时不可用，请稍后重试。",
            ),
            500,
        )
