# Product Catalog

A small Django project that models **products**, **categories**, and **tags**, and
serves a single page where you can search products by description and filter them
by category and tags. Search and filters can be combined.

![Catalog overview](docs/screenshots/catalog-overview.png)

## Requirements

- **Python 3.12+** (required by Django 6.0)
- Django 6.0.6 (installed via `requirements.txt`)
- SQLite — bundled with Python, no database server to install

## Setup and run

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd django-product-catalog

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the database schema
python manage.py migrate

# 5. Load the sample data (5 categories, 10 tags, 30 products)
python manage.py loaddata sample_data

# 6. (Optional) Create an admin account to browse/edit data in the admin
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

Then open:

- Catalog page: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

> The `db.sqlite3` file is intentionally gitignored, so a fresh clone starts with
> an empty database. Step 4 (`migrate`) creates the schema and step 5
> (`loaddata`) populates the sample data — don't skip them or the catalog page
> will be empty.

## Features

The catalog page (`/`) lets a user:

- **Search by description** — case-insensitive substring match.
- **Filter by category** — single category dropdown.
- **Filter by tags** — multi-select checkboxes; a product matches if it has _any_
  of the selected tags.
- **Combine** search + category + tags in one request.
- **Paginate** results, with a selectable page size (25 / 50 / 100, default 25).
  The active search and filters are preserved as you page through results.

Example below: searching `Web`, category `Electronics`, and tag `Compact`
together narrow 30 products down to one.

![Combined search and filter](docs/screenshots/catalog-combined-filter.png)

## Data model

```mermaid
erDiagram
    CATEGORY ||--o{ PRODUCT : "categorizes"
    PRODUCT }o--o{ TAG : "tagged with"

    CATEGORY {
        bigint id PK
        string name UK
    }
    PRODUCT {
        bigint id PK
        string name
        text description
        bigint category_id FK
    }
    TAG {
        bigint id PK
        string name UK
    }
```

- **Category → Product**: one-to-many (`Product.category`, FK). Each product
  belongs to exactly one category.
- **Product and Tag**: many-to-many (`Product.tags`). A product can have zero or
  more tags, and a tag can apply to many products.

The query logic lives in `catalog/views.py`. It uses `select_related("category")`
and `prefetch_related("tags")` to avoid N+1 queries, and `.distinct()` on the
tag filter so a product isn't repeated when it matches multiple selected tags.

## Data population

The sample data was entered through the **Django admin** interface. The admin is
registered for all three models in `catalog/admin.py` (with list display, search,
and filters), so you can add or edit records yourself after creating a superuser.

For one-command reproducibility, the same dataset is also exported as a fixture at
`catalog/fixtures/sample_data.json` and loaded in step 5 above.

| Categories (5)                                                | Products (30)                                             | Tags (10)                                         |
| ------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------- |
| ![Categories in admin](docs/screenshots/admin-categories.png) | ![Products in admin](docs/screenshots/admin-products.png) | ![Tags in admin](docs/screenshots/admin-tags.png) |

## Running the tests

```bash
python manage.py test
```

The suite (`catalog/tests.py`) covers search, each filter, combined filtering,
pagination (default size, page-size options, out-of-range pages), URL routing,
and graceful handling of invalid query parameters.

## Configuration notes

`SECRET_KEY` is read from the `DJANGO_SECRET_KEY` environment variable and falls
back to a development-only key when it is not set:

```bash
export DJANGO_SECRET_KEY="your-production-secret"
```

`DEBUG = True` and the SQLite database are kept for a zero-config local setup;
both should be changed for any real deployment.

## Assumptions and notes

- **Search targets the product description** (case-insensitive substring), as
  specified in the brief. Product names are not searched.
- **Tag filtering uses OR semantics** — selecting multiple tags returns products
  that have _any_ of them. (AND semantics, requiring all selected tags, would be a
  one-line change if preferred.)
- **The catalog is served at `/`.** The earlier `/products/` URL still works and
  redirects to `/`.
- **SQLite** is used for simplicity; nothing in the app is SQLite-specific.
