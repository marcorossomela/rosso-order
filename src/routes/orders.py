from flask import Blueprint, render_template, request, redirect, url_for, flash from flask_mail import Message from flask_login import login_required from src.extensions import db, mail from src.models.order import Order from src.models.supplier import Supplier

orders_bp = Blueprint('orders_bp', name)

@orders_bp.route('/create', methods=['GET', 'POST']) @login_required def create_order(): suppliers = Supplier.query.all()

if request.method == 'POST':
    supplier_id = request.form.get('supplier_id')
    details = request.form.get('details')
    cc_email = request.form.get('cc_email')

    if not supplier_id or not details:
        flash('Tutti i campi sono obbligatori.', 'danger')
        return redirect(url_for('orders_bp.create_order'))

    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        flash('Fornitore non valido.', 'danger')
        return redirect(url_for('orders_bp.create_order'))

    # Salva ordine nel DB
    new_order = Order(supplier_id=supplier_id, details=details)
    db.session.add(new_order)
    db.session.commit()

    # Invia l'email
    try:
        msg = Message(
            subject=f"Nuovo Ordine da Rossopomodoro",
            recipients=[supplier.email],
            body=f"Ciao {supplier.name},\n\nHai ricevuto un nuovo ordine:\n\n{details}\n\nGrazie!",
            cc=[cc_email] if cc_email else []
        )
        mail.send(msg)
        flash('Ordine inviato e salvato correttamente.', 'success')
    except Exception as e:
        flash(f"Errore nell'invio email: {e}", 'danger')

    return redirect(url_for('auth_bp.dashboard'))

return render_template('create_order.html', suppliers=suppliers)

