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
from . import web


@web.route("/inventory_list", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager','national_manager','admin'])
def inventory_list():
    me = session.get("me") or {}
    query = request.args.get("query")
    search = False
    if query:
        search = True
    page = request.args.get('page', type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    inventories = InventoryModel().get_all_inventories(query=query)
    inventories_for_render = inventories[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(inventories), per_page=per_page, search=search, record_name='inventories')

    return render_template("cms/admin_inventory.html", me=me, inventories = inventories_for_render, pagination=pagination)


@web.route("/update/<id>/inventory", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager','national_manager','admin'])
def update_inventory(id):
    me = session.get("me") or {}
    inventories = InventoryModel().get_inventory_by_field('id', id)
    all_equipment = EquipmentModel().get_equipment_by_inventory_id(id)

    if request.method == "GET":
        stores = StoreModel().get_all_stores()
        types = TypeModel().get_all_types()
        types_and_categories = TypeModel().get_types_and_categories()
        categories = CategoryModel().get_all_categories()
        return render_template("cms/admin_inventory_update.html", me=me, inventories=inventories, id=id, stores=stores, types=types, categories=categories, types_and_categories=types_and_categories)

    if request.method == "POST":
        # image
        file_info = request.files['image']
        file_type = file_info.content_type
        file_name = file_info.filename
        if file_name:
            folder_path = os.path.join(os.getcwd(),'app/static/images/inventory',str(request.form['store_id']))
            # PA path:
            # folder_path = os.path.join(os.getcwd(),'/home/Agrihire/COMP639S1_Project_2_Group_I/app/static/images/inventory',str(request.form['store_id']))
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file_full_path = os.path.join(folder_path,file_name)
            file_info.save(file_full_path)
            file_path = os.path.join('static/images/inventory',str(request.form['store_id']),file_name)
        else:
            file_path = 'inventories.image'

        price = request.form['price']

        data = {
            'date_of_purchase': request.form['date_of_purchase'],
            'specifications': request.form['specifications'],
            'store_id': request.form['store_id'],
            'type_id': request.form['type_id'],
            'price': float(price) if price else None,
            'cost': request.form['cost'],
        }
        print("data", data)
        if file_name:
            data['image'] = file_path
        
        InventoryModel().update_inventory(id, data)
        type_id = request.form['type_id']
        store_id = request.form['store_id']
        for equipment in all_equipment:
            EquipmentModel().update_equipment(equipment['id'], {"type_id": type_id, "store_id": store_id})
        flash("Inventory Updated successfully!", "success")
        return redirect(url_for("web.inventory_list"))

    return render_template("cms/admin_inventory_update.html", me=me, inventories=inventories, id=id, stores=stores, types=types, categories=categories, types_and_categories=types_and_categories)



@web.route("/delete/<id>/inventory", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager','national_manager','admin'])
def delete_inventory(id):
    me = session.get("me") or {}
    inventories = InventoryModel().get_inventory_by_id(id)
    all_equipment = EquipmentModel().get_equipment_by_inventory_id(id)

    if inventories.get("is_deleted"):
        InventoryModel().update_inventory(id, {"is_deleted": False})
        for equipment in all_equipment:
            EquipmentModel().update_equipment(equipment['id'], {"is_deleted": False})
        flash("Restored inventory and its equipment successfully!", "success")
    else:
        InventoryModel().update_inventory(id, {"is_deleted": True})
        for equipment in all_equipment:
            EquipmentModel().update_equipment(equipment['id'], {"is_deleted": True})
        flash("Deleted inventory and its equipment successfully!", "success")
    
    return redirect(url_for("web.inventory_list"))


@web.route("/add_inventory", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def add_inventory():
    me = session.get("me") or {}
    stores = StoreModel().get_all_stores()
    types = TypeModel().get_all_types()
    types_and_categories = TypeModel().get_types_and_categories()
    categories = CategoryModel().get_all_categories()
    if request.method == "POST":
        form = AddInventoryForm()
        if form.validate():
            generate_inventory_serial_number = InventoryModel().generate_inventory_serial_number()
            # Image handling
            file_info = request.files['image']
            file_name = file_info.filename
            if file_name:
                # PA path:
                # folder_path = os.path.join(os.getcwd(),'/home/Agrihire/COMP639S1_Project_2_Group_I/app/static/images/inventory',str(request.form['store_id']))
                folder_path = os.path.join(os.getcwd(), 'app/static/images/inventory', str(request.form['store_id']))
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                file_full_path = os.path.join(folder_path, file_name)
                file_info.save(file_full_path)
                file_path = os.path.join('static/images/inventory', str(request.form['store_id']), file_name)
            else:
                file_path = ''
            
            name = request.form['name']

            # add inventory data
            inventory_data = {
                'inventory_serial_number': generate_inventory_serial_number,
                'date_of_purchase': request.form['date_of_purchase'],
                'specifications': request.form['specifications'],
                'store_id': request.form['store_id'],
                'type_id': request.form['type_id'],
                'quantity': request.form['quantity'],
                # 'price': request.form['price'],
                'cost': request.form['cost'],
                'image': file_path
            }
            InventoryModel().add_inventory(inventory_data)

            quantity = int(request.form['quantity'])
            equipment_serial_numbers = EquipmentModel().generate_equipment_serial_numbers_by_quantity(quantity)

            # get inventory_id and quantity of the newly added inventory
            inventory_id = InventoryModel().get_inventory_by_field('inventory_serial_number', generate_inventory_serial_number).get('id')
            cost = InventoryModel().get_inventory_by_field('inventory_serial_number', generate_inventory_serial_number).get('cost')

            equipment_ids = []

            # add equipment data
            for serial_number in equipment_serial_numbers:
                equipment_data = {
                    'equipment_serial_number': serial_number,
                    'name': name,
                    'type_id': request.form['type_id'],
                    'inventory_id': inventory_id,
                    'store_id': request.form['store_id'],
                    'cost': cost,
                    'status': 'active'
                }
                EquipmentModel().quick_add_equipment(equipment_data)
                equipment = EquipmentModel().get_equipment_by_field('equipment_serial_number', serial_number)
                equipment_ids.append(equipment['id'])

            flash("Inventory added successfully! Now please add all the equipments for the inventory.", "success")
            return redirect(url_for("web.update_equipment_for_inventory", inventory_id=inventory_id, equipment_serial_numbers=equipment_serial_numbers, equipment_ids=equipment_ids))
        else:
            print("form.errors", form.errors)
            flash(form.errors, "danger")
    return render_template("cms/admin_inventory_add.html", me=me, stores=stores, types=types, categories=categories, types_and_categories=types_and_categories)

@web.route("/add_equipment_details/for/<inventory_id>/inventory", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager', 'national_manager', 'admin'])
def update_equipment_for_inventory(inventory_id):
    me = session.get("me") or {}
    inventories = InventoryModel().get_inventory_by_id(inventory_id)
    equipments = EquipmentModel().get_equipment_by_inventory_id(inventory_id, query=None)
    equipment_ids = [equipment['id'] for equipment in equipments]
    stores = StoreModel().get_all_stores()

    if request.method == "GET":
        types = TypeModel().get_all_types()
        types_and_categories = TypeModel().get_types_and_categories()
        categories = CategoryModel().get_all_categories()
        return render_template("cms/admin_inventory_add_equipment.html", me=me, stores=stores, types=types, categories=categories, types_and_categories=types_and_categories, inventories=inventories, equipments=equipments, equipment_ids=equipment_ids, inventory_id=inventory_id)

    if request.method == "POST":
        for equipment_id in equipment_ids:
            print("equipment_id:", equipment_id)
            details = request.form.get(f'details_{equipment_id}')

            # Image handling
            file_info = request.files[f'image_path_{equipment_id}']
            file_name = file_info.filename
            if file_name:
                # PA path:
                # folder_path = os.path.join(os.getcwd(),'/home/Agrihire/COMP639S1_Project_2_Group_I/app/static/images/equipment',str(equipment_id))
                folder_path = os.path.join(os.getcwd(), 'app/static/images/equipment', str(equipment_id))
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                file_full_path = os.path.join(folder_path, file_name)
                file_info.save(file_full_path)
                file_path = os.path.join('static/images/equipment', str(equipment_id), file_name)
            else:
                file_path = ''
            
            if details is not None or file_path is not None:
                data = {}
                if details:
                    data['details'] = details
                if file_path:
                    data['image_path'] = file_path
                if data:
                    EquipmentModel().update_equipment(equipment_id, data)
        flash("Equipment Added successfully!", "success")
        return redirect(url_for("web.see_equipments_in_inventory", id=inventory_id))
    return render_template("cms/admin_inventory_add.html", me=me)


@web.route("/equipments/<id>/list", methods=["GET", "POST"])
@auth_required(roles=['staff', 'local_manager','national_manager','admin'])
def see_equipments_in_inventory(id):
    me = session.get("me") or {}
    query = request.args.get("query")
    search = False
    if query:
        search = True
    page = request.args.get('page', type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page
    equipments = EquipmentModel().get_equipment_by_inventory_id(id, query=None)
    # inventories = InventoryModel().get_all_inventories(query=query)
    equipments_for_render = equipments[offset:offset + per_page]
    pagination = Pagination(page=page, total=len(equipments), per_page=per_page, search=search, record_name='equipments')

    return render_template("cms/admin_inventory_equipment.html", me=me, equipments = equipments_for_render, pagination=pagination)
