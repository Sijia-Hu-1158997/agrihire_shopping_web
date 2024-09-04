'''
Author: Maggiefyer 109766140@qq.com
Date: 2024-05-20 01:58:37
LastEditors: Maggiefyer 109766140@qq.com
LastEditTime: 2024-05-30 18:02:23
FilePath: \COMP639S1_Project_2_Group_I\app\web\__init__.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter

web = Blueprint("web", __name__, template_folder="templates")




from app.web import auth, backend_inventory, backend_user, frontend, backend, frontend_profile, backend_equipment, frontend_equipment, frontend_booking, frontend_news, backend_news, backend_category, backend_type, backend_payments, backend_service, backend_promotions, backend_schedule,frontend_message,backend_message,backend_report
