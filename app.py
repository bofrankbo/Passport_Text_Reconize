from flask import Flask
from modules.routes import routes
from modules.tasks import scheduler
import logging

app = Flask(__name__)
app.register_blueprint(routes)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info("Starting Flask app with scheduled tasks...")
    app.run(host="0.0.0.0")