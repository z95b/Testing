import pandas as pd
import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Cargar el archivo CSV
file_path = 'volaris/volaris.csv'  # Actualiza con la ruta correcta a tu archivo CSV
volaris_data = pd.read_csv(file_path)

# Definir la función para calcular la distancia utilizando la fórmula del haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Función para obtener las coordenadas de una ciudad utilizando Geopy
def get_coordinates(city, country_code='US'):
    geolocator = Nominatim(user_agent="city_airport_locator")
    try:
        location = geolocator.geocode(f"{city}, {country_code}")
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except GeocoderTimedOut:
        return get_coordinates(city, country_code)

# Lista de ciudades de interés
cities = [
    "Las Vegas", "Sacramento", "Tulsa", "Wichita", "Louisville", "Omaha", "Des Moines", 
    "Oklahoma City", "Memphis", "Rochester", "Knoxville", "Buffalo", "Grand Rapids", 
    "Lincoln", "Toledo", "Norfolk", "Madison", "Richmond", "Harrisburg", "Palm Springs", 
    "Sioux Falls", "Birmingham", "Charleston", "Cedar Rapids"
]

closest_airports = []

# Encontrar el aeropuerto más cercano para cada ciudad del array cities
for city in cities:
    city_lat, city_lon = get_coordinates(city)
    
    if city_lat is None or city_lon is None:
        closest_airports.append((city, "No disponible", "No disponible"))
        continue
    
    min_distance = float('inf')
    closest_airport = None
    
    for index, row in volaris_data.iterrows():
        airport_lat = row['airport_lat']
        airport_lon = row['airport_lon']
        distance = haversine(city_lat, city_lon, airport_lat, airport_lon)
        
        if distance < min_distance:
            min_distance = distance
            closest_airport = row['airport']
    
    closest_airports.append((city, closest_airport, min_distance))

# Crear un DataFrame con los resultados
df_closest_airports = pd.DataFrame(closest_airports, columns=['Ciudad', 'Aeropuerto más cercano', 'Distancia (km)'])


# Guardar el DataFrame en un archivo CSV si se desea
df_closest_airports.to_csv('volaris/aeropuertos_mas_cercanos.csv', index=False)
