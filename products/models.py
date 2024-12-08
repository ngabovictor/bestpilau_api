from django.db import models

from utils.fields import JSONSchemaField
from utils.models import BaseModel
from auditlog.registry import auditlog


class ProductCategory(BaseModel):
    outlet = models.ForeignKey('outlets.Outlet', related_name='product_categories', on_delete=models.PROTECT)
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.ImageField(upload_to='product_category_images', null=True, blank=True)
    caption = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey('self', related_name='category', on_delete=models.SET_NULL,
                               null=True, blank=True)
    vendor = models.UUIDField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name
    
auditlog.register(ProductCategory)

OPTIONS_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["option_name", "selection_type", "is_required", "options"],
            "properties": {
                "option_name": {"type": "string"},
                "selection_type": {
                    "type": "string",
                    "enum": ["SINGLE", "MULTIPLE"]
                },
                "is_required": {"type": "boolean"},
                "options": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["option", "additional_price"],
                        "properties": {
                            "option": {"type": "string"},
                            "additional_price": {"type": "number"}
                        }
                    }
                }
            }
        }
    }

INGREDIENTS_SCHEMA = {
        "type": "array",
        "items": {
            "type": "string"
        }
    }

class Product(BaseModel):
    outlet = models.ForeignKey('outlets.Outlet', related_name='products', on_delete=models.PROTECT)
    name = models.CharField(max_length=255, null=False, blank=False)
    caption = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    category = models.ForeignKey(ProductCategory, related_name='product_category',
                                 on_delete=models.PROTECT)
    description = models.TextField()
    

    ingredients = JSONSchemaField(
        schema=INGREDIENTS_SCHEMA,
        default=list,
        blank=True,
        null=True
    )
    price = models.DecimalField(decimal_places=2, max_digits=20)  # INITIAL PRICE
    is_available = models.BooleanField(default=True)
    processing_time = models.PositiveIntegerField(null=True, blank=True,
                                                  help_text='duration minutes')

    options = JSONSchemaField(
        schema=OPTIONS_SCHEMA,
        default=list,
        blank=True,
        null=True
    )

    """
    [
        {
            "option_name":"Add drinks",
            "selection_type":"SINGLE" or "MULTIPLE", 
            "is_required": true,
            "options":[
                {
                    "option":"Fanta",
                    "additional_price":0
                }
            ]
        },
    ]
    """

    def __str__(self):
        return self.name

auditlog.register(Product)
