# client = pymongo.MongoClient(os.environ.get("MONGO_DSN"))
# db = client.websh
# sh = db.links
# @app.route('/sh/<path>')
# def redirect(path):
#     data = sh.find_one({"path":path})
#     return redirect(data["target"], 301)
