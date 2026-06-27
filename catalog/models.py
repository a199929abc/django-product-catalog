"""Database models for the product catalog.

A Product belongs to exactly one Category and can carry any number of Tags.
"""

from django.db import models


class Category(models.Model):
    """A category that groups related products; each product belongs to one category."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """A reusable tag that can be assigned to multiple products."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """A product in the catalog. Each product belongs to one category and can have multiple tags."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="products",
        blank=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name