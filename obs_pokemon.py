import obspython as obs
import requests
import os
from PIL import Image, ImageDraw, ImageFont

poke_api_url = "http://192.168.1.3:9001/obs-pokemon/team/species"

headers = {
        "Accept": "application/json",
    }

nuzlocke_theme = ""
checkbox_value = False
pkmn = 0

level_cap = 0
fainted = 0



def script_description():
    return "Pokemon sprite finder."

def script_update(settings):

    global nuzlocke_theme

    global pkmn
    global checkbox_value

    global level_cap
    global fainted


    nuzlocke_theme = obs.obs_data_get_string(settings, "nuzlocke_theme")
    checkbox_value = obs.obs_data_get_bool(settings, "shiny_checkbox")
    pkmn = obs.obs_data_get_int(settings, "pkmn")

    level_cap = obs.obs_data_get_int(settings, "level_cap")

    
    update_text_source(settings)



def create_image(section : str, title : str, text: str):
    img = Image.new('RGBA', (270, 100), (0, 0, 0, 0))

    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("font/impact.ttf", 50)
    except IOError:
        font = ImageFont.load_default()

    d.text((10,10), text, fill="white", stroke_width=2, stroke_fill="black", font=font)

    path = f'C:/nuzlocke-recordings/{title}'

    if not os.path.exists(path):
        obs.script_log(obs.LOG_INFO, "Creating a directory")
        os.makedirs(path)

    file = f'{path}/{section}.png'
    img.save(file, 'PNG')
    return file


def generate_level_cap_image(props, prop):

    obs.script_log(obs.LOG_INFO, f'Generate an image level cap of {str(level_cap)}')
    file = create_image("level_cap_image", nuzlocke_theme, f"LEVEL CAP : {str}")
    
    if file != '':
        current_scene_source = obs.obs_frontend_get_current_scene()
        current_scene = obs.obs_scene_from_source(current_scene_source)

        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "file", file)

        image_source = obs.obs_source_create("image_source", 'level cap image', settings, None)

        obs.obs_scene_add(current_scene, image_source)
        obs.obs_source_release(image_source)
        obs.obs_data_release(settings)
        obs.obs_source_release(current_scene_source)  






def search_pkmn_sprite(props, prop):
    obs.script_log(obs.LOG_INFO, gen_selected)
    obs.script_log(obs.LOG_INFO, f"{str(pkmn)}")
    obs.script_log(obs.LOG_INFO, nuzlocke_theme)

    request = {
        "id": pkmn,
        "is_shiny": checkbox_value,
        "generation": gen_selected,
        "art_style": ""
    }

    response = requests.post(f"{poke_api_url}/{str(pkmn)}", headers=headers, json=request)

    if response.status_code == 200:
        data = response.json()
        obs.script_log(obs.LOG_INFO, str(data))

        get_pkmn_img = requests.get(data['data']['image'], stream=True)
        get_pkmn_img.raise_for_status()

        species = data['data']['species']

        path = f'C:/nuzlocke-recordings/{nuzlocke_theme}'

        if not os.path.exists(path):
            obs.script_log(obs.LOG_INFO, "Creating a directory")
            os.makedirs(path)

        result = f'{path}/{species}-{gen_selected}.png'

        with open(result, 'wb') as file:
            for chunk in get_pkmn_img.iter_content(chunk_size=8192):
                file.write(chunk)
        
        obs.script_log(obs.LOG_INFO, f'Sucessfully uploaded {species}')

        # create the scene
        current_scene_source = obs.obs_frontend_get_current_scene()
        current_scene = obs.obs_scene_from_source(current_scene_source)

        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "file", result)

        image_source = obs.obs_source_create("image_source", species, settings, None)

        obs.obs_scene_add(current_scene, image_source)
        obs.obs_source_release(image_source)
        obs.obs_data_release(settings)
        obs.obs_source_release(current_scene_source)  

    return True


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_text(props, "nuzlocke_theme", "Title of your Nuzlocke", obs.OBS_TEXT_DEFAULT)

    dropdown = obs.obs_properties_add_list(props, "gen_selected", "Choose a Gen", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(dropdown, "Gen 1", "generation-i")
    obs.obs_property_list_add_string(dropdown, "Gen 2", "generation-ii")
    obs.obs_property_list_add_string(dropdown, "Gen 3", "generation-iii")
    obs.obs_property_list_add_string(dropdown, "Gen 4", "generation-iv")
    obs.obs_property_list_add_string(dropdown, "Gen 5", "generation-v")
    obs.obs_property_list_add_string(dropdown, "Gen 6", "generation-vi")
    obs.obs_properties_add_int(props, "pkmn", "Species", 1, 1000, 1)

    obs.obs_properties_add_bool(props, "shiny_checkbox", "Is it shiny?")
    obs.obs_properties_add_button(props, "pkmn_search", "Search", search_pkmn_sprite)


    return props




def update_text_source(settings):

    global gen_selected
    gen_selected = obs.obs_data_get_string(settings, "gen_selected")



