from flask import Flask, render_template
from app.extensions import mongo
from app.webhook.routes import webhook


def create_app():
    app = Flask(__name__)
    
    from config import BaseConfig
    app.config.from_object(BaseConfig)
    
    
    mongo.init_app(app)
    
    
    
    app.register_blueprint(webhook)
    
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Page Not Found",
                             error_description="The page you're looking for doesn't exist."), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Internal Server Error",
                             error_description="Something went wrong on our end. Please try again later."), 500
    
    return app
