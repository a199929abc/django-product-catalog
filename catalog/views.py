from django.shortcuts import render

from .models import Category, Product, Tag


def product_list(request):
    search_query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "")
    raw_tag_ids = request.GET.getlist("tags")

    selected_category = category_id if category_id.isdigit() else ""
    selected_tag_ids = [tag_id for tag_id in raw_tag_ids if tag_id.isdigit()]

    products = Product.objects.select_related("category").prefetch_related("tags")

    if search_query:
        products = products.filter(description__icontains=search_query)

    if selected_category:
        products = products.filter(category_id=selected_category)

    if selected_tag_ids:
        products = products.filter(tags__id__in=selected_tag_ids).distinct()

    context = {
        "products": products,
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
        "search_query": search_query,
        "selected_category": selected_category,
        "selected_tag_ids": selected_tag_ids,
    }

    return render(request, "catalog/product_list.html", context)