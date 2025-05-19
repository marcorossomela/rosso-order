from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.extensions import db
from src.models.supplier import Supplier
from src.models.product import Product

suppliers_bp = Blueprint('suppliers_bp', __name__)

@suppliers_bp.route('/suppliers-products', methods=['GET', 'POST'])
def manage_suppliers_products():
    if request.method == 'POST':
        # Aggiunta fornitore con prodotti base
        if 'email' in request.form and 'phone' in request.form:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()

            if name and email:
                existing = Supplier.query.filter_by(email=email).first()
                if existing:
                    flash('Fornitore già esistente con questa email.', 'warning')
                else:
                    supplier = Supplier(name=name, email=email, phone=phone)
                    db.session.add(supplier)
                    db.session.flush()

                    default_products = [
                        ('Pomodoro', 'Kg'),
                        ('Mozzarella', 'Kg'),
                        ('Farina', 'Bag'),
                        ('Olio', 'Each')
                    ]

                    for pname, unit in default_products:
                        product = Product(name=pname, unit=unit, supplier_id=supplier.id)
                        db.session.add(product)

                    db.session.commit()
                    flash('Fornitore e prodotti base aggiunti!', 'success')
            else:
                flash('Nome e email sono obbligatori per il fornitore.', 'danger')

        # Aggiunta prodotto
        elif 'supplier_id' in request.form:
            name = request.form.get('name', '').strip()
            unit = request.form.get('unit', '').strip()
            supplier_id = request.form.get('supplier_id')

            if name and unit and supplier_id:
                existing = Product.query.filter_by(name=name, unit=unit, supplier_id=supplier_id).first()
                if existing:
                    flash('Prodotto già esistente per questo fornitore.', 'warning')
                else:
                    db.session.add(Product(name=name, unit=unit, supplier_id=supplier_id))
                    db.session.commit()
                    flash('Prodotto aggiunto con successo!', 'success')
            else:
                flash('Tutti i campi sono obbligatori per aggiungere un prodotto.', 'danger')

        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    suppliers = Supplier.query.all()
    return render_template('suppliers.html', suppliers=suppliers)

@suppliers_bp.route('/edit/<supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)

    if request.method == 'POST':
        supplier.name = request.form.get('name', '').strip()
        supplier.email = request.form.get('email', '').strip()
        supplier.phone = request.form.get('phone', '').strip()
        db.session.commit()
        flash('Fornitore aggiornato con successo!', 'success')
        return redirect(url_for('suppliers_bp.manage_suppliers_products'))

    return render_template('edit_supplier.html', supplier=supplier)


---

2. edit_supplier.html

{% extends "base.html" %}
{% block title %}Modifica Fornitore{% endblock %}

{% block content %}
<style>
  .form-container {
    background: white;
    padding: 25px;
    margin: 40px auto;
    width: 90%;
    max-width: 600px;
    border-radius: 10px;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
  }

  input, button {
    display: block;
    width: 100%;
    padding: 10px;
    margin-top: 10px;
    margin-bottom: 20px;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 6px;
  }

  button {
    background-color: #1f7aec;
    color: white;
    font-weight: bold;
    border: none;
    cursor: pointer;
  }

  button:hover {
    background-color: #135cc7;
  }
</style>

<div class="form-container">
  <h2>Modifica Fornitore</h2>
  <form method="POST">
    <input type="text" name="name" value="{{ supplier.name }}" placeholder="Nome Fornitore" required>
    <input type="email" name="email" value="{{ supplier.email }}" placeholder="Email" required>
    <input type="text" name="phone" value