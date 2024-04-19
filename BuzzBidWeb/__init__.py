from flask import Flask, session

def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sss'

    from .views import views
    from .authentication import auth
    from .search_items_view import search_items_view
    from .item_description_view import item_description_view

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    app.register_blueprint(search_items_view, url_prefix = '/')
    app.register_blueprint(item_description_view, url_prefix = '/')

    @app.before_request
    def clear_session():
        app.before_request_funcs[None].remove(clear_session)
        session.clear()

    return app
