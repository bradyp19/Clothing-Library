# Generated by Django 4.2.19 on 2025-03-01 00:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("closet", "0002_patron_librarian"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="patron",
            name="patron",
        ),
        migrations.DeleteModel(
            name="Librarian",
        ),
        migrations.DeleteModel(
            name="Patron",
        ),
    ]
