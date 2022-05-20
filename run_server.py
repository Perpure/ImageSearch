from web import app
import os

file_path = os.path.realpath(__file__)
app.config['PROJECT_DIR'] = file_path
app.run(debug=True, host='0.0.0.0', threaded=True)