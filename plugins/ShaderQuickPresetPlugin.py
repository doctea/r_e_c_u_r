import data_centre.plugin_collection
from data_centre.plugin_collection import ActionsPlugin, SequencePlugin

class ShaderQuickPresetPlugin(ActionsPlugin): #,SequencePlugin):
    def __init__(self, plugin_collection):
        super().__init__(plugin_collection)

        self.presets = self.load_presets()

        self.selected_preset = None

    def load_presets(self):
        return [None]*10

    @property
    def parserlist(self):
        return [ 
            ( r"store_next_preset", self.store_next_preset ),
            ( r"store_current_preset", self.store_current_preset ),
            ( r"switch_to_preset_([0-9])", self.switch_to_preset ),
        ]

    def store_next_preset(self):
        # store the current state to a preset
        #insert_position = len(self.presets)
        #if insert_position>10: insert_position = 0

        if self.selected_preset is None:
            self.selected_preset = 0
        else:
            self.selected_preset += 1

        self.selected_preset %= 10
        self.store_current_preset()

    def store_current_preset(self):
        if self.selected_preset is None: self.selected_preset = 0

        insert_position = self.selected_preset
        self.presets[insert_position] = {
                'selected_shader_slots': [ shader.get('slot',None) for shader in self.pc.message_handler.shaders.selected_shader_list ],
                'shader_params': self.pc.message_handler.shaders.selected_param_list.copy(),
                'layer_active_status': self.pc.message_handler.shaders.selected_status_list.copy(),
                'feedback_active': self.pc.data.feedback_active,
        }
        print ("stored %s at position %s" % (self.presets[insert_position], insert_position))
        self.selected_preset = insert_position

    def switch_to_preset(self, preset):
        #if preset>len(self.presets):
        if self.presets[preset] is None:
            print ("no quick shader preset in slot %s!" % preset)
            return
        print ("switching to preset %s" % preset)
        self.selected_preset = preset
        #self.pc.message_handler.actions.shaders.selected_shader_list = self.presets[preset].get('selected_shader_list',self.pc.message_handler.actions.shaders.selected_shader_list)
        preset = self.presets[preset]

        print ("recalled preset %s" % preset)

        for (layer, param_list) in enumerate(preset.get('shader_params',[])):
            if param_list:
                for param,value in enumerate(param_list):
                    self.pc.midi_input.call_method_name('set_the_shader_param_%s_layer_%s_continuous' % (param,layer), value)

        for (layer, slot) in enumerate(preset.get('selected_shader_slots',[])):
            if slot:
                print("setting layer %s to slot %s" % (layer, slot))
                self.pc.midi_input.call_method_name('play_shader_%s_%s' % (layer, slot))

        for (layer, active) in enumerate(preset.get('layer_active_status',[])):
            print ("got %s layer with status %s " % (layer,active))
            if active=='▶':
                self.pc.midi_input.call_method_name('start_shader_layer_%s' % layer)
            else:
                self.pc.midi_input.call_method_name('stop_shader_layer_%s' % layer)

        self.pc.data.feedback_active = preset.get('feedback_active',self.pc.data.feedback_active)