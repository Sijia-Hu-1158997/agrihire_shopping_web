import os

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_paginate import Pagination, get_page_parameter, get_page_args
from app.decorators.auth import auth_required
from app.forms.user_form import UpdateUserInfoForm, RegisterForm, AdminRegisterForm
from app.models.user import UserModel
from app.models.store import StoreModel
from app.models.type import TypeModel
from app.models.category import CategoryModel
from app.forms.inventory_form import AddInventoryForm, AddEquipmentForm
from app.models.inventory import InventoryModel
from app.models.equipment import EquipmentModel
from app.models.service import ServiceModel
from . import web
from datetime import datetime, timezone, date, timedelta


@web.route("/service_list", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager','national_manager','admin'])
def service_list():
    me = session.get("me") or {}
    query = request.args.get("query")
    search = False
    if query:
        search = True
    page = request.args.get('page', type=int, default=1)
    per_page = 6
    offset = (page - 1) * per_page
    services = ServiceModel().get_service(query=query)
    services_for_render = services[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(services), per_page=per_page, search=search, record_name='services')

    return render_template("cms/admin_service.html", me=me, services = services_for_render, pagination=pagination)


@web.route("/service/<service_id>/check_history", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager','national_manager','admin'])
def view_service_history(service_id):
    me = session.get("me") or {}
    today_date = date.today()
    services = ServiceModel().get_service_by_id(service_id)
    query = request.args.get("query")
    search = False
    if query:
        search = True
    page = request.args.get('page', type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    service_record = ServiceModel().get_all_service_by_service_id(service_id, query=query)
    service_record_for_render = service_record[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(service_record), per_page=per_page, search=search, record_name='Service Record')
        
    return render_template("cms/admin_service_history.html", me=me, services=services, service_record=service_record_for_render, service_id=service_id, pagination=pagination, today_date=today_date)


@web.route("/service/<service_id>/add_equipment", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def add_equipment_for_service(service_id):
    me = session.get("me") or {}
    equipments = EquipmentModel().get_all_equipment()
    today_date = date.today()
    
    if request.method == "POST":
        service_end_str = request.form['service_end']
        service_end_date = datetime.strptime(service_end_str, '%Y-%m-%d').date()

        data = {
            'equipment_id': request.form['equipment_id'],
            'service_id': service_id,
            'service_end': service_end_str,
            'details': request.form['details'],
        }
        if service_end_date > today_date:
            print("service_end_date 2", service_end_date)
            ServiceModel().add_service_record(data)
            # change equipment status
            equipment_id = int(request.form['equipment_id'])
            data_equipment = {'status': 'repairing'}
            EquipmentModel().update_equipment(equipment_id, data_equipment)
            flash("Add equipment for service successfully!", "success")
            return redirect(url_for("web.view_service_history", service_id=service_id, today_date=today_date))
        else:
            flash("Service end date must not prior to the start date!", "danger")
        return redirect(url_for("web.view_service_history", service_id=service_id, today_date=today_date))
    
    return render_template("cms/admin_service_add_equipment.html", me=me, equipments=equipments, service_id=service_id, today_date=today_date)




@web.route("/service/<equipment_id>/view_history", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def view_equipment_service_history(equipment_id):
    me = session.get("me") or {}
    equipment = EquipmentModel().get_equipment_by_id(equipment_id)
    today_date = date.today()
    
    query = request.args.get("query")
    search = False
    if query:
        search = True
    page = request.args.get('page', type=int, default=1)
    per_page = 6
    offset = (page - 1) * per_page
    service_record = ServiceModel().get_service_record_by_equipment_id(equipment_id, query=query)
    service_record_for_render = service_record[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(service_record), per_page=per_page, search=search, record_name='Service Record')
    
    return render_template("cms/admin_service_equipment_history.html", me=me, equipment=equipment, service_record=service_record_for_render, equipment_id=equipment_id, pagination=pagination, today_date=today_date)


@web.route("/service/<equipment_id>/add_equipment_for_service", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def add_equipment_for_service_based_on_equipment(equipment_id):
    me = session.get("me") or {}
    equipment = EquipmentModel().get_equipment_by_id(equipment_id)
    services = ServiceModel().get_service()
    
    if request.method == 'POST':
        data = {
            'equipment_id': equipment_id,
            'service_id': request.form['service_id'],
            'service_end': request.form['service_end'],
            'details': request.form['details'],
        }
        service_end_str = request.form['service_end']
        service_end_date = datetime.strptime(service_end_str, '%Y-%m-%d').date()
        if service_end_date > date.today():
            ServiceModel().add_service_record(data)
            flash("Add equipment for service successfully!", "success")
            return redirect(url_for("web.view_equipment_service_history", equipment_id=equipment_id))
        else:
            flash("Service end date must not prior to the start date!", "danger")

    return render_template("cms/admin_service_add_service_for_equipment.html", me=me, equipment=equipment, services=services, equipment_id=equipment_id)


@web.route("/service/<service_record_id>/update_service_record", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def update_service_record(service_record_id):
    me = session.get("me") or {}
    service_record = ServiceModel().get_service_record_by_field('id', service_record_id)
    equipment_id = service_record.get("equipment_id")
    equipment = EquipmentModel().get_equipment_by_id(equipment_id)
    services = ServiceModel().get_service()
    
    if request.method == 'POST':
        data = {
            'equipment_id': equipment_id,
            'service_id': request.form['service_id'],
            'service_end': request.form['service_end'],
            'details': request.form['details'],
        }
        # check if service date is later than start date:
        service_end_str = request.form['service_end']
        service_end_date = datetime.strptime(service_end_str, '%Y-%m-%d').date()
        if service_end_date > service_record.get("service_start").date():
            ServiceModel().update_service_record(service_record_id, data)
            flash("Update this service record successfully!", "success")
            return redirect(url_for("web.view_equipment_service_history", equipment_id=equipment_id))
        else:
            flash("Service end date must not prior to the start date!", "danger")

    return render_template("cms/admin_service_update_record.html", me=me, equipment=equipment, services=services, service_record=service_record, equipment_id=equipment_id, service_record_id=service_record_id)




@web.route("/delete/<service_record_id>/service_record", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager','national_manager','admin'])
def delete_service_record(service_record_id):
    me = session.get("me") or {}
    service_record = ServiceModel().get_service_record_by_field('id', service_record_id)
    if service_record:
        equipment_id = service_record.get("equipment_id")
        is_deleted = service_record.get("is_deleted")
        service_end = service_record.get("service_end")

        if not is_deleted:
            # if service han't finish, which means service_end is larger than today, delete record means its status will be back to active
            if service_end and service_end > datetime.now().date():
                status_data = {'status': 'active'}
                EquipmentModel().update_equipment(equipment_id, status_data)
                ServiceModel().update_service_record(service_record_id, {"is_deleted": True})

            flash("Deleted successfully", "success")
        return redirect(url_for("web.view_equipment_service_history", equipment_id=equipment_id))
    
    return redirect(url_for("web.equipment_list"))


