import bson.errors
from flask import Flask, request, jsonify
from bson import ObjectId
import pymongo.errors
from sql_info import mongo_url, db_name
from datetime import date
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
        dic_livro = request.json
        try:
            cur.execute(f"SELECT * FROM usuarios WHERE id={id}")
            if cur.rowcount == 0:
                return {"message" : f"Usuário com ID={id} não existe."}, 204
            else:
                values = cur.fetchone()
                cols = ["nome", "email", "data_cadastro"]
                values = dict([(cols[i], values[i+1]) for i in range(len(values)-1)])
                
                for k, val in dic_livro.items():
                    values[k] = val
                
                values = [f'{cols[i]} = \'{values[cols[i]]}\'' for i in range(len(cols))]
                cur.execute(f'UPDATE usuarios SET {", ".join(values)} WHERE id={id}')
                conn.commit()
                return {'message' : f'Usuário com ID={id} atualizado com sucesso.'}, 200

        except psycopg2.Error as e:
            conn.rollback()
            return {"erro": str(e)}, 400
        finally:
            cur.close()
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
        print(args)

        try:
            if args:
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
        cur = conn.cursor()
        dic_livro = request.json

        for key in ["titulo", "autor", "ano_publi", "genero"]:
            if key not in dic_livro.keys():
                if key == "titulo":
                    return {"message" : "Necessário informar Título do livro."}, 400
                elif key == "ano_publi":
                    dic_livro[key] = 0
                else:
                    dic_livro[key] = ""

        try:
            cur.execute("""INSERT INTO livros (titulo, autor, ano_publi, genero) 
                        VALUES ('{titulo}', '{autor}', {ano_publi}, '{genero}')""".format(**dic_livro))
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            return {"erro": str(e)}, 400
        finally:
            cur.close()

        resp = {
        "message": "Livro cadastrado",
        "livro": dic_livro}

        return resp, 201
#-----------------------------------------------------------------

#GET (/bikes/<int:id>): Retorna detalhes de um livro específico pelo ID.
#DELETE (/bikes/<int:id>): Exclui um livro pelo ID.
#PUT (/bikes/<int:id>): Atualiza um livro pelo ID.
@app.route("/bikes/<int:id>", methods=["GET", "DELETE", "PUT"])
def get_bike(id):
    collection = database['bikes']

    #------------ GET ------------
    if request.method == "GET":
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT * FROM livros WHERE id={id}")
            data = cur.fetchone()
        except psycopg2.Error as e:
            return {"erro": str(e)}, 400
        finally:
            cur.close()

        if data == None:
            return {'message' : f'Livro com ID={id} não encontrado.'}, 204
        else:
            return {"livro" : data}, 200
    
    #------------ DELETE ------------
    elif request.method == "DELETE":
        cur = conn.cursor()
        try:
            cur.execute(f"DELETE FROM livros WHERE id={id}")
            if cur.rowcount == 0:
                return {"message" : f"Livro com ID={id} não existe."}, 204
            else:
                conn.commit()
                return {"message" : f"Livro com ID={id} deletado com sucesso."}, 200
        except psycopg2.Error as e:
            conn.rollback()
            return {"erro": str(e)}, 400
        finally:
            cur.close()
    
    #------------ PUT ------------
    elif request.method == "PUT":
        cur = conn.cursor()
        dic_livro = request.json
        try:
            cur.execute(f"SELECT * FROM livros WHERE id={id}")
            if cur.rowcount == 0:
                return {"message" : f"Livro com ID={id} não existe."}, 204
            else:
                values = cur.fetchone()
                cols = ['titulo', 'autor', 'ano_publi', 'genero']
                values = dict([(cols[i], values[i+1]) for i in range(len(values)-1)])
                
                for k, val in dic_livro.items():
                    values[k] = val
                
                values = [f'{cols[i]} = \'{values[cols[i]]}\'' if cols[i] != 'ano_publi' else f'{cols[i]} = {values[cols[i]]}' for i in range(len(cols))]
                cur.execute(f'UPDATE livros SET {", ".join(values)} WHERE id={id}')
                conn.commit()
                return {'message' : f'Livro com ID={id} atualizado com sucesso.'}, 200

        except psycopg2.Error as e:
            conn.rollback()
            return {"erro": str(e)}, 400
        finally:
            cur.close()

#-----------------------------------------------------------------

#--------------------------- Empréstimos ----------------------------
    
#GET (/emprestimos): Lista todos os empréstimos.
@app.route("/emprestimos", methods=["GET"]) 
def get_emprestimos():
    collection = database['usuarios']
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM usuarios")
    except psycopg2.Error as e:
        return {"erro": str(e)}, 400
    finally:
        data = cur.fetchall()
        cur.close()

    return {"usuarios" : data}, 200
#-----------------------------------------------------------------

#DELETE /emprestimos/<int:id>: Exclui um empréstimo pelo ID.
@app.route("/emprestimos/<int:id>", methods=["DELETE"])
def delete_emprestimo(id):
    collection = db['usuarios']
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM usuarios WHERE id={id}")
        if cur.rowcount == 0:
            return {"message" : f"Usuário com ID={id} não existe."}, 204
        else:
            conn.commit()
            return jsonify({"message" : f"Usuário com ID={id} deletado com sucesso."}), 200
    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}, 400
    finally:
        cur.close()
#-----------------------------------------------------------------

#POST /emprestimos/usuarios/<id_usuario>/bikes/<id_bike>: Exclui um empréstimo pelo ID.
@app.route("/emprestimos/usuarios/<id_usuario>/bikes/<id_bike>", methods=["POST"])
def post_emprestimo(id):
    collection = db['emprestimo']
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM usuarios WHERE id={id}")
        if cur.rowcount == 0:
            return {"message" : f"Usuário com ID={id} não existe."}, 204
        else:
            conn.commit()
            return jsonify({"message" : f"Usuário com ID={id} deletado com sucesso."}), 200
    except psycopg2.Error as e:
        conn.rollback()
        return {"erro": str(e)}, 400
    finally:
        cur.close()
#-----------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
