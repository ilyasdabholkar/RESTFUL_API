from flask import Flask,g,request,jsonify
from database import get_db
from functools import wraps 

app = Flask(__name__)
api_username = 'admin'
api_password = 'password'

#closes database connection if left open to avoid memory leaks
@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close;

#Decorator for Authentications
def authorised(f):
    @wraps(f)
    def decorator(*args,**kwargs):
        auth = request.authorization
        #if some authentication is used
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args,**kwargs)
        return jsonify({'message' : 'Authentication Failed'}),403
    return decorator

#Route to return all members
@app.route('/member',methods=['GET'])
@authorised
def get_members():
    db = get_db()
    cur = db.execute("SELECT id,name,email,level from members")
    members = cur.fetchall()
    db.close()

    #Empty list to store all the json objects from database
    return_values=[]
    #create a dictionary object of every member in members
    for member in members:
        member_dict = {}
        member_dict['id'] = member['id']
        member_dict['name'] = member['name']
        member_dict['email'] = member['email']
        member_dict['level'] = member['level']
        #add the dictionary object to return values
        return_values.append(member_dict)
    return jsonify({'members' : return_values})

#Route to get a specific member
@app.route('/member/<int:member_id>',methods=['GET'])
@authorised
def get_member(member_id):
    db = get_db()
    cur = db.execute("SELECT id,name,email,level FROM members WHERE id=?",[member_id])
    member = cur.fetchone()
    db.close()
    return jsonify({'id' : member['id'], 
                    'name' : member['name'], 
                    'email' : member['email'], 
                    'level' : member['level']})

#Route to add a new member
@app.route('/member',methods=['POST'])
@authorised
def add_member():
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute("INSERT INTO members(name,email,level) VALUES(?,?,?)",[name,email,level])
    db.commit()

    cur = db.execute("SELECT id,name,email,level FROM members WHERE email=?",[email])
    new_member = cur.fetchone()
    db.close()

    return jsonify({'id' : new_member['id'], 
                    'name' : new_member['name'], 
                    'email' : new_member['email'], 
                    'level' : new_member['level']})

#Route to update a member details
@app.route('/member/<int:member_id>',methods=['PUT','PATCH'])
@authorised
def edit_member(member_id):
    edit_member_data = request.get_json()
    name = edit_member_data['name']
    email = edit_member_data['email']
    level = edit_member_data['level']

    db = get_db()
    db.execute("UPDATE members SET name = ?,email = ?,level = ? WHERE id = ? ",[name,email,level,member_id])
    db.commit()

    cur = db.execute("SELECT id,name,email,level FROM members WHERE id=?",[member_id])
    member = cur.fetchone()
    db.close()
    return jsonify({'id' : member['id'], 
                    'name' : member['name'], 
                    'email' : member['email'], 
                    'level' : member['level']})
    

#Route to delete a member
@app.route('/member/<int:member_id>',methods=['DELETE'])
@authorised
def delete_member(member_id):
    db = get_db()
    db.execute("DELETE FROM members WHERE id = ? ",[member_id])
    db.commit()
    return jsonify({'message' : 'member deleted'})

if __name__ == '__main__':
    app.run(debug=True)