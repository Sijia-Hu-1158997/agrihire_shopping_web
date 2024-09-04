import os

from flask import current_app, flash, redirect, render_template, request, session, url_for
from app.decorators.auth import auth_required
from app.models.user import UserModel
from app.models.equipment import EquipmentModel
from . import web

@web.route("/equipments", methods=["GET", "POST"])
# @auth_required(roles=["member", "instructor", "manager"])
def equipments():
    me = session.get("me") or {}
    equipment_model = EquipmentModel()
    equipments = equipment_model.get_all_equipment()
    return render_template(
        "frontend/equipments.html", me=me, equipments=equipments
    )


@web.route("/equipment_detail/<equipment_id>/")
# @auth_required(roles=["member", "instructor", "manager"])
def equipment_detail(equipment_id):
    me = session.get("me") or {}

    equipment_model = EquipmentModel()
    target = equipment_model.get_equipment_by_id(equipment_id)
    
    return render_template(
        "frontend/equipment_detail.html",
        me=me,
        target=target
    )



