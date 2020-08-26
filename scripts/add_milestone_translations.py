from languages.models import MilestoneTranslation, Language
from milestones.models import Milestone
from core.settings import BASE_DIR
from openpyxl import load_workbook
import sys
import os


def run():
    if len(sys.argv) < 4:
        return None

    # get filename in command line
    filename = sys.argv[3]

    # get file
    file_url = os.path.join(BASE_DIR, filename)

    # get workbook
    wb = load_workbook(filename=file_url)

    # get worksheet
    ws = wb['list']

    # iterate in rows
    for data in ws.rows:
        ml = Milestone.objects.filter(code=data[0].value)
        if ml.exists():
            milestone = ml.last()
            print(milestone.pk, milestone)
            lang = Language.objects.get(name='en')
            n_mt = MilestoneTranslation.objects.create(milestone=milestone, language=lang, name=data[1].value,
                                                       description=data[1].value)
            print(n_mt.pk, n_mt.name, n_mt.description)
