
## Installation

Run the [pip](https://pip.pypa.io/en/stable/) command to install the latest version:

```bash
   pip install git+https://github.com/sitmena/sitech-django-models.git@v1.0
```

## Usage
Given that you have the model
```python
class YourModel(models.Model):
    mai_field = models.CharField()
    other_field = models.BooleanField()
```        
<br/>  
        
**-Tracking Fields:** 
```python
from sitech_models import TrackingFieldsMixin

class YourModel(TrackingFieldsMixin, models.Model):
    mai_field = models.CharField()
    other_field = models.BooleanField()

obj = YourModel.objects.get(1)
```  
 - Call `get_old_field('field_name')` to access the old value.
 - Call `set_old_field('field_name', value)` to set the old value.

<br/>  

**- Soft Delete:** 
```python
from sitech_models import SoftDeleteMixin

class MyModel(SoftDeleteMixin, models.Model):
    mai_field = models.CharField()
    other_field = models.BooleanField()
    
obj = YourModel.objects.get(1)
```  

Add `SOFT_DELETE = True` to your `Settings` 
-  `obj.delete()`  "soft delete"
-  `YourModel.objects.filters().delete()`  "soft delete"
-  `YourModel.objects.filters().delete(force_delete=True)`  "force delete"
-  `obj.delete(force_delete=True)`  "force delete"

<br/>  

**- Model:**  You can use sitech_models.Model to exteneds all the above mixins
```python
from sitech_models import Model

class MyModel(Model):
    mai_field = models.CharField()
    other_field = models.BooleanField()
```     
