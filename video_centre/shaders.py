import display_centre.menu as menu
import os

class Shaders(object):
    MENU_HEIGHT = 10
    EMPTY_SHADER = dict(name='none',is_shader=True,shad_type='-',param_number=0,path='-',shad_index=0)
    def __init__(self, root, osc_client, message_handler, data):
        self.root = root
        self.osc_client = osc_client
        self.message_handler = message_handler
        self.data = data
        self.shaders_menu = menu.ShadersMenu(self.data, self.message_handler, self.MENU_HEIGHT )
        self.selected_shader = self.EMPTY_SHADER
        self.focused_param = None
        self.shaders_menu_list = self.generate_shaders_list()
        if self.shaders_menu_list is not None:
            pass
                 
        self.selected_status = '-' ## going to try using symbols for this : '-' means empty, '▶' means running, '■' means not running, '!' means error
        self.selected_param_values = [0.0,0.0,0.0,0.0]
        #self.load_selected_shader()

    def generate_shaders_list(self):
        shaders_menu_list = []
        raw_list = self.shaders_menu.generate_raw_shaders_list()
        shad_i = 0
        for line in raw_list:
            if line['is_shader']:
                stripped_name = line['name'].lstrip()
                has_path, path = self.get_path_for_shader(stripped_name)
                shad_type = self.determine_shader_type(path)
                parameter_number = self.determine_shader_parameter_number(path)
                #print('shader index is {}'.format(shad_i))
                shaders_menu_list.append(dict(name=line['name'],is_shader=True,shad_type=shad_type,param_number=parameter_number,path=path,shad_index=shad_i))
                shad_i = shad_i +1
            else:
                shaders_menu_list.append(dict(name=line['name'],is_shader=False,shad_type='',param_number=None,path=None,shad_index=None))
        return shaders_menu_list


    def get_path_for_shader(self, file_name):
        ######## returns full path for a given file name ########
        for path in self.data.PATHS_TO_SHADERS:    
            for root, dirs, files in os.walk(path):
                if file_name in files:
                    return True, '{}/{}'.format(root, file_name)
        return False, ''

    def determine_shader_type(self, path):
        with open(path, 'r') as selected_shader:
                shader_text = selected_shader.read()
                if '//0-input' in shader_text:
                    return '0in'
                elif '//1-input' in shader_text:
                    return '1in'
                elif '//2-input' in shader_text:
                    return '2in'

                else:
                    return '-'

    def determine_shader_parameter_number(self, path):
        max_amount = 4
        if True: # for now always assume 4 params
            return max_amount
        with open(path, 'r') as selected_shader:
            shader_text = selected_shader.read()
            for i in range(max_amount):
                if 'uniform float u_x{}'.format(i) not in shader_text:
                    return i
            return max_amount

    def load_selected_shader(self):
        self.selected_param_values = [0.0,0.0,0.0,0.0]
        self.osc_client.send_message("/shader/load", [self.selected_shader['path'],self.selected_shader['shad_type'] == '2in',self.selected_shader['param_number']])
        if not self.selected_status == '▶':
            self.selected_status = '■'

    def start_selected_shader(self):
        self.osc_client.send_message("/shader/start", True)
        self.selected_status = '▶'

    def stop_selected_shader(self):
        self.osc_client.send_message("/shader/stop", True)
        self.selected_status = '■'

    def select_shader_index(self, index):
             self.message_handler.set_message('INFO', "choosing shader index %s" % index)
             self.shaders_menu.selected_list_index = index
             self.enter_on_shaders_selection()

    def select_shader_name(self, filename):
            #while self.shaders_menu_list[x]['name']!=filename:
            hier = ""
            for path in filename.split('/'):
                # print("looking for %s" % path)
                for index,shader in enumerate(self.shaders_menu_list):
                    # print("%s: looped over '%s'" % (index, shader['name']))
                    is_file, name = self.shaders_menu.extract_file_type_and_name_from_menu_format(
                                        shader['name'])
                    # print ("name==path is %s" % (name==path))
                    if not is_file and name.strip()==path:
                        # print("found menu %s" %path)
                        #o, ind = self.shaders_menu._check_folder_state("%s/%s"%(hier,path))
                        hier += "%s/"%path
                        if shader['name'][-1:]=="|":
                            # print("opening menu?? %s"%(hier[:-1]))
                            # print("name is '%s'" % shader['name'])
                            self.shaders_menu.update_open_folders(hier)
                            self.shaders_menu.update_open_folders(path)
                            self.shaders_menu_list = self.generate_shaders_list()
                        break
                    elif is_file and name.strip()==path:
                        # print("selecting shader with index %s" % index)
                        self.select_shader_index(index)
                        self.shaders_menu.top_menu_index = index
                        #break
                        return

            print("didn't find a shader for %s " % filename)
            self.message_handler.set_message('INFO', "no shader for '%s'" % filename)

    def enter_on_shaders_selection(self):
        index = self.shaders_menu.selected_list_index
        is_file, name = self.shaders_menu.extract_file_type_and_name_from_menu_format(
            self.shaders_menu_list[index]['name'])
        is_selected_shader = False
        if is_file and name == self.selected_shader['name'].lstrip():
            is_selected_shader = True
        elif is_file:
            self.selected_shader = self.shaders_menu_list[index]
            self.load_selected_shader()
        else:
            self.shaders_menu.update_open_folders(name)
        self.shaders_menu_list = self.generate_shaders_list()
        return is_file, is_selected_shader, self.selected_shader

    def increase_this_param(self, amount_change):
        param = self.focused_param
        current_amount = self.selected_param_values[param]
        amount = self.get_new_param_amount(current_amount,amount_change)
        self.set_param_to_amount(param, amount)

    def decrease_this_param(self, amount_change):
        param = self.focused_param
        current_amount = self.selected_param_values[param]
        amount = self.get_new_param_amount(current_amount,-amount_change)
        self.set_param_to_amount(param, amount)
    
    @staticmethod
    def get_new_param_amount(current, change):
        if current + change > 1:
            return 1
        elif current + change < 0:
            return 0
        else: 
            return current + change
    
    def set_param_to_amount(self, param, amount):
        if self.data.settings['shader']['X3_AS_SPEED']['value'] == 'enabled' and param == 3:
            self.osc_client.send_message("/shader/speed", [param, amount] )
        else:
            self.osc_client.send_message("/shader/param", [param, amount] )
        self.selected_param_values[param] = amount
        
