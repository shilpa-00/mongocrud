from flask import Flask, Response, request, render_template
from pymongo import MongoClient
import json
from bson.objectid import ObjectId

app=Flask(__name__)

# try:
#     mongo=MongoClient(host='localhost',port=27017,serverSelectionTimeoutMS=1000)
#     db=mongo.studentsdb #client instance is used to create a MongoDB database called studentsdb
#     print('Database connected')
#     mongo.server_info() #trigger exception if cant connect to db
# except:
#     print('Cant connect to db')

def get_db():
    try:
        client=MongoClient(host='mongo',port=27017)
        db=client["studentsdb"]
        print('Database connected')
    except:
        print('Error in connecting database')
    return db

@app.route('/')
def home():
    return "The server is running"

@app.route('/students',methods=['GET','POST'])
def create_user():
    db=get_db()
    if request.method=='POST':
        try:
            data=request.get_json()
            student={"name":data["name"],"department":data["department"]}
            dbResponse=db.students.insert_one(student) #inserts document into collection by creating collection if not exists
            return Response(
                response= json.dumps(
                    {"message":"Student created", 
                    "studentID":f"{dbResponse.inserted_id}"
                    }),
                status= 200,
                mimetype="application/json"
            )
        except:
            return Response(
                response= json.dumps({"message":"Cannot insert students"}),
                status= 500,
                mimetype="application/json"
            )
    elif request.method=='GET':
        print("Hey from get")
        try:
            data=list(db.students.find())
            for student in data:
                student["_id"]=str(student["_id"])
            return Response(
                response= json.dumps(data),
                status= 200,
                mimetype="application/json"
            )
        except:
            return Response(
                response= json.dumps({"message":"Cannot get students"}),
                status= 404,
                mimetype="application/json"
            )
    else:
         return Response(
                response= json.dumps({"message":"403"}),
                status= 403,
                mimetype="application/json"
            )
@app.route('/students/<id>',methods=['GET'])
def getstudent(id):
    db=get_db()
    data=db.students.find_one({"_id":ObjectId(id)})
    if data is None:
        return Response(
                response= json.dumps({"message":"No students with that id"}),
                status= 404,
                mimetype="application/json"
            )
    data["_id"]=str(data["_id"])
    return Response(
                response= json.dumps(data),
                status= 200,
                mimetype="application/json"
            )

@app.route('/students/<id>',methods=['PUT'])
def updatestudent(id):
    db=get_db()
    updateddata=request.get_json()
    student=db.students.find_one({'_id':ObjectId(id)})
    if student is None:
        return Response(
                response= json.dumps({"message":"No students with that id"}),
                status= 404,
                mimetype="application/json"
            )
    data=db.students.update_one(
        {'_id':ObjectId(id)},
        {'$set':{'name':updateddata['name'],'department':updateddata['department']}}
    )
    if data.modified_count==1:
        return Response(
                response= json.dumps({"message":"Student updated"}),
                status= 200,
                mimetype="application/json"
            )
    else:
        return Response(
                response= json.dumps({"message":"Data is up to date"}),
                status= 200,
                mimetype="application/json"
            )

@app.route('/students/<id>',methods=['DELETE'])
def deletestudent(id):
    db=get_db()
    student=db.students.find_one({'_id':ObjectId(id)})
    if student is None:
        return Response(
                response= json.dumps({"message":"No students with that id"}),
                status= 404,
                mimetype="application/json"
            )
    data=db.students.delete_one({'_id':ObjectId(id)})
    return Response(
            response= json.dumps({"message":"Student deleted"}),
            status= 200,
            mimetype="application/json"
        )

if __name__=='__main__':
    app.run(port=5000,debug=True,host='0.0.0.0')