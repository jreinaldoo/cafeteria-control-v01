from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.services.recipe_service import (
    create_recipe,
    add_recipe_item,
    update_recipe,
    update_recipe_item,
    delete_recipe,
    delete_recipe_item,
    get_all_recipes,
    get_recipe,
    get_all_products,
)

recipes_bp = Blueprint("recipes", __name__)


@recipes_bp.get("/")
def index():
    """Lista todas as receitas"""
    recipes = get_all_recipes()
    return render_template("recipes/index.html", recipes=recipes)


@recipes_bp.get("/new")
def new():
    """Formulário para criar nova receita"""
    products = get_all_products()
    return render_template("recipes/form.html", products=products, recipe=None)


@recipes_bp.post("/create")
def create():
    """Cria uma nova receita"""
    name = request.form.get("name")
    description = request.form.get("description")

    if not name:
        flash("Nome da receita é obrigatório", "error")
        return redirect(url_for("recipes.new"))

    recipe = create_recipe(name, description)
    flash("Receita criada com sucesso!", "success")
    return redirect(url_for("recipes.edit", recipe_id=recipe.id))


@recipes_bp.get("/<int:recipe_id>/edit")
def edit(recipe_id):
    """Formulário para editar receita"""
    recipe = get_recipe(recipe_id)
    if not recipe:
        flash("Receita não encontrada", "error")
        return redirect(url_for("recipes.index"))

    products = get_all_products()
    return render_template("recipes/form.html", recipe=recipe, products=products)


@recipes_bp.post("/<int:recipe_id>/update")
def update(recipe_id):
    """Atualiza uma receita"""
    name = request.form.get("name")
    description = request.form.get("description")

    if not name:
        flash("Nome da receita é obrigatório", "error")
        return redirect(url_for("recipes.edit", recipe_id=recipe_id))

    update_recipe(recipe_id, name, description)
    flash("Receita atualizada com sucesso!", "success")
    return redirect(url_for("recipes.edit", recipe_id=recipe_id))


@recipes_bp.post("/<int:recipe_id>/items/add")
def add_item(recipe_id):
    """Adiciona um item à receita"""
    product_id = request.form.get("product_id")
    quantity_used = request.form.get("quantity_used")

    if not product_id or not quantity_used:
        flash("Produto e quantidade são obrigatórios", "error")
        return redirect(url_for("recipes.edit", recipe_id=recipe_id))

    try:
        add_recipe_item(recipe_id, int(product_id), quantity_used)
        flash("Item adicionado com sucesso!", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("recipes.edit", recipe_id=recipe_id))


@recipes_bp.post("/items/<int:item_id>/update")
def update_item(item_id):
    """Atualiza um item da receita"""
    product_id = request.form.get("product_id")
    quantity_used = request.form.get("quantity_used")
    recipe_id = request.form.get("recipe_id")

    if not product_id or not quantity_used:
        flash("Produto e quantidade são obrigatórios", "error")
        return redirect(url_for("recipes.edit", recipe_id=recipe_id))

    try:
        update_recipe_item(item_id, int(product_id), quantity_used)
        flash("Item atualizado com sucesso!", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("recipes.edit", recipe_id=recipe_id))


@recipes_bp.post("/items/<int:item_id>/delete")
def delete_item_route(item_id):
    """Remove um item da receita"""
    item = get_recipe(int(request.form.get("recipe_id")))
    if item:
        recipe_id = item.id
    else:
        flash("Receita não encontrada", "error")
        return redirect(url_for("recipes.index"))

    try:
        delete_recipe_item(item_id)
        flash("Item removido com sucesso!", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("recipes.edit", recipe_id=recipe_id))


@recipes_bp.post("/<int:recipe_id>/delete")
def delete_recipe_route(recipe_id):
    """Remove uma receita"""
    try:
        delete_recipe(recipe_id)
        flash("Receita removida com sucesso!", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("recipes.index"))
