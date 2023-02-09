
import os
import logging
import pandas as pd
import xgboost as xgb
from flask import Flask, request, Response, jsonify
from google.cloud import storage

client = storage.Client(project=os.environ['PROJECT_ID'])

# Model Download from gcs

fname = "model.json"

with open(fname, "wb") as model:
    client.download_blob_to_file(
        f"{os.environ['AIP_STORAGE_URI']}/{fname}", model
    )

# Loading model
print("[INFO] ------ Loading model from: {}".format(fname))
model = xgb.Booster(model_file=fname)

# Creation of the Flask app
app = Flask(__name__)

# Flask route for Liveness checks
@app.route(os.environ['AIP_HEALTH_ROUTE'])
def isalive():
    status_code = Response(status=200)
    return status_code

# Flask route for predictions
@app.route(os.environ['AIP_PREDICT_ROUTE'],methods=['GET','POST'])
def prediction():
    _features = ['Id','Elevation', 'Aspect', 'Slope', 'Horizontal_Distance_To_Hydrology', 'Vertical_Distance_To_Hydrology', 'Horizontal_Distance_To_Roadways',
                          'Hillshade_9am', 'Hillshade_Noon', 'Hillshade_3pm','Horizontal_Distance_To_Fire_Points', 'Wilderness_Area1', 'Wilderness_Area2', 'Wilderness_Area3', 
                          'Wilderness_Area4', 'Soil_Type1', 'Soil_Type2', 'Soil_Type3', 'Soil_Type4', 'Soil_Type5', 'Soil_Type6', 'Soil_Type7', 'Soil_Type8', 'Soil_Type9',
                          'Soil_Type10','Soil_Type11','Soil_Type12','Soil_Type13','Soil_Type14','Soil_Type15','Soil_Type16','Soil_Type17','Soil_Type18','Soil_Type19', 
                          'Soil_Type20', 'Soil_Type21', 'Soil_Type22', 'Soil_Type23', 'Soil_Type24', 'Soil_Type25', 'Soil_Type26', 'Soil_Type27', 'Soil_Type28', 'Soil_Type29',
                          'Soil_Type30', 'Soil_Type31', 'Soil_Type32', 'Soil_Type33', 'Soil_Type34', 'Soil_Type35', 'Soil_Type36', 'Soil_Type37', 'Soil_Type38', 'Soil_Type39', 'Soil_Type40']
    data = request.get_json(silent=True, force=True)
    dmf = xgb.DMatrix(pd.DataFrame(data["instances"], columns=_features))
    response = pd.DataFrame(model.predict(dmf))
    logging.info(f"Response: {response}")
    return jsonify({"Cover Type": str(response.idxmax(axis=1)[0])})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
