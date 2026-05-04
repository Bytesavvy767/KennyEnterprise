from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from models import Product, Order, User


def init_admin(app, db):
    admin = Admin(app, name='Kenny Enterprise Admin')
    with app.app_context():
        admin.add_view(ModelView(Product, db.session))
        admin.add_view(ModelView(Order, db.session))
        admin.add_view(ModelView(User, db.session))
