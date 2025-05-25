from rest_framework import serializers
from . import models

"""
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Client
        fields = ('id','email','name','interestlevel',''address','useremail','created','updated')
"""

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Patient
        fields = ('address', 'contact',)
        #'user','username', 'first_name', 'last_name', 'email')

