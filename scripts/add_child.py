from messenger_users.models import User
from attributes.models import Attribute
from instances.models import Instance
from core.settings import BASE_DIR
import xlrd
import sys
import os


def run():
    if len(sys.argv) < 4 or len(sys.argv) > 4:
        return None

    filename = sys.argv[3]
    file_path = os.path.join(BASE_DIR, filename)
    attribute = Attribute.objects.get(name='birthday')

    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)
    index = 1
    for i in range(sheet.nrows):
        try:
            #print(sheet.row_values(i))
            u = User.objects.get(id=sheet.row_values(i)[0])
            if u:
                children = u.get_instances().filter(entity_id=1)
                if children.count() < 1:
                    ins = Instance.objects.create(entity_id=1, name=sheet.row_values(i)[1])
                    assoc = ins.instanceassociationuser_set.create(user_id=u.pk)
                    attr_v = ins.attributevalue_set.create(attribute=attribute, value=sheet.row_values(i)[2])
                    print(ins.pk, ins, assoc, attr_v)

        except Exception as e:
            print(e)
            pass