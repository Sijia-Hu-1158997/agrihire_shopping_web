'''
Author: Maggiefyer 109766140@qq.com
Date: 2024-05-07 20:16:04
LastEditors: Maggiefyer 109766140@qq.com
LastEditTime: 2024-05-31 04:03:44
FilePath: \COMP639S1_Project_2_Group_I\app\web\backend.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from app.models.message import MessageModel
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
from app.forms.user_form import UpdateUserInfoForm, RegisterForm, AdminRegisterForm
from . import web
from flask import g


# Write your CMS routes here
def get_dashboard_data():
    cursor = g.db_conn.cursor(dictionary=True)

    # Products Rented Out (count of active booking items)
    query_products_rented_out = "SELECT COUNT(*) AS products_rented_out FROM booking_items"
    cursor.execute(query_products_rented_out)
    products_rented_out = cursor.fetchone()['products_rented_out']

    # Total Paid Amount (sum of total from paid invoices)
    query_total_paid_amount = "SELECT SUM(total) AS total_paid_amount FROM invoice WHERE status = 'paid'"
    cursor.execute(query_total_paid_amount)
    total_paid_amount = cursor.fetchone()['total_paid_amount']

    # Total Customers (count of customers)
    query_total_customers = "SELECT COUNT(*) AS total_customers FROM users WHERE role = 'customer'"
    cursor.execute(query_total_customers)
    total_customers = cursor.fetchone()['total_customers']

    # Total Staff Members (count of staff, including admin and managers)
    query_total_staff_members = """
        SELECT COUNT(*) AS total_staff_members 
        FROM users 
        WHERE role IN ('staff', 'local_manager', 'national_manager', 'admin')
    """
    cursor.execute(query_total_staff_members)
    total_staff_members = cursor.fetchone()['total_staff_members']

    cursor.close()

    return {
        'products_rented_out': products_rented_out,
        'total_paid_amount': total_paid_amount,
        'total_customers': total_customers,
        'total_staff_members': total_staff_members
    }

@web.route("/dashboard", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def admin_home():
    me = session.get("me") or {}
    if not me:
        return redirect(url_for("web.login"))

    dashboard_data = get_dashboard_data()
    return render_template("cms/dashboard.html", me=me, data=dashboard_data)

# @web.route("/dashboard", methods=["GET", "POST"])
# @auth_required(roles=['staff', 'local_manager','national_manager','admin'])
# def admin_home():
#     me = session.get("me") or {}
#     if not me:
#         return redirect(url_for("web.login"))
#     return render_template("cms/dashboard.html", me=me)


@web.route("/admin/profile", methods=["GET", "POST"])
# @auth_required(roles=['instructor', 'manager'])
def admin_profile():
    return render_template("cms/admin_profile.html")


@web.route("/admin/table", methods=["GET", "POST"])
# @auth_required(roles=['instructor', 'manager'])
def admin_table():
    me = session.get("me") or {}
    return render_template("cms/admin_table.html", me=me)

@web.route("/admin/bookings", methods=["GET", "POST"])
@auth_required(roles=["local_manager", "customer", "national_manager", "staff", "admin"])
def admin_bookings():
  me = session.get("me") or {}

  return render_template(
        "cms/admin_bookings.html",
        me=me,
    )
@web.route("/admin/checkout", methods=["GET", "POST"])
@auth_required(roles=["local_manager", "national_manager", "staff"])
def admin_checkout():
  me = session.get("me") or {}

  return render_template(
        "cms/admin_checkout.html",
        me=me,
    )

@web.route("/admin/returnin", methods=["GET", "POST"])
@auth_required(roles=["local_manager", "national_manager", "staff"])
def admin_returnin():
  me = session.get("me") or {}

  return render_template(
        "cms/admin_returnin.html",
        me=me,
    )

@web.route("/admin/categories", methods=["GET", "POST"])
@auth_required(roles=["local_manager", "national_manager", "staff"])
def admin_categories():
  me = session.get("me") or {}

  return render_template(
        "cms/admin_categories.html",
        me=me,
    )


@web.route("/member_feedback", methods=["GET", "POST"])
@auth_required(roles=['local_manage', 'national_manager','admin'])
def add_feedback():
    me = session.get("me") or {}
    user_model = UserModel()
    user_id = me.get("id")
    if request.method == "POST":
        data = {
            "title": request.form.get("title"),
            "content": request.form.get("content"),
            "feedback_user_id": user_id
        }
        user_model.add_feedback(data)
        flash("Thank you. Your feedback has been sent successfully!", "success")
    return render_template("member_feedback.html", me=me)

@web.route("/admin_feedback", methods=["GET", "POST"])
@auth_required(roles=['local_manage', 'national_manager','admin'])
def admin_feedback():
    # TO DO: fix the bug for pagination "found 0 feedback, displaying 1 - 0"
    me = session.get("me") or {}
    user_model = UserModel()
    query = request.args.get("query")
    search = False
    if query:
        search = True
    page = request.args.get('page', type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    feedbacks = user_model.get_feedback(query=query)
    feedbacks_for_render = feedbacks[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(feedbacks), per_page=per_page, search=search, record_name='feedback')
    return render_template("admin_feedback.html", me=me, feedbacks=feedbacks_for_render, pagination=pagination)

@web.route("/admin/checkout", methods=["GET", "POST"])
@auth_required(roles=['staff','local_manage', 'national_manager','admin'])
def admin_attendance():
    me = session.get("me") or {}

    #workshop_model = shopModel()
    #workshop_courses = workshop_model.get_workshops()

    #lesson_model = LessonModel()
    #lesson_courses = lesson_model.get_lessons()
    #return render_template("admin_attendance.html", me=me,workshop_courses=workshop_courses,lesson_courses=lesson_courses)
    return render_template("admin_checkout.html")