from app import app, register_routes

if __name__ == "__main__":
    register_routes()
    app.run(debug=True)
