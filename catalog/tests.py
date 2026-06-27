from urllib.parse import parse_qs

from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Tag


class ProductListViewTests(TestCase):
    """Search, category/tag filtering, combining filters, and invalid-input handling."""

    @classmethod
    def setUpTestData(cls):
        cls.electronics = Category.objects.create(name="Electronics")
        cls.office_supplies = Category.objects.create(name="Office Supplies")

        cls.compact = Tag.objects.create(name="Compact")
        cls.wireless = Tag.objects.create(name="Wireless")
        cls.durable = Tag.objects.create(name="Durable")

        cls.mouse = Product.objects.create(
            name="Wireless Mouse",
            description="A compact wireless mouse designed for everyday laptop use.",
            category=cls.electronics,
        )
        cls.mouse.tags.add(cls.compact, cls.wireless)

        cls.keyboard = Product.objects.create(
            name="Mechanical Keyboard",
            description="A durable keyboard designed for long typing sessions.",
            category=cls.electronics,
        )
        cls.keyboard.tags.add(cls.durable)

        cls.notebook = Product.objects.create(
            name="Notebook Set",
            description="A compact notebook set for office notes and planning.",
            category=cls.office_supplies,
        )
        cls.notebook.tags.add(cls.compact)

    def test_root_url_serves_product_list(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")

    def test_products_url_redirects_to_root(self):
        response = self.client.get("/products/")

        self.assertRedirects(response, "/")

    def test_product_list_displays_all_products_by_default(self):
        response = self.client.get(reverse("product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
        self.assertContains(response, "Mechanical Keyboard")
        self.assertContains(response, "Notebook Set")

    def test_search_products_by_description(self):
        response = self.client.get(reverse("product_list"), {"q": "wireless"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
        self.assertNotContains(response, "Mechanical Keyboard")
        self.assertNotContains(response, "Notebook Set")

    def test_search_is_case_insensitive(self):
        response = self.client.get(reverse("product_list"), {"q": "WIRELESS"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
        self.assertNotContains(response, "Mechanical Keyboard")

    def test_blank_search_does_not_filter_products(self):
        response = self.client.get(reverse("product_list"), {"q": "   "})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
        self.assertContains(response, "Mechanical Keyboard")
        self.assertContains(response, "Notebook Set")

    def test_filter_products_by_category(self):
        response = self.client.get(
            reverse("product_list"),
            {"category": str(self.electronics.id)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
        self.assertContains(response, "Mechanical Keyboard")
        self.assertNotContains(response, "Notebook Set")

    def test_filter_products_by_tag(self):
        response = self.client.get(
            reverse("product_list"),
            {"tags": [str(self.compact.id)]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
        self.assertContains(response, "Notebook Set")
        self.assertNotContains(response, "Mechanical Keyboard")

    def test_multiple_tag_filters_match_any_selected_tag(self):
        response = self.client.get(
            reverse("product_list"),
            {"tags": [str(self.compact.id), str(self.durable.id)]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
        self.assertContains(response, "Mechanical Keyboard")
        self.assertContains(response, "Notebook Set")

    def test_combined_search_category_and_tag_filters(self):
        response = self.client.get(
            reverse("product_list"),
            {
                "q": "wireless",
                "category": str(self.electronics.id),
                "tags": [str(self.compact.id)],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
        self.assertNotContains(response, "Mechanical Keyboard")
        self.assertNotContains(response, "Notebook Set")

    def test_no_matching_products_shows_empty_state(self):
        response = self.client.get(reverse("product_list"), {"q": "nonexistent"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products found")
        self.assertNotContains(response, "Wireless Mouse")
        self.assertNotContains(response, "Mechanical Keyboard")
        self.assertNotContains(response, "Notebook Set")

    def test_invalid_filter_parameters_do_not_crash_page(self):
        response = self.client.get(
            reverse("product_list"),
            {
                "category": "invalid-category",
                "tags": ["invalid-tag"],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wireless Mouse")
        self.assertContains(response, "Mechanical Keyboard")
        self.assertContains(response, "Notebook Set")


class ProductListPaginationTests(TestCase):
    """Pagination behavior: default size, 50/100 page-size options, and out-of-range pages."""

    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Bulk")
        for index in range(60):
            Product.objects.create(
                name=f"Product {index:02d}",
                description=f"Sample product number {index} for pagination.",
                category=category,
            )

    def test_default_page_size_is_25(self):
        response = self.client.get(reverse("product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 25)

    def test_last_page_returns_remaining_products(self):
        response = self.client.get(reverse("product_list"), {"page": 3})

        # 60 products at 25 per page -> page 3 holds the remaining 10.
        self.assertEqual(len(response.context["page_obj"]), 10)
        self.assertEqual(response.context["page_obj"].number, 3)

    def test_per_page_can_be_increased_to_50(self):
        response = self.client.get(reverse("product_list"), {"per_page": 50})

        self.assertEqual(len(response.context["page_obj"]), 50)

    def test_per_page_can_be_increased_to_100(self):
        response = self.client.get(reverse("product_list"), {"per_page": 100})

        # Only 60 products exist, so all fit on a single 100-item page.
        self.assertEqual(len(response.context["page_obj"]), 60)

    def test_invalid_per_page_falls_back_to_default(self):
        response = self.client.get(reverse("product_list"), {"per_page": "999"})

        self.assertEqual(len(response.context["page_obj"]), 25)
        self.assertEqual(response.context["selected_per_page"], 25)

    def test_out_of_range_page_returns_last_page(self):
        response = self.client.get(reverse("product_list"), {"page": 999})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 3)

    def test_pagination_preserves_filters_and_drops_page(self):
        response = self.client.get(
            reverse("product_list"),
            {"per_page": 50, "q": "number"},
        )

        params = parse_qs(response.context["base_query"])
        self.assertEqual(params["per_page"], ["50"])
        self.assertEqual(params["q"], ["number"])
        self.assertNotIn("page", params)