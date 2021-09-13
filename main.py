import time, os
import requests, json
from ipregistry import IpregistryClient
import threading
import ctypes
from random import choice
from dotenv import load_dotenv
from datetime import datetime as dt

"""This script will change your wallpaper according to the weather... """
""" YOU MAY ADD OR DELETE ANY OTHER IMAGES YOU WANT IN THE /Warm AND /Cool Folders *.jpg *.png or even *.gif... """

"""
Third parties -
- ip-registry - https://ipregistry.co/
- api.tomorrow - https://www.tomorrow.io
"""

"""Getting the api keys from the env file, (this file wont be shown on github because it has api keys), if you need your own 
api keys then check out the links stated above..."""

load_dotenv()
CLIENT = IpregistryClient(os.getenv("IP_API_KEY"))
IP_INFO = ""

"""Getting User and local drive info"""
user = input("Enter the current user: \n")
DRIVE_LETTER = input("\nEnter your local disk drive letter.. just the letter please \n")


"""CODE FOR UNBLOCKING THE IMAGES IN  THE 'Warm and Cool' FOLDERS THAT ARE GOING TO BE USED AS WALLPAPERS..."""

try:

    os.system("powershell.exe -Command Unblock-File -Path '%userprofile%/desktop/WeatherWall/walls/Cool/*.jpg,*.png,*.gif'")

    os.system("powershell.exe -Command Unblock-File -Path '%userprofile%/desktop/WeatherWall/walls/Warm/*.jpg,*.png,*.gif'")

except Exception as error:
    print("error occurred while trying to unblock files.\n" + str(error))

"""CODE FOR LOOKING UP THE LOCATION OF CLIENT.. PROVIDED THAT CLIENT IS CONNECTED TO THE INTERNET.."""
try:
    IP_INFO = CLIENT.lookup()
except Exception as exception:
    print("error\n" + str(exception))

our_data = IP_INFO
api_key = os.getenv("WEATHER_API")


List_of_cool_files = []  # list for all the images in the Cool folder
List_of_warm_files = []  # same for the Warm folder

"""Gets all the files in the cool and warm walls dir and stored them in a list"""

List_of_cool_files.append(os.listdir(f"C:/Users/{user}/Desktop/WeatherWall/walls/Cool"))
List_of_warm_files.append(os.listdir(f"C:/Users/{user}/Desktop/WeatherWall/walls/Warm"))

print(f"Warm dir --> {List_of_warm_files}")
print(f"Cool dir --> {List_of_cool_files}")

RUN = True

"""WRITING THE LOCATION INFO OF USER TO location.json"""
# os.system("unblock.bat")
try:
    with open("location.json", "w") as json_file:
        json_file.write(str(our_data))

    with open("location.json", "r") as json_file:
        object_gotten = json_file.read()

except Exception as error:
    json_file.close()
    print(str(error))


"""EXTRACTING THE LOCATION INFO FROM location.json into a python Dictionary"""


def extract_data_from_location_json(location_object):
    object_12 = json.loads(location_object)
    dict_format = dict(object_12)

    # getting country/region
    country = dict_format["location"]["country"]["name"]
    city = dict_format["location"]["region"]["name"]
    print("\nLocation:\n" + country, end="\n" + city + "\n")

    # getting latitude/ longitude
    lat = dict_format["location"]["latitude"]
    long = dict_format["location"]["longitude"]

    # returning a url api request to api.tomorrow using the lat and long
    api_request = f"https://api.tomorrow.io/v4/timelines?location={lat},{long}&fields=temperature&timesteps=1h&units=metric&apikey={api_key}"

    return api_request


# using that url to now make a request using this function
def get_data(request):
    try:
        data = requests.get(request)
        returned_data = json.loads(data.content)
        # this returned data will be written to temperature.json file
        return returned_data

    except Exception as e:
        print("error\n" + str(e))


"""writing temperatures in temperature.json file"""


def write_temperature_to_file(func, filename, mode):
    with open(filename, mode) as temperature_file:
        json.dump(func, temperature_file, indent=3)


"""same process - converting to python dictionary"""


def get_the_temp_now(filename, mode):
    with open(filename, mode) as temperature_file:
        try:
            temp_object = temperature_file.read()

        except Exception as f:
            print(str(f))
    all_temperatures = json.loads(temp_object)
    dict_format = dict(all_temperatures)

    # getting the main temperature that matters at the current time the most
    main_temperature = 1

    return main_temperature


""" this function below is for choosing a random image from the two folders namely- Warm and Cool"""


def random(array_of_images: list):
    random_file = choice(array_of_images)
    random_image = choice(random_file)

    return random_image


def random2(array_of_cools: list):
    random_file = choice(array_of_cools)
    random_image = choice(random_file)

    return random_image


"""Now the main part comes for manipulating the desktop wallpaper according to the temperature"""


def manipulate(temp: float, warm_files: str, cool_files: str):

    if temp >= 23:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, f"{DRIVE_LETTER.upper()}:/Users/{user}/Desktop/WeatherWall/walls/Warm/{warm_files}",
                                                    0)
        if temp <= 27:
            print("\nWarm weather-")

        elif temp <= 33:
            print("\nHot weather-")

        elif temp > 33:
            print("\nVery hot weather-")

    if temp < 23:
        ctypes.windll.user32.SystemParametersInfoW(20, 0,
                                                   f"{DRIVE_LETTER.upper()}:/Users/{user}/Desktop/WeatherWall/walls/Cool/{cool_files}",
                                                0)
        if temp > 20:
            print("\nAveragely-cool/warm weather-")

        elif temp > 15:
            print("\nCool weather -")

        elif temp > 10:
            print("\nCold weather -")

        elif temp > 0:
            print("\nExtremely chilly/cold weather")

        else:
            print("\nIcy weather-")


"""THIS RECURSIVE FUNC MAKES A REQUEST EVERY 2000 SECONDS TO UPDATE THE WEATHER, FOR BETTER ACCURACY"""


def request_loop():

    write_temperature_to_file((get_data(str(extract_data_from_location_json(object_gotten)))), "temperature.json", "w")
    time.sleep(2000)

    request_loop()


"""THE MAIN LOOP WILL RUN AND CHANGE WALLPAPERS AFTER EVERY INTERVAL (time_interval arg)..."""


def main(state: bool, time_interval: float):

    while state is True:
        now = dt.now()
        current_time = now.strftime("%H:%M %p")

        manipulate(get_the_temp_now("temperature.json", "r"), str(random(List_of_warm_files)), str(random2(List_of_cool_files)))
        print(str(get_the_temp_now("temperature.json", "r")) + f" Degrees Celsius.\n Current-time: {current_time} ")
        time.sleep(time_interval)


'''THESE TWO FUNCTIONS ARE GIVEN SEPARATE THREADS TO AVOID ISSUES...'''

Main_thread = threading.Thread(target=lambda: main(RUN, 4))
Sub_thread = threading.Thread(target=request_loop, args=(), kwargs={})

if __name__ == '__main__':
    Sub_thread.start()
    Main_thread.start()


""" YOU MAY ADD OR DELETE ANY OTHER IMAGES YOU WANT IN THE /Warm AND /Cool Folders *.jpg *.png or even *.gif... """



