# actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import requests
import json

path_u = ''
name_course = ''
uni_list = {"uabc":"Universidad Autónoma de Baja California",
            "uc":"Universidad Continental",
            "udg":"Universidad de Guadalajara",
            "uned":"Universidad Nacional de Educación a Distancia",
            "unmp":"Universidad Nacional de Mar del Plata",
            "unsam":"Universidad Nacional de San Martín",
            "uncp":"Universidad Nacional del Centro del Perú",
            "ul":"Universidade de Lisboa",
            "unl":"Universidade Nova de Lisboa"}

def get_intent_from_message(message, key):
    print(message)
    start_index = message.find('{')
    print(start_index)
    end_index = message.find('}')
    print(end_index)
    if start_index != -1 and end_index != -1:
        json_string = message[start_index:end_index+1]
        data_course = json.loads(json_string)
        print(data_course)
        print("20")
        print(key)
        print("22")
        return data_course.get(key)
    return None

def get_university_id(intent, universities):
    university_dict = {item[1]: item[0] for item in universities}
    return university_dict.get(intent)

def save_path(path):
    global path_u
    path_u = path
    return path_u

def save_course(course):
    global name_course
    start_index = course.find('{')
    end_index = course.find('}')
    if start_index != -1 and end_index != -1:
        json_string = course[start_index:end_index+1]
        data_course = json.loads(json_string)
        name_course = data_course.get("course")
        print("save_course 45")
        print (name_course)
        print("save_course 47")
        return name_course
    return None
class ActionGetUniversitiesFromAPI(Action):
    def name(self):
        return "action_get_universities_from_api"

    def run(self, dispatcher: CollectingDispatcher, tracker:Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            
            #https://yachay2-ws.javali.pt/chatbot-get-modules/529
            response = requests.get('https://yachay2-ws.javali.pt/list-universities')
            data = response.json()

            # Supongamos que 'data' contiene la información que deseas mostrar
            # La API devuelve un campo llamado 'name'
            # field_to_extract = "name"
            extracted_info = [(item[0],item[1]) for item in data]
            print(extracted_info)
            # for item in data:  #for item in data.get("availableModules", []):
            #     if isinstance(item, dict) and field_to_extract in item:
            #         extracted_info.append(item[field_to_extract])

            if extracted_info:
                buttons = []
                indexC = ''
                for index, item in enumerate(extracted_info):
                    btn_title = f"{item[1]}"
                    btn_payload = f"/action_get_courses_from_api{{\"intent\": \"{item[1]}\"}}"
                    buttons.append({"title": btn_title, "payload": btn_payload})
                    indexC = str(index)
                print(indexC)


                # formatted_info = "<ul>"
                # for item in extracted_info:
                #     formatted_info += "<li>{}</li>".format(item)
                # formatted_info += "</ul>"
                # Almacenar la información en un slot para usarla en la respuesta
                dispatcher.utter_message(buttons=buttons)
                intent = tracker.get_intent_of_latest_message()

                print(intent)
                return []
            else:
                dispatcher.utter_message("No se pudo extraer la información de la API.")
                return []
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message("Ocurrió un error al conectarse a la API: {}".format(str(e)))
            return []
        except Exception as e:
            dispatcher.utter_message("Ocurrió un error inesperado: {}".format(str(e)))
            return []
        

class ActionGetCoursesFromAPI(Action):
    def name(self):
        return "action_get_courses_from_api"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            try_intent = tracker.get_intent_of_latest_message()
            print(try_intent)
            last_message = tracker.latest_message.get("text", "")
            print(f"Last message text: {last_message}")
            intent = get_intent_from_message(last_message, "intent")

            if intent is None:
                if try_intent in uni_list:
                    intent = uni_list[try_intent]

            print(intent)
            obtain_id = requests.get('https://yachay2-ws.javali.pt/list-universities')
            data = obtain_id.json()
            if intent in uni_list or intent in uni_list.values():
                university_id = get_university_id(intent, data)

            print(university_id)
            
            # Ir al path de la universidad seleccionada
            path_uni = save_path('https://yachay2-ws.javali.pt/chatbot-get-modules/{}'.format(university_id))
            response = requests.get(path_uni)
            print(path_u)
            data = response.json()
            print(data)


            field_to_extract = "name"
            extracted_info = []

            for item in data.get("availableModules", []):
                if isinstance(item, dict) and field_to_extract in item:
                    extracted_info.append(item[field_to_extract])

            # for item in data:
            #     if item[field_to_extract] == intent:
            #         extracted_info.extend(item["address"].keys())

            if extracted_info:
                buttons = []
                for index, item in enumerate(extracted_info):
                    btn_title = f"{item}"
                    btn_payload = f"/action_get_steps_from_api{{\"intent\": \"city\", \"course\": \"{item}\"}}"
                    print(btn_payload)
                    buttons.append({"title": btn_title, "payload": btn_payload})

                # formatted_info = "<ul>"
                # for item in extracted_info:
                #     formatted_info += "<li>{}</li>".format(item)
                # formatted_info += "</ul>"
                # Almacenar la información en un slot para usarla en la respuesta
                dispatcher.utter_message(buttons=buttons)
                print(intent)
                print(index)
                return [SlotSet("current_intent", intent)]
            else:
                dispatcher.utter_message("No se pudo extraer la información de la API.")
                return []
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message("Ocurrió un error al conectarse a la API: {}".format(str(e)))
            return []
        except Exception as e:
            dispatcher.utter_message("Ocurrió un error inesperado: {}".format(str(e)))
            return []

class ActionGetStepsFromAPI(Action):
    def name(self):
        return "action_get_steps_from_api"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            print("STEPS")
            last_message = tracker.latest_message.get("text", "")
            print(f"Last message text: {last_message}")
            course_value = get_intent_from_message(last_message, "intent")
            course_get_steps = save_course(last_message)

            print(f"180: {course_value}")
            print(f"181: {course_get_steps}")
            #https://yachay2-ws.javali.pt/chatbot-get-modules/529
            response = requests.get(path_u)
            print(f"199: {path_u}")
            data = response.json()


            # do not care
            intent = tracker.get_slot("current_intent")
            intent2 = tracker.get_intent_of_latest_message()
            print("Si entra")
            print(intent)
            print(intent2)
            # don't

            # for item in data:  #for item in data.get("availableModules", []):
            #     if isinstance(item, dict) and field_to_extract in item:
            #         extracted_info.append(item[field_to_extract])

            if intent:
                print(f"200: {course_get_steps}")

                field_to_extract = "applyInstructions"
                extracted_info = []
                for item in data.get("availableModules", []):
                    if item["name"] == course_get_steps:
                        extracted_info.extend(item[field_to_extract])

                if extracted_info:
                    # formatted_info = "<ul>"
                    # formatted_item = ''
                    # for item in extracted_info:
                    #     item_list = item.split(',')
                    #     formatted_item += "<li>{}</li>".format("</li><li>".join(item_list))
                    #     formatted_info += formatted_item
                    # formatted_info += "</ul>"
                    # Almacenar la información en un slot para usarla en la respuesta
                    full_sting = ''.join(extracted_info)
                    print(full_sting)
                    dispatcher.utter_message(text=full_sting)
                    return []
            else:
                dispatcher.utter_message("No se pudo extraer la información de la API.")
                return []
        except requests.exceptions.RequestException as e:
            dispatcher.utter_message("Ocurrió un error al conectarse a la API: {}".format(str(e)))
            return []
        except Exception as e:
            dispatcher.utter_message("Ocurrió un error inesperado: {}".format(str(e)))
            return []
        