from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__)

# Enable CORS to allow communication between frontend and backend
CORS(app, resources={r"/*": {"origins": "http:public_ip:8081"}})

# Country-capital timezones
country_capitals = {
    "Russia": "Europe/Moscow",
    "Canada": "America/Toronto",  # Example timezone
    "United States": "America/New_York",
    "China": "Asia/Shanghai",
    "Brazil": "America/Sao_Paulo",
    "Australia": "Australia/Sydney",
    "India": "Asia/Kolkata",
    "Argentina": "America/Argentina/Buenos_Aires",
    "Kazakhstan": "Asia/Almaty",
    "Algeria": "Africa/Algiers",
    "Democratic Republic of the Congo": "Africa/Kinshasa",
    "Greenland": "America/Nuuk",
    "Saudi Arabia": "Asia/Riyadh",
    "Mexico": "America/Mexico_City",
    "Indonesia": "Asia/Jakarta",
    "Sudan": "Africa/Khartoum",
    "Libya": "Africa/Tripoli",
    "Iran": "Asia/Tehran",
    "Mongolia": "Asia/Ulaanbaatar",
    "Peru": "America/Lima",
    "Chad": "Africa/Ndjamena",
    "Niger": "Africa/Niamey",
    "Angola": "Africa/Luanda",
    "Mali": "Africa/Bamako",
    "South Africa": "Africa/Johannesburg",
    "Colombia": "America/Bogota",
    "Ethiopia": "Africa/Addis_Ababa",
    "Bolivia": "America/La_Paz",
    "Mauritania": "Africa/Nouakchott",
    "Egypt": "Africa/Cairo",
    "Tanzania": "Africa/Dar_es_Salaam",
    "Nigeria": "Africa/Lagos",
    "Venezuela": "America/Caracas",
    "Pakistan": "Asia/Karachi",
    "Namibia": "Africa/Windhoek",
    "Mozambique": "Africa/Maputo",
    "Turkey": "Europe/Istanbul",
    "Chile": "America/Santiago",
    "Zambia": "Africa/Lusaka",
    "Myanmar": "Asia/Yangon",
    "Afghanistan": "Asia/Kabul",
    "South Sudan": "Africa/Juba",
    "France": "Europe/Paris",
    "Somalia": "Africa/Mogadishu",
    "Central African Republic": "Africa/Bangui",
    "Ukraine": "Europe/Kiev",
    "Madagascar": "Indian/Antananarivo",
    "Botswana": "Africa/Gaborone",
    "Kenya": "Africa/Nairobi",
    "Yemen": "Asia/Aden",
    "Thailand": "Asia/Bangkok",
    "Spain": "Europe/Madrid",
    "Turkmenistan": "Asia/Ashgabat",
    "Cameroon": "Africa/Douala",
    "Papua New Guinea": "Pacific/Port_Moresby",
    "Sweden": "Europe/Stockholm",
    "Uzbekistan": "Asia/Tashkent",
    "Morocco": "Africa/Casablanca",
    "Iraq": "Asia/Baghdad",
    "Paraguay": "America/Asuncion",
    "Zimbabwe": "Africa/Harare",
    "Japan": "Asia/Tokyo",
    "Germany": "Europe/Berlin",
    "Republic of the Congo": "Africa/Brazzaville",
    "Finland": "Europe/Helsinki",
    "Vietnam": "Asia/Ho_Chi_Minh",
    "Malaysia": "Asia/Kuala_Lumpur",
    "Norway": "Europe/Oslo",
    "Côte d'Ivoire": "Africa/Abidjan",
    "Poland": "Europe/Warsaw",
    "Oman": "Asia/Muscat",
    "Italy": "Europe/Rome",
    "Philippines": "Asia/Manila",
    "Ecuador": "America/Guayaquil",
    "Burkina Faso": "Africa/Ouagadougou",
    "New Zealand": "Pacific/Auckland",
    "Gabon": "Africa/Libreville",
    "Guinea": "Africa/Conakry",
    "United Kingdom": "Europe/London",
    "Uganda": "Africa/Kampala",
    "Ghana": "Africa/Accra",
    "Romania": "Europe/Bucharest",
    "Laos": "Asia/Vientiane",
    "Guyana": "America/Guyana",
    "Belarus": "Europe/Minsk",
    "Kyrgyzstan": "Asia/Bishkek",
    "Senegal": "Africa/Dakar",
    "Syria": "Asia/Damascus",
    "Cambodia": "Asia/Phnom_Penh",
    "Uruguay": "America/Montevideo",
    "Suriname": "America/Paramaribo",
    "Tunisia": "Africa/Tunis",
    "Nepal": "Asia/Kathmandu",
    "Bangladesh": "Asia/Dhaka",
    "Tajikistan": "Asia/Dushanbe",
    "Greece": "Europe/Athens",
    "Nicaragua": "America/Managua",
    "North Korea": "Asia/Pyongyang",
    "Malawi": "Africa/Blantyre",
    "Eritrea": "Africa/Asmara",
    "Benin": "Africa/Porto-Novo",
    "Honduras": "America/Tegucigalpa",
    "Liberia": "Africa/Monrovia",
    "Bulgaria": "Europe/Sofia",
    "Cuba": "America/Havana",
    "Guatemala": "America/Guatemala",
    "Iceland": "Atlantic/Reykjavik",
    "South Korea": "Asia/Seoul",
    "Hungary": "Europe/Budapest",
    "Portugal": "Europe/Lisbon",
    "Jordan": "Asia/Amman",
    "Serbia": "Europe/Belgrade",
    "Azerbaijan": "Asia/Baku",
    "Austria": "Europe/Vienna",
    "United Arab Emirates": "Asia/Dubai",
    "Czech Republic": "Europe/Prague",
    "Panama": "America/Panama",
    "Sierra Leone": "Africa/Freetown",
    "Ireland": "Europe/Dublin",
    "Georgia": "Asia/Tbilisi",
    "Sri Lanka": "Asia/Colombo",
    "Lithuania": "Europe/Vilnius",
    "Latvia": "Europe/Riga",
    "Togo": "Africa/Lome",
    "Croatia": "Europe/Zagreb",
    "Bosnia and Herzegovina": "Europe/Sarajevo",
    "Costa Rica": "America/Costa_Rica",
    "Slovakia": "Europe/Bratislava",
    "Dominican Republic": "America/Santo_Domingo",
    "Bhutan": "Asia/Thimphu",
    "Estonia": "Europe/Tallinn",
    "Denmark": "Europe/Copenhagen",
    "Netherlands": "Europe/Amsterdam",
    "Switzerland": "Europe/Zurich",
    "Moldova": "Europe/Chisinau",
    "Belgium": "Europe/Brussels",
    # Add remaining countries as needed
}

# Root route
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the World Time App By Ritik Sharma!",
        "usage": "Use /time?country=<country_name> to get the time for a specific country."
    })

# Get time for a specific country
@app.route('/time', methods=['GET'])
def get_time():
    country = request.args.get('country')
    if not country or country not in country_capitals:
        return jsonify({"error": "Invalid country"}), 400

    timezone = pytz.timezone(country_capitals[country])
    now = datetime.now(timezone)
    return jsonify({
        "country": country,
        "capital": country_capitals[country],
        "digital_time": now.strftime("%I:%M %p"),
        "analog_time": now.strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
