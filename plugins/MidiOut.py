# TODO: this whole file + class !
# TODO: functionality --
# display screen + ui to configure INPUT MIDI DEVICE, LISTEN CCs, OUTPUT MIDI DEVICE, OUTPUT CCs,
# and mapping between [INPUT MIDI DEVICE, LISTEN CC] -> [OUTPUT MIDI DEVICE, OUTPUT CC]
# with binding in between !
# ALSO -- map from [ INTERNAL MODULATION ] -> [OUTPUT MIDI DEVICE, OUTPUT CC]
#   to do this use ModulationReceiverPlugin to receive modulation
#   this will allow control from LFOs etc!
# ++ mapping from [INPUT MIDI DEVICE, LISTEN CC] -> internal modulation [A|B|C|D]
# new actions to send midi messages directly from bindings eg send_midi_Skulpt_chan_1_cc_32
# QuickPreset/Automation looping
#   save state / replay state 
# ideas https://www.reddit.com/r/videosynthesis/comments/gma1ak/how_do_you_automate_midi_ccs/fr2tr3k/?context=3
#   Some features that came to my mind would be a precise beat-triggering, a sequencer mode over 16bars like the beatstep with rand mode, making recorded controls gapless by interpolating between end and start of the next sample, Scenes with a couple of sequenced controls, some LFO presets (Sin,Saw,Sq), a frequency-domain based control puuuh... And of course some kind of Raspi-Gui like recur... christmas tomorrow?
