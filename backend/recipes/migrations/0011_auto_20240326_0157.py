# Generated by Django 3.2.16 on 2024-03-25 18:57

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20240325_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Убедитесь, что это значение больше либо равно 1.')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_list', to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]
