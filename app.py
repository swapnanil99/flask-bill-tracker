from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)   # IMPORTANT
    date = db.Column(db.DateTime, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():

    expenses = Expense.query.order_by(Expense.id.desc()).all()

    total_bills = len(expenses)

    paid_count = Expense.query.filter_by(status="Paid").count()

    pending_count = Expense.query.filter_by(status="Pending").count()

    total_amount = db.session.query(
        db.func.sum(Expense.amount)
    ).scalar() or 0

    return render_template(
        'index.html',
        expenses=expenses,
        total_bills=total_bills,
        paid_count=paid_count,
        pending_count=pending_count,
        total_amount=total_amount
    )


@app.route('/add', methods=['POST'])
def add():

    description = request.form.get('description')
    amount = float(request.form.get('amount'))
    category = request.form.get('category')
    status = request.form.get('status')
    date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')

    new_bill = Expense(
        description=description,
        amount=amount,
        category=category,
        status=status,
        date=date
    )

    db.session.add(new_bill)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/delete/<int:id>')
def delete(id):

    bill = Expense.query.get_or_404(id)

    db.session.delete(bill)
    db.session.commit()

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)