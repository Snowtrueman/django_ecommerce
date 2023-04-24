from django.urls import path
from .views import *

urlpatterns = [
    path("", Index.as_view(), name="main"),
    path("products/category/<slug:category_slug>", Products.as_view(), name="products"),
    path("products/category/<slug:category_slug>/<int:product_id>", Product.as_view(), name="product"),
    path("products/special/", Special.as_view(), name="special"),
]
