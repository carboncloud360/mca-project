from rest_framework import routers
from hms import api_views as hire_viewed

routerep = routers.DefaultRouter()
routerep.register(r'patient', hire_viewed.PatientViewset)
