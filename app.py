import bson.errors
from flask import Flask, request, jsonify
from bson import ObjectId
import pymongo.errors
from sql_info import mongo_url, db_name
from datetime import datetime
import pymongo
import bson

app = Flask("aps5_henrique_bucci")

client = pymongo.MongoClient(mongo_url)
db = client['aps5']

#--------------------------- Root ----------------------------

#GET (/): Deve retornar "Bem-vindo ao sistema".
@app.route("/", methods=["GET"])
def hello_world():
    return "Bem-vindo ao sistema."
#-----------------------------------------------------------------

#--------------------------- Usuários ----------------------------
    
#GET (/usuarios): Lista todos os usuários.
#POST (/usuarios): Cadastro de um novo usuário.
@app.route("/usuarios", methods=["GET", "POST"])
def get_usuarios():
    collection = db['usuarios']

    #------------ GET ------------
    if request.method == "GET":

        try:
            users = list(collection.find({}))
            for user in users:
                user['_id'] = str(user['_id'])

        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500

        return {"usuarios" : users}, 200
    
    #------------ POST ------------
    elif request.method == "POST":
        user = request.json

        for key in ["nome", "cpf", "data_nascimento"]:
            if key not in user.keys():
                return {"message" : f"Necessário informar campo {key} para realizar o cadastro."}, 400

        try:
            inserted = collection.insert_one(user)
        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500
        finally:
            user['_id'] = str(user['_id'])

        resp = {
        "message": "Usuário cadastrado",
        "usuario": user}

        return resp, 201
#-----------------------------------------------------------------

#GET (/usuarios/<int:id>): Retorna detalhes de um usuário específico pelo ID.
#DELETE /usuarios/<int:id>: Exclui um usuário pelo ID.
#PUT (/usuarios/<int:id>): Atualiza um usuário pelo ID.
@app.route("/usuarios/<string:id>", methods=["GET", "DELETE", "PUT"])
def get_usuario(id):
    collection = db['usuarios']

    #------------ GET ------------
    if request.method == "GET":
        try:
            user = collection.find_one({"_id": ObjectId(id)})
        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500
        finally:
            user['_id'] = str(user['_id'])

        return {"usuario" : user}, 200
    
    #------------ DELETE ------------
    elif request.method == "DELETE":
        try:
            deleted = collection.delete_one({'_id' : ObjectId(id)})
            if deleted.deleted_count == 0:
                return {"message" : f"Usuário com ID={id} não encontrado."}, 200
            else:
                return {"message" : f"Usuário com ID={id} deletado com sucesso."}, 200
        except bson.errors.InvalidId:
            return {"message": 'Insira um ID válido.'}, 400
        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500
    
    #------------ PUT ------------
    elif request.method == "PUT":
        update_data = request.json
        try:
            updated = collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            if updated.modified_count == 0:
                return {"message" : f"Usuário com ID={id} não encontrado."}, 200
            else:
                return {"message" : f"Usuário com ID={id} atualizado com sucesso."}, 200
        except bson.errors.InvalidId:
            return {"message": 'Insira um ID válido.'}, 400
        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500
#-----------------------------------------------------------------

#--------------------------- Bikes ----------------------------

#GET (/bikes): Lista todas as bikes. Suporte para query por cidade.
#POST (/bikes): Cadastro de um novo livro.
@app.route("/bikes", methods=["GET", "POST"])
def get_bikes():
    collection = db['bikes']

    #------------ GET ------------
    if request.method == "GET":
        args = request.args.to_dict()
        try:
            if args:
                if 'disponibilidade' in args:
                    tf = {'true' : True, 'false' : False}
                    args['disponibilidade'] = tf[args['disponibilidade']]
                
                bikes = collection.find(args)
            else:
                bikes = collection.find({})

            bikes = list(bikes)
            for bike in bikes:
                bike['_id'] = str(bike['_id'])

        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500

        return {"bicicletas" : bikes}, 200

    #------------ POST ------------
    elif request.method == 'POST':
        bikes = request.json

        for key in ["marca", "modelo", "cidade", "disponibilidade"]:
            if key not in bikes.keys():
                if key == "disponibilidade":
                    bikes[key] = True
                else:
                    return {"message" : f"Necessário informar {key} da bicicleta."}, 400
        try:
            inserted = collection.insert_one(bikes)
        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500
        finally:
            bikes['_id'] = str(bikes['_id'])

        resp = {
        "message": "Bicicleta cadastrada",
        "bicicletas": bikes}

        return resp, 201
#-----------------------------------------------------------------

#GET (/bikes/<int:id>): Retorna detalhes de um livro específico pelo ID.
#DELETE (/bikes/<int:id>): Exclui um livro pelo ID.
#PUT (/bikes/<int:id>): Atualiza um livro pelo ID.
@app.route("/bikes/<string:id>", methods=["GET", "DELETE", "PUT"])
def get_bike(id):
    collection = db['bikes']

    #------------ GET ------------
    if request.method == "GET":
        try:
            bikes = collection.find_one({"_id": ObjectId(id)})
        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500
        except bson.errors.InvalidId as e:
            return {"message": f"Bicicleta com ID={id} não encontrada."}, 204
        finally:
            if bikes != None:
                bikes['_id'] = str(bikes['_id'])

        return {"bicicletas" : bikes}, 200
    
    #------------ DELETE ------------
    elif request.method == "DELETE":
        try:
            deleted = collection.delete_one({'_id' : ObjectId(id)})
            if deleted.deleted_count == 0:
                return {"message" : f"Bicicleta com ID={id} não encontrada."}, 204
            else:
                return {"message" : f"Bicicleta com ID={id} deletada com sucesso."}, 200
        except bson.errors.InvalidId:
            return {"message": 'Insira um ID válido.'}, 400
        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500
    
    #------------ PUT ------------
    elif request.method == "PUT":
        update_data = request.json
        try:
            updated = collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
            if updated.modified_count == 0:
                return {"message" : f"Bicicleta com ID={id} não encontrado."}, 200
            else:
                return {"message" : f"Bicicleta com ID={id} atualizado com sucesso."}, 200
        except bson.errors.InvalidId:
            return {"message": 'Insira um ID válido.'}, 400
        except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500

#-----------------------------------------------------------------

#--------------------------- Empréstimos ----------------------------
    
#GET (/emprestimos): Lista todos os empréstimos.
@app.route("/emprestimos", methods=["GET"]) 
def get_emprestimos():
    collection = db['emprestimos']
    try:
        emprestimos = list(collection.find({}))
        for emprestimo in emprestimos:
                emprestimo['_id'] = str(emprestimo['_id'])
    except pymongo.errors.PyMongoError as e:
            return {"server_error": str(e)}, 500
    finally:
        emprestimos['_id'] = str(emprestimos['_id'])

    return {"emprestimos" : emprestimos}, 200
#-----------------------------------------------------------------

#DELETE /emprestimos/<int:id>: Exclui um empréstimo pelo ID.
@app.route("/emprestimos/<int:id>", methods=["DELETE"])
def delete_emprestimo(id):
    collection = db['emprestimos']
    try:
        deleted = collection.delete_one({'_id' : ObjectId(id)})
        if deleted.deleted_count == 0:
            return {"message" : f"Emprestimo com ID={id} não encontrado."}, 204
        else:
            return {"message" : f"Emprestimo com ID={id} deletado com sucesso."}, 200
    except bson.errors.InvalidId:
        return {"message": 'Insira um ID válido.'}, 400
    except pymongo.errors.PyMongoError as e:
        return {"server_error": str(e)}, 500
#-----------------------------------------------------------------

#POST /emprestimos/usuarios/<id_usuario>/bikes/<id_bike>: Exclui um empréstimo pelo ID.
@app.route("/emprestimos/usuarios/<id_usuario>/bikes/<id_bike>", methods=["POST"])
def post_emprestimo(id_usuario, id_bike):
    collection = db['emprestimos']
    try:
        # First, check if the user and bike exist
        if not db['usuarios'].find_one({'_id': ObjectId(id_usuario)}):
            return jsonify({"message": "Usuário não encontrado."}), 404
        if not db['bikes'].find_one({'_id': ObjectId(id_bike)}):
            return jsonify({"message": "Bicicleta não encontrada."}), 404

        # Create a new loan entry
        loan = {
            "usuario_id": ObjectId(id_usuario),
            "bike_id": ObjectId(id_bike),
            "data_emprestimo": datetime.now()
        }
        db['emprestimos'].insert_one(loan)

        return jsonify({"message": "Empréstimo registrado com sucesso.", "emprestimo": loan}), 201
    except bson.errors.InvalidId:
        return jsonify({"message": "ID inválido fornecido."}), 400
    except pymongo.errors.PyMongoError as e:
        return jsonify({"server_error": str(e)}), 500
#-----------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
