def get_shopping_list(ingredients):
    """Создать список покупок для передачи в файл."""
    shopping_dict = {}

    for ingredient in ingredients:
        name = ingredient["ingredient__name"]
        amount = ingredient["amount"]
        measurement_unit = ingredient["ingredient__measurement_unit"]

        if name not in shopping_dict:
            shopping_dict[name] = {
                "amount": amount,
                "measurement_unit": measurement_unit
            }
        else:
            shopping_dict[name]["amount"] += amount

    output_ingredients = "Cписок покупок:\n\n"

    for ingredient, data in shopping_dict.items():
        output_ingredients += (
            f"* {ingredient.capitalize()} "
            f"- {data['amount']} {data['measurement_unit']}\n"
        )

    return output_ingredients
