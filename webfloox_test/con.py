from app import app, db

# If you have specific models to import, do it here
# from app.models import User, ...

with app.app_context():
    # Now you're inside the application context
    # Perform your database operations here
    users = db.create_all()  # Example operation
    # Example querying
    print(users)
