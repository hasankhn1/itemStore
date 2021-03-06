from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'jose'
api = Api(app)

jwt = JWT(app, authenticate, identity)

items = []


class Item(Resource):
  request_parser = reqparse.RequestParser()
  request_parser.add_argument('price',
  type=float,
  required=True,
  help='This is required')
  @jwt_required()
  def get(self, name):
    item = next(filter(lambda x: x['name'] == name, items), None)
    return {'item': item}, 200 if item else 404

  def post(self, name):
    if next(filter(lambda x: x['name'] == name, items), None):
      return {'message': 'An item with {} already exists'.format(name)}, 400

    data = Item.request_parser.parse_args()
    item = ({'name': name, 'price': data['price']})
    items.append(item)
    return item, 201

  def delete(self, name):
    global items
    items = list(filter(lambda x: x['name'] != name, items))
    return {'message': 'Item is successfully deleted'}

  def put(self, name):
    data = Item.request_parser.parse_args()
    item = next(filter(lambda x: x['name'] == name, items),None)
    if item is None:
      new_item = {'name': name, 'price': data['price']}
      items.append(new_item)
      return new_item, 200
    else:
      item['price'] = data['price']
      return item.update(data), 200


class ItemList(Resource):
  def get(self):
    return {'items': items}


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

app.run(port=5000, debug=True)
