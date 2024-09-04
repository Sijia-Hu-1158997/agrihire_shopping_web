'''
Author: Maggiefyer 109766140@qq.com
Date: 2024-05-07 20:15:59
LastEditors: Maggiefyer 109766140@qq.com
LastEditTime: 2024-06-02 11:02:38
FilePath: \COMP639S1_Project_2_Group_I\app\__init__.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import os
import app.secure as secure
import mysql.connector
from flask import Flask, app, g



def init_app():
    app = Flask(__name__)
    app.config.from_object("app.secure")


    # connect to the database
    app.config["SECRET_KEY"] = "SECRET_1234531231231312312312"
    app.secret_key = app.config["SECRET_KEY"]

    # Load configuration
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    
    @app.before_request
    def before_request():
        if "db_conn" not in g:
            g.db_conn = mysql.connector.connect(
                host=secure.dbhost,
                user=secure.dbuser,
                password=secure.dbpass,
                database=secure.dbname,
                port=secure.dbport,
            )

    @app.teardown_request
    def teardown_request(exception=None):
        db_conn = g.pop("db_conn", None)
        if db_conn is not None:
            db_conn.close()

    register_blueprint(app)
    return app

def register_blueprint(app):
    from app.web import web
    app.register_blueprint(web)   

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']