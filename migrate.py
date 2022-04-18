from web import db
from web.models import User, Publication

db.reflect()
db.drop_all()
db.create_all()
user = User("User", "testpassword")
publication = Publication(user, 'text', ['aaa'])