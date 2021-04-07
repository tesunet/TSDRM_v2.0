from django.test import TestCase
import sys,os
import django
from drm.workflow.workflow import *
sys.path.append(os.path.dirname(__file__) + os.sep + '../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TSDRM.settings')
django.setup()
# Create your tests here.
testJob = Job('eef392ec-8ada-11eb-9d49-a4bb6d10e0ef')
testJob.run_job()

