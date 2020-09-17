from milestones.models import Milestone
from core.settings import BASE_DIR
from openpyxl import load_workbook
import os


def run():
    # file uri
    file_url = os.path.join(BASE_DIR, 'mapping.xlsx')
    # get workbook
    wb = load_workbook(filename=file_url)
    # get worksheet
    ws = wb['Sheet1']

    for i, row in enumerate(ws.rows, start=1):

        if 0 < i < 119:
            code = row[0].value
            lf = row[1].value[2:]
            up = True
            if i > 109:
                up = False
                lf = row[1].value[4:]

            ms = Milestone.objects.filter(code=code)
            if ms.exists():
                m = ms.first()
                if not up:
                    lf = int(lf) * -1

                m.secondary_value = lf
                m.second_code = row[1].value
                m.save()
                print(m.pk, m.second_value, m.second_code)
