from messenger_users.models import User
from core.settings import BASE_DIR
import xlrd
import sys
import os


def run():
    if len(sys.argv) < 4 or len(sys.argv) > 4:
        return None

    filename = sys.argv[3]
    file_path = os.path.join(BASE_DIR, filename)

    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)
    index = 1
    for i in range(sheet.nrows):
        try:
            u = User.objects.get(id=sheet.row_values(i)[1])
            if u:
                if sheet.row_values(i)[2]:
                    u.userdata_set.create(data_key='user_reg', data_value=sheet.row_values(i)[2])

                if sheet.row_values(i)[3]:
                    u.userdata_set.create(data_key='user_locale', data_value=sheet.row_values(i)[3])

                if sheet.row_values(i)[4]:
                    u.userdata_set.create(data_key='tipo_de_licencia', data_value=sheet.row_values(i)[4])

                if sheet.row_values(i)[5]:
                    u.userdata_set.create(data_key='childtype', data_value=sheet.row_values(i)[5])

                if sheet.row_values(i)[6]:
                    u.userdata_set.create(data_key='user_rol',
                                          data_value=sheet.row_values(i)[6].encode('utf-8').decode('utf-8', 'ignore'))
                if sheet.row_values(i)[7]:
                    u.userdata_set.create(data_key='Premium', data_value=sheet.row_values(i)[7])

                if sheet.row_values(i)[8]:
                    u.userdata_set.create(data_key='childMonths', data_value=sheet.row_values(i)[8])

                if sheet.row_values(i)[9]:
                    u.userdata_set.create(data_key='user_type', data_value=sheet.row_values(i)[9])

                if sheet.row_values(i)[10]:
                    u.userdata_set.create(data_key='Pais', data_value=sheet.row_values(i)[10])

                if sheet.row_values(i)[11]:
                    u.userdata_set.create(data_key='Pais', data_value=sheet.row_values(i)[11])
            print(u)
        except Exception as e:
            print(e)
            pass
