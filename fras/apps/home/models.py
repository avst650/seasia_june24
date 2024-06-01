from django.db import models

class registration(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=191)
    department = models.CharField(max_length=191)
    date_time = models.DateTimeField(auto_now_add=True)
    image = models.BinaryField(null=True)
    class Meta:
        db_table = 'registration'
        
class attendance(models.Model):
    emp_id = models.ForeignKey(registration, on_delete=models.CASCADE)
    status = models.CharField(max_length=191)
    date_time = models.DateTimeField(auto_now=True)
    image = models.BinaryField(null=True)
    class Meta:
        db_table = 'attendance'
               
class unknown(models.Model):
    status = models.CharField(max_length=191)
    date_time = models.DateTimeField(auto_now=True)
    image = models.BinaryField(null=True)
    class Meta:
        db_table = 'unknown'
        
        
        
class rejected_unknown(models.Model):
    status = models.CharField(max_length=191)
    date_time = models.DateTimeField()
    image = models.BinaryField(null=True)
    class Meta:
        db_table = 'rejected_unknown'