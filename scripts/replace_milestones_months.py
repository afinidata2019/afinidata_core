from milestones.models import Milestone
from core.settings import BASE_DIR
from openpyxl import load_workbook
import os


def run():
    # file uri
    file_url = os.path.join(BASE_DIR, 'completion.xlsx')
    # get workbook
    wb = load_workbook(filename=file_url)
    # get worksheet
    ws = wb['Sheet1']

    for i, row in enumerate(ws.rows, start=1):

        if 0 < i:
            ms = Milestone.objects.filter(code=row[0].value)
            if ms.exists():
                m = ms.first()
                m.value = row[2].value
                m.save()
                print(m.pk, m.code, m.value)
