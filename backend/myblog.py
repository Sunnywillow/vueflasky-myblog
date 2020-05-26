from app import create_app, db
from app.models import User
app = create_app()


@app.shell_context_processor  # 上下文
def make_shell_context():
    return {'db': db, 'User': User}

