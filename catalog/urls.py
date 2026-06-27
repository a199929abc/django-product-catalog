from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    # Keep the previous URL working by redirecting it to the canonical root page.
    path(
        "products/",
        RedirectView.as_view(pattern_name="product_list"),
        name="product_list_legacy",
    ),
]