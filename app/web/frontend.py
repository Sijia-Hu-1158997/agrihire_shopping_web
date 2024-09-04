from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_paginate import Pagination, get_page_parameter, get_page_args
from app.decorators.auth import auth_required
from app.models.user import UserModel
from . import web
from app.models.user import UserModel
from app.forms.user_form import UpdatePasswordForm, UpdateUserInfoForm  # Import your form class

from app.models.equipment import EquipmentModel

@web.route("/")
@web.route("/home")
def home():
    me = session.get("me") or {}


    equipment_model = EquipmentModel()
    all_equipments = equipment_model.get_all_equipment()
    view_equipments = all_equipments[-3:]

    return render_template(
        "frontend/home.html", me=me,view_equipments=view_equipments
    )


@web.route("/about")
def about():
    me = session.get("me") or {}
    return render_template(
        "frontend/about.html", me=me
    )
  
@web.route("/cart")
def cart():
    me = session.get("me") or {}
    return render_template(
        "frontend/cart.html", me=me
    )

@web.route("/checkout")
def checkout():
    me = session.get("me") or {}
    return render_template(
        "frontend/checkout.html", me=me
    )

@web.route("/contact")
def contact():
    me = session.get("me") or {}
    return render_template(
        "frontend/contact.html", me=me
    )

@web.route("/news")
def news():
    me = session.get("me") or {}
    return render_template(
        "frontend/news.html", me=me
    )

@web.route("/shop")
def shop():
    me = session.get("me") or {}
    return render_template(
        "frontend/shop.html", me=me
    )

@web.route("/news-detail")
def news_detail():
    me = session.get("me") or {}
    return render_template(
        "frontend/single-news.html", me=me
    )

@web.route("/product_detail")
def product_detail():
    me = session.get("me") or {}
    return render_template(
        "frontend/single-product.html", me=me
    )


@web.route("/404")
def not_found():
    return render_template(
        "frontend/404.html"
    )


