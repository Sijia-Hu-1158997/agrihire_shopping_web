'''
Author: Maggiefyer 109766140@qq.com
Date: 2024-06-12 13:13:23
LastEditors: Maggiefyer 109766140@qq.com
LastEditTime: 2024-06-12 13:15:06
FilePath: \COMP639S1_Project_2_Group_I\app\secure.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

# These details are available on the first MySQL Workbench screen
# Usually called 'Local Instance'

# For local instance
# # docker run --name spb -e MYSQL_ROOT_PASSWORD=secret001 -p 13306:3306 -d mysql
dbuser = "root"  # Your MySQL username - likely 'root'
dbpass = "16540789+"  # ---- PUT YOUR PASSWORD HERE ----
dbhost = "localhost"
dbport = "3306"  # update this to 3306 if  3306 port is available
dbname = "agrihire"

# For pythonanywhere - production
# dbhost = "Agrihire.mysql.pythonanywhere-services.com"
# dbport = "3306"
# dbname = "Agrihire$agri_hire_new"


# common configuration
WTF_CSRF_CHECK_DEFAULT = False
