from multiprocessing import Process

def run_recognition_server():
    from server_recognition import app
    app.run(port=8000)

def run_admin_server():
    from server_admin import app_admin
    app_admin.run(port=8001)

if __name__ == '__main__':
    Process(target=run_recognition_server).start()
    Process(target=run_admin_server).start()
