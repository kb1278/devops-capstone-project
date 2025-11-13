import sys
from flask import Flask
from service import config
from service.common import log_handlers
from flask_talisman import Talisman

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

# Disable HTTPS redirects in testing to avoid 302s
talisman_force_https = False
if app.config.get("TESTING", False):
    talisman_force_https = False

talisman = Talisman(app, force_https=talisman_force_https)

# Import routes and models AFTER Flask app creation to avoid circular imports
# pylint: disable=wrong-import-position, cyclic-import
from service import routes, models  # noqa: F401 E402
from service.common import error_handlers, cli_commands  # noqa: F401 E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

# Banner log for service start
app.logger.info("*" * 70)
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info("*" * 70)

# Initialize the database
try:
    models.init_db(app)
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("Database initialization failed: %s", error)
    # Gunicorn requires exit code 4 to stop spawning workers on failure
    sys.exit(4)

app.logger.info("Service initialized successfully!")


