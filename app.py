from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import json
import folium
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def read_item():
    with open("static/index.html") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/save-location")
async def save_location(request: Request):
    location_data = await request.json()
    if location_data:
        try:
            # Serialize the location data to a string
            location_str = json.dumps(location_data)

            with open('locations.json', 'a') as file:
                # Write the location data followed by a newline
                file.write(location_str)
                file.write('\n')

            return {"message": "Location data saved successfully"}
        except Exception as e:
            print(f"Error saving location data: {e}")
            return {"error": "Failed to save location data"}
    else:
        return {"error": "No location data provided"}



@app.get("/map", response_class=HTMLResponse)
async def map_view():
    # Create a map centered at [0, 0] (equivalent to null island)
    map_center = [0, 0]
    my_map = folium.Map(location=map_center, zoom_start=2)

    # Read saved locations from locations.json
    with open('locations.json', 'r') as file:
        for line in file:
            # Parse each line as a JSON object
            try:
                location = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue

            # Ensure that location is a dictionary
            if not isinstance(location, dict):
                print("Invalid location data:", location)
                continue

            # Extract latitude and longitude from location
            lat = location.get('latitude')
            lon = location.get('longitude')

            # Add marker to the map if latitude and longitude are present
            if lat is not None and lon is not None:
                folium.Marker([lat, lon]).add_to(my_map)

    # Save the map to a temporary HTML file
    map_file = "temp_map.html"
    my_map.save(map_file)

    # Read the HTML content of the temporary map file
    with open(map_file, "r") as file:
        html_content = file.read()

    # Return the HTML content with the map
    return HTMLResponse(content=html_content, status_code=200)



@app.get("/get-locations", response_class=JSONResponse)
async def get_locations():
    locations = []
    try:
        with open('locations.json', 'r') as file:
            for line in file:
                line = line.strip()
                if line:  # Check if line is not empty
                    try:
                        location = json.loads(line)
                        locations.append(location)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
    except FileNotFoundError:
        print("File not found: locations.json")
    return locations
# Add your certificate if you wish to use SSL 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile="server.key", ssl_certfile="server.crt")








