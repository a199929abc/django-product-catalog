from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Category, Product, Tag

# Supported page sizes; the first value is the default.
PAGE_SIZES = (25, 50, 100)
DEFAULT_PAGE_SIZE = PAGE_SIZES[0]


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

    per_page_raw = request.GET.get("per_page", "")
    selected_per_page = (
        int(per_page_raw)
        if per_page_raw.isdigit() and int(per_page_raw) in PAGE_SIZES
        else DEFAULT_PAGE_SIZE
    )

    paginator = Paginator(products, selected_per_page)
    # get_page() coerces missing/non-integer/out-of-range values to a valid page.
    page_obj = paginator.get_page(request.GET.get("page"))

    # Keep the active search/filter/page-size params on pagination links,
    # dropping only "page" so each link points at its own page number.
    preserved_params = request.GET.copy()
    preserved_params.pop("page", None)
    base_query = preserved_params.urlencode()

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "base_query": base_query,
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
        "search_query": search_query,
        "selected_category": selected_category,
        "selected_tag_ids": selected_tag_ids,
        "page_sizes": PAGE_SIZES,
        "selected_per_page": selected_per_page,
    }

    return render(request, "catalog/product_list.html", context)