from datetime import datetime, timedelta, timezone
from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for, g
)

from app.forms.user_form import RegisterForm, UpdatePasswordForm, UpdateUserInfoForm, SignInForm
from app.models.user import UserModel
from . import web
from flask_paginate import Pagination, get_page_parameter, get_page_args
from app.decorators.auth import auth_required
from app.models.reminder import ReminderModel


@web.route("/register")
def register():
    me = session.get("me") or {}
    return render_template("register.html", me=me)


@web.route("/register/step/init", methods=["POST"])
def register_step_init():
    form = RegisterForm(request.form)
    userModel = UserModel()
    if form.validate():
        userModel.register_user(form.data)
        me = userModel.get_user_by_field(
            field_name="email", field_value=form.email.data
        )
        session["me"] = me
    else:
        flash(form.errors, "danger")
    return redirect(url_for("web.register"))


# step 2
@web.route("/register/step/one", methods=["POST"])
def register_step_one():
    form = UpdateUserInfoForm(request.form)
    userModel = UserModel()
    me = session.get("me")
    if form.validate():
        form.onboarding.data = 2
        userModel.update_user_info(me["id"], form.data)
        me = userModel.get_user_by_field(field_name="id", field_value=me["id"])
        session["me"] = me
    else:
        flash(form.errors, "danger")
    return redirect(url_for("web.register"))


@web.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = SignInForm(request.form)
        if form.validate():
            userModel = UserModel()
            me = userModel.check_password(form.username.data, form.password.data)
            if me:
                session["me"] = me
                flash("You have been signed in.", "success")
            else:
                flash("Invalid username or password.", "danger")
        else:
            flash(form.errors, "danger")

    me = session.get("me") or {}
    today_date = datetime.now().date()

    if me:
        user_id = me.get("id")
        reminder_model = ReminderModel()
        booking_data = reminder_model.get_booking_items_by_user_id(user_id)
        reminder_days = timedelta(days=3)

        collect_reminders = {}
        return_reminders = {}

        if me.get("role") == "customer" and booking_data:
            for booking_id, hire_dates in booking_data.items():
                for dates in hire_dates:
                    hire_start = dates['hire_start'].date()
                    hire_end = dates['hire_end'].date()
                    hire_start_formatted = hire_start.strftime('%d/%m/%Y')
                    hire_end_formatted = hire_end.strftime('%d/%m/%Y')

                    if today_date <= hire_start <= today_date + reminder_days:
                        if hire_start_formatted not in collect_reminders:
                            collect_reminders[hire_start_formatted] = []
                        collect_reminders[hire_start_formatted].append(booking_id)

                    if today_date <= hire_end <= today_date + reminder_days:
                        if hire_end_formatted not in return_reminders:
                            return_reminders[hire_end_formatted] = []
                        return_reminders[hire_end_formatted].append(booking_id)

        flash_messages = []

        if collect_reminders:
            unique_collect_booking_ids = set()
            for ids in collect_reminders.values():
                unique_collect_booking_ids.update(ids)
            
            collect_message = ', '.join(map(str, unique_collect_booking_ids))
            flash_messages.append(f"Reminder: You have equipment under booking IDs {collect_message} to be collected in three days.")

        if return_reminders:
            unique_return_booking_ids = set()
            for ids in return_reminders.values():
                unique_return_booking_ids.update(ids)
            
            return_message = ', '.join(map(str, unique_return_booking_ids))
            flash_messages.append(f"Reminder: You have equipment under booking IDs {return_message} to be returned in three days.")

        # Flash at most two reminders
        for message in flash_messages[:2]:
            flash(message, "warning")

        if me.get("onboarding") != 2 and me.get("role") == "customer":
            flash("You must complete the registration process first.", "success")
            return redirect(url_for("web.register"))

        if me.get("role") == "customer" and reminder_model.get_pending_bookings(user_id):
            flash("Please confirm your booking and finish the payment!", "danger")
            return redirect(url_for("web.booking_list"))

        # 添加以下两行：获取dashboard数据并传递给模板
        if me.get("role") in ["staff", "local_manager", "national_manager", "admin"]:
            dashboard_data = get_dashboard_data()  # 获取dashboard数据
            return render_template("cms/dashboard.html", me=me, data=dashboard_data)  # 确保传递data变量

    else:
        return render_template("login.html")

    return redirect(url_for("web.home"))

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



#change password page
@web.route("/changepassword", methods=["GET", "POST"])
@auth_required(roles=['customer', 'staff', 'local_manager', 'national_manager', 'admin'])
def changepassword():
    me = session.get("me") or {}
    form = UpdatePasswordForm() # initialize form
    user_model = UserModel()

    if request.method == "POST":
        form = UpdatePasswordForm(request.form) # get form
        if form.validate():
            user = user_model.validate_oldpassword(me.get("username"), form.password.data)
            if user:
                if form.password.data!=form.new_password.data:

                    user_model.update_password(me.get("id"), form.new_password.data)
                    session["me"] = user
                    flash("Password Updated successfully", "success")
                    return redirect(url_for("web.changepassword", me=me))
                else:
                    flash("new password can not be the same as old password", "danger")
                    return render_template("frontend/changepassword.html", me=me, form=form)
            else:
                flash("Invalid old password", "danger")
        else:
            #messages=form.errors
            #categorys = ["password", "new_password", "confirm_password"]
            #print (form.errors)
            #if messages:
                #for category, message in messages:
                    #if category:
                       #flash(message, "danger")
                    #else:
                        #flash("something wrong, please try again")
            #return redirect(url_for("web.changepassword"))  # redirect path
    #else:
        #return render_template("frontend/changepassword.html", me=me, form=form)

            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'password':
                       flash(error, 'password_error')
                    elif field == 'new_password':
                       flash(error, 'new_password_error')
                    elif field == 'confirm_password':
                       flash(error, 'confirm_password_error')
    return render_template("frontend/changepassword.html", me=me, form=form)


@web.route("/logout")
def logout():
    me = session.get("me") or {}
    if me:
        session.pop("me", None)
        flash("You have been signed out.", "success")
        if me.get("role") in ["staff", "local_manager", "national_manager", "admin"]:
            # TO DO: Here redirect to admin_home:
            return redirect(url_for("web.home"))
    return redirect(url_for("web.home"))