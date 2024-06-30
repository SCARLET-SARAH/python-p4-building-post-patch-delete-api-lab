#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Bakery API</h1>'

@app.route('/bakeries', methods=['GET'])
def bakeries():
    bakeries = Bakery.query.all()
    return jsonify([bakery.to_dict() for bakery in bakeries])

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if bakery:
        if request.method == 'PATCH':
            name = request.form.get('name')
            if name:
                bakery.name = name
                db.session.commit()
            return jsonify(bakery.to_dict())
        else:
            return jsonify(bakery.to_dict(include_baked_goods=True))
    else:
        return jsonify({'error': 'Bakery not found'}), 404

@app.route('/baked_goods', methods=['GET', 'POST'])
def baked_goods():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        bakery_id = int(request.form.get('bakery_id'))
        baked_good = BakedGood(name=name, description=description, price=price, bakery_id=bakery_id)
        db.session.add(baked_good)
        db.session.commit()
        return jsonify(baked_good.to_dict()), 201
    else:
        baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
        return jsonify([baked_good.to_dict() for baked_good in baked_goods])

@app.route('/baked_goods/<int:id>', methods=['GET', 'DELETE'])
def baked_good_by_id(id):
    baked_good = BakedGood.query.get(id)
    if baked_good:
        if request.method == 'DELETE':
            db.session.delete(baked_good)
            db.session.commit()
            return jsonify({'message': 'Baked good deleted successfully'}), 200
        else:
            return jsonify(baked_good.to_dict())
    else:
        return jsonify({'error': 'Baked good not found'}), 404

if __name__ == '__main__':
    app.run(port=5555, debug=True)