from app.app import app

# Add health check route for deployment monitoring
@app.route('/api/ping')
def ping():
    return {'status': 'ok', 'message': 'SaveMax API is running'}

if __name__ == '__main__':
    app.run() 