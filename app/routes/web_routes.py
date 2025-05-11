from flask import render_template, send_from_directory

def register_routes(app):
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')

    @app.route('/process/<int:pid>')
    def process_details(pid):
        """Process details page"""
        return render_template('process_details.html', pid=pid)