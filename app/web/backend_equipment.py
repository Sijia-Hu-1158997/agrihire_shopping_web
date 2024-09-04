import os

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_paginate import Pagination, get_page_parameter, get_page_args
from app.decorators.auth import auth_required
from app.forms.user_form import UpdateUserInfoForm, RegisterForm, AdminRegisterForm
from app.models.user import UserModel
from app.models.store import StoreModel
from app.models.type import TypeModel
from app.models.category import CategoryModel
from app.forms.inventory_form import AddEquipmentForm
from app.models.inventory import InventoryModel
from app.models.equipment import EquipmentModel
from app.models.service import ServiceModel
from app.models.booking_item import BookingItemModel
from . import web
from datetime import datetime, timezone, date, timedelta


@web.route("/equipment_list", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def equipment_list():
    me = session.get("me") or {}
    query = request.args.get("query")
    search = False
    if query:
        search = True
    page = request.args.get('page', type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    equipments = EquipmentModel().get_all_equipment(query=query)
    equipments_for_render = equipments[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(equipments), per_page=per_page, search=search, record_name='equipments')

    return render_template("cms/admin_equipment.html", me=me, equipments=equipments_for_render, pagination=pagination)


@web.route("/update/<id>/equipment", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def update_equipment_details(id):
    me = session.get("me") or {}
    equipments = EquipmentModel().get_equipment_by_field('id', id)
    equipment_is_delete = equipments.get("is_deleted")
    if not equipments:
        flash("No equipment found with the specified ID", "danger")
        return redirect(url_for("web.equipment_list"))
    
    inventory_id = equipments.get("inventory_id")
    inventory = InventoryModel().get_inventory_by_id(inventory_id)
    if not inventory:
        flash("No inventory found for the specified equipment", "danger")
        return redirect(url_for("web.equipment_list"))
    
    quantity_of_inventory = int(inventory.get("quantity"))

    # Check if equipment has finished repairing
    equipment_status = equipments.get("status")
    if equipment_status == 'repairing':
        service_record = ServiceModel().get_latest_service_record_by_equipment_id(id)
        if service_record:
            service_end = service_record.get("service_end")
            if service_end and service_end < datetime.now().date():
                status_data = {'status': 'active'}
                EquipmentModel().update_equipment(id, status_data)

    if request.method == "GET":
        stores = StoreModel().get_all_stores()
        types = TypeModel().get_all_types()
        types_and_categories = TypeModel().get_types_and_categories()
        categories = CategoryModel().get_all_categories()
        inventories = InventoryModel().get_all_inventories()
        return render_template("cms/admin_equipment_update.html", me=me, equipments=equipments, id=id, stores=stores, types=types, categories=categories, types_and_categories=types_and_categories, inventories=inventories)

    if request.method == "POST":
        # image
        file_info = request.files['image_path']
        file_name = file_info.filename
        if file_name:
            folder_path = os.path.join(os.getcwd(), 'app/static/images/inventory', str(id))
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file_full_path = os.path.join(folder_path, file_name)
            file_info.save(file_full_path)
            file_path = os.path.join('static/images/inventory', str(id), file_name)
        else:
            file_path = ''

        data = {
            'name': request.form['name'],
            'status': request.form['status'],
            'details': request.form['details'],
            'image_path': file_path
        }
        EquipmentModel().update_equipment(id, data)
        data_status = request.form['status']
        
        if equipment_is_delete == False:
            # check if equipment is already in repairing or retired
            if data_status == 'repairing':
                if equipment_status == 'active':
                    quantity_of_inventory -= 1
                    InventoryModel().update_inventory(inventory_id, {"quantity": quantity_of_inventory})
                    flash("Equipment updated successfully! Please complete the service record!", "success")
                    return redirect(url_for("web.add_equipment_for_service_based_on_equipment", equipment_id=id))
                else:
                    flash("The equipment is in repairing or already retired!", "danger")
                    return redirect(url_for("web.see_equipments_in_inventory", id=inventory_id))
            elif data_status == 'retired':
                quantity_of_inventory -= 1
                InventoryModel().update_inventory(inventory_id, {"quantity": quantity_of_inventory})
                flash("Equipment retired successfully!", "success")
                return redirect(url_for("web.see_equipments_in_inventory", id=inventory_id))
            elif data_status == 'active' and equipment_status == 'repairing':
                finish_repairing = {
                    'service_end': datetime.now(),
                    'status': 'active'
                }
                ServiceModel().update_service_record(id, finish_repairing)
                quantity_of_inventory += 1
                InventoryModel().update_inventory(inventory_id, {"quantity": quantity_of_inventory})
                flash("Equipment updated successfully!", "success")
    return redirect(url_for("web.see_equipments_in_inventory", id=inventory_id))


@web.route("/delete/<id>/equipment", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def delete_equipment(id):
    me = session.get("me") or {}
    equipment = EquipmentModel().get_equipment_by_id(id)
    if not equipment:
        flash("No equipment found with the specified ID", "danger")
        return redirect(url_for("web.equipment_list"))

    inventory_id = equipment.get("inventory_id")
    inventory = InventoryModel().get_inventory_by_id(inventory_id)
    if not inventory:
        flash("No inventory found for the specified equipment", "danger")
        return redirect(url_for("web.equipment_list"))

    quantity_of_inventory = int(inventory.get("quantity"))

    booking_items = BookingItemModel().get_booking_items_by_equipment_id(id)
    if booking_items:
        hire_end = booking_items.get("hire_end")
        if hire_end:
            hire_end_date = hire_end.date()
        else:
            hire_end_date = None
    else:
        hire_end_date = None

    today_date = datetime.now().date()
    status = equipment.get("status")

    if equipment.get("is_deleted"):
        EquipmentModel().update_equipment(id, {"is_deleted": False})
        quantity_of_inventory += 1
        InventoryModel().update_inventory(inventory_id, {"quantity": quantity_of_inventory})
        flash("Restored successfully", "success")
    else:
        if quantity_of_inventory >= 1:
            if hire_end_date and hire_end_date > today_date or status == 'repairing':
                flash("The equipment is still hired out or in repairing, cannot be deleted!", "danger")
                return redirect(url_for("web.see_equipments_in_inventory", id=inventory_id))
            else:
                quantity_of_inventory -= 1
                InventoryModel().update_inventory(inventory_id, {"quantity": quantity_of_inventory})
                EquipmentModel().update_equipment(id, {"is_deleted": True})
                flash("Deleted successfully", "success")
        else:
            flash("There is nothing in this inventory to be deleted!", "danger")
    return redirect(url_for("web.see_equipments_in_inventory", id=inventory_id))


@web.route("/hire/<id>/record", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def hire_equipment_record(id):
    me = session.get("me") or {}
    equipment = EquipmentModel().get_equipment_by_id(id)
    if not equipment:
        flash("No equipment found with the specified ID", "danger")
        return redirect(url_for("web.equipment_list"))

    booking_record = BookingItemModel().get_booking_items_by_equipment_id(id)
    print("booking_record", booking_record)

    return render_template("cms/admin_equipment_hire_record.html", me=me, equipment=equipment, booking_record=booking_record, id=id)
