from app.models.user import UserModel
from werkzeug.utils import secure_filename
from flask import (
    app,
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
from app.forms.user_form import UpdateUserInfoForm, RegisterForm, AdminRegisterForm
from . import web
from app.models.news import NewsModel
from app.forms.news_form import AddNewsForm

import os
import datetime


@web.route("/admin/customers", methods=["GET", "POST"])
@auth_required(roles=['local_manager', 'national_manager','admin', 'staff'])
def admin_customers():
    me = session.get("me") or {}
    role = "customer"
    users = UserModel().get_user_list_by_field('role', role)
    return render_template("cms/admin_user_list.html", me=me, users=users)


@web.route("/admin/staffs", methods=["GET", "POST"])
@auth_required(roles=['local_manager', 'national_manager','admin'])
def admin_staffs():
    me = session.get("me") or {}
    role = "staff"
    users = UserModel().get_user_list_by_field('role', role)
    return render_template("cms/admin_user_list.html", me=me, users=users)


@web.route("/admin/local_managers", methods=["GET", "POST"])
@auth_required(roles=['national_manager','admin'])
def admin_local_managers():
    me = session.get("me") or {}
    role = "local_manager"
    users = UserModel().get_user_list_by_field('role', role)
    return render_template("cms/admin_user_list.html", me=me, users=users)


@web.route("/admin/national_managers", methods=["GET", "POST"])
@auth_required(roles=['admin'])
def admin_national_managers():
    me = session.get("me") or {}
    role = "national_manager"
    users = UserModel().get_user_list_by_field('role', role)
    return render_template("cms/admin_user_list.html", me=me, users=users)



@web.route("/admin/update/<id>/user", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def admin_update_user(id):
    me = session.get("me") or {}
    if request.method == "GET":
        user = UserModel().get_user_list_by_field(field_name="id", field_value=id)
    
    if request.method == "POST":
        form = UpdateUserInfoForm(request.form)
        if form.validate():
            UserModel().update_user_info(id, form.data)
            flash("Updated successfully", "success")
            user = UserModel().get_user_list_by_field(field_name="id", field_value=id) 
        else:
            flash(form.errors, "danger")
            user = UserModel().get_user_list_by_field(field_name="id", field_value=id)
    return render_template("/cms/admin_user_update.html", me=me, user=user[0])


@web.route("/admin/update/<id>/password", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def admin_update_password(id):
    me = session.get("me") or {}
    if request.method == "GET":
        user = UserModel().get_user_list_by_field(field_name="id", field_value=id)
    
    if request.method == "POST":
        form = UpdateUserInfoForm(request.form)
        if form.validate() and form.data['password']:
            UserModel().update_password(id, form.data['password'])
            flash("Updated password successfully", "success")
            user = UserModel().get_user_list_by_field(field_name="id", field_value=id) 
        else:
            flash(form.errors, "danger")
            user = UserModel().get_user_list_by_field(field_name="id", field_value=id)
    return render_template("/cms/admin_user_changepassword.html", me=me, user=user[0])

        
@web.route("/delete/<id>/user", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager','national_manager','admin'])
def delete_user(id):
    user_list = UserModel().get_user_list_by_field(field_name="id", field_value=id)
    user = user_list[0] 
    role = user.get("role")

    if not user_list:
        flash("User not found", "danger")
        return redirect(url_for("web.admin_customers"))
    if user.get("is_deleted"):
        UserModel().update_user_info(id, {"is_deleted": False})
        flash("Restored successfully", "success")
    else:
        UserModel().update_user_info(id, {"is_deleted": True})
        flash("Deleted successfully", "success")
    endpoint = f"web.admin_{role}s"
    return redirect(url_for(endpoint))

  

@web.route("/admin/users/adduser", methods=["GET", "POST"])
@auth_required(roles=['local_manager', 'national_manager','admin'])
def add_user():
    me = session.get("me") or {}
    if request.method == "POST":
        form = AdminRegisterForm(request.form)
        role = form.data.get("role")
        if form.validate():
            UserModel().admin_register_user(form.data) 
            flash("Add successfully!", "success")
            endpoint = f"web.admin_{role}s"
            return redirect(url_for(endpoint))
        else:
            flash(form.errors, "danger")
    return render_template("cms/admin_user_add.html", me=me)


@web.route("/admin_customer_list", methods=["GET", "POST"])
@auth_required(roles=["staff", "local_manager", "national_manager", "admin"])
def admin_customer_list():
    me = session.get("me") or {}
    user_model = UserModel()
    if request.method == "POST":
        query = request.form.get("query")
    else:
        query = request.args.get("query")
        search = False
        if query:
            search = True
        page = request.args.get("page", type=int, default=1)
        per_page = 10
        offset = (page - 1) * per_page
        users = user_model.get_customers(query=query)
        users_for_render = users[offset : offset + per_page]
        pagination = Pagination(
            page=page,
            total=len(users),
            per_page=per_page,
            search=search,
            record_name="users",
        )
        return render_template(
            "cms/admin_customer_list.html", me=me, users=users_for_render, pagination=pagination
        )

    users = user_model.get_customers(query=query)

    return render_template("cms/admin_customer_list.html", me=me, users=users)
