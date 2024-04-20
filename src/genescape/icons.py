"""
An exploratory module with the goal of avoid dependency on faicons package.

TODO: not fully implemented.
"""
import pickle
from faicons import icon_svg

# Load default icons
icon_play = icon_svg("play")
icon_down = icon_svg("download")
icon_zoom_in = icon_svg("magnifying-glass-plus")
icon_zoom_out = icon_svg("magnifying-glass-minus")
zoom_reset = icon_svg("magnifying-glass")

def pack():
    icon_play_val=b'\x80\x04\x95C\x02\x00\x00\x00\x00\x00\x00\x8c\x0fhtmltools._core\x94\x8c\x03Tag\x94\x93\x94)\x81\x94}\x94(\x8c\x04name\x94\x8c\x03svg\x94\x8c\x06add_ws\x94\x89\x8c\x05attrs\x94h\x00\x8c\x0bTagAttrDict\x94\x93\x94)\x81\x94(\x8c\x07viewBox\x94\x8c\x0b0 0 384 512\x94\x8c\x13preserveAspectRatio\x94\x8c\x04none\x94\x8c\x0baria-hidden\x94\x8c\x04true\x94\x8c\x04role\x94\x8c\x03img\x94\x8c\x05class\x94\x8c\x02fa\x94\x8c\x05style\x94\x8c\x89fill:currentColor;height:1em;width:0.75em;margin-left:auto;margin-right:0.2em;position:relative;vertical-align:-0.125em;overflow:visible;\x94u\x8c\x08children\x94h\x00\x8c\x07TagList\x94\x93\x94)\x81\x94h\x02)\x81\x94}\x94(h\x05\x8c\x04path\x94h\x07\x88h\x08h\n)\x81\x94\x8c\x01d\x94\x8c\x92M73 39c-14.8-9.1-33.4-9.4-48.5-.9S0 62.6 0 80V432c0 17.4 9.4 33.4 24.5 41.9s33.7 8.1 48.5-.9L361 297c14.3-8.7 23-24.2 23-41s-8.7-32.2-23-41L73 39z\x94sh\x18h\x1a)\x81\x94\x8c\x10prev_displayhook\x94Nubah#Nub.'
    icon_down_val=b'\x80\x04\x95i\x03\x00\x00\x00\x00\x00\x00\x8c\x0fhtmltools._core\x94\x8c\x03Tag\x94\x93\x94)\x81\x94}\x94(\x8c\x04name\x94\x8c\x03svg\x94\x8c\x06add_ws\x94\x89\x8c\x05attrs\x94h\x00\x8c\x0bTagAttrDict\x94\x93\x94)\x81\x94(\x8c\x07viewBox\x94\x8c\x0b0 0 512 512\x94\x8c\x13preserveAspectRatio\x94\x8c\x04none\x94\x8c\x0baria-hidden\x94\x8c\x04true\x94\x8c\x04role\x94\x8c\x03img\x94\x8c\x05class\x94\x8c\x02fa\x94\x8c\x05style\x94\x8c\x88fill:currentColor;height:1em;width:1.0em;margin-left:auto;margin-right:0.2em;position:relative;vertical-align:-0.125em;overflow:visible;\x94u\x8c\x08children\x94h\x00\x8c\x07TagList\x94\x93\x94)\x81\x94h\x02)\x81\x94}\x94(h\x05\x8c\x04path\x94h\x07\x88h\x08h\n)\x81\x94\x8c\x01d\x94X\xb6\x01\x00\x00M288 32c0-17.7-14.3-32-32-32s-32 14.3-32 32V274.7l-73.4-73.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l128 128c12.5 12.5 32.8 12.5 45.3 0l128-128c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L288 274.7V32zM64 352c-35.3 0-64 28.7-64 64v32c0 35.3 28.7 64 64 64H448c35.3 0 64-28.7 64-64V416c0-35.3-28.7-64-64-64H346.5l-45.3 45.3c-25 25-65.5 25-90.5 0L165.5 352H64zM432 456c-13.3 0-24-10.7-24-24s10.7-24 24-24s24 10.7 24 24s-10.7 24-24 24z\x94sh\x18h\x1a)\x81\x94\x8c\x10prev_displayhook\x94Nubah#Nub.'
    icon_zoom_in_val=b'\x80\x04\x95\x1e\x03\x00\x00\x00\x00\x00\x00\x8c\x0fhtmltools._core\x94\x8c\x03Tag\x94\x93\x94)\x81\x94}\x94(\x8c\x04name\x94\x8c\x03svg\x94\x8c\x06add_ws\x94\x89\x8c\x05attrs\x94h\x00\x8c\x0bTagAttrDict\x94\x93\x94)\x81\x94(\x8c\x07viewBox\x94\x8c\x0b0 0 512 512\x94\x8c\x13preserveAspectRatio\x94\x8c\x04none\x94\x8c\x0baria-hidden\x94\x8c\x04true\x94\x8c\x04role\x94\x8c\x03img\x94\x8c\x05class\x94\x8c\x02fa\x94\x8c\x05style\x94\x8c\x88fill:currentColor;height:1em;width:1.0em;margin-left:auto;margin-right:0.2em;position:relative;vertical-align:-0.125em;overflow:visible;\x94u\x8c\x08children\x94h\x00\x8c\x07TagList\x94\x93\x94)\x81\x94h\x02)\x81\x94}\x94(h\x05\x8c\x04path\x94h\x07\x88h\x08h\n)\x81\x94\x8c\x01d\x94Xk\x01\x00\x00M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM184 296c0 13.3 10.7 24 24 24s24-10.7 24-24V232h64c13.3 0 24-10.7 24-24s-10.7-24-24-24H232V120c0-13.3-10.7-24-24-24s-24 10.7-24 24v64H120c-13.3 0-24 10.7-24 24s10.7 24 24 24h64v64z\x94sh\x18h\x1a)\x81\x94\x8c\x10prev_displayhook\x94Nubah#Nub.'
    icon_zoom_out_val=b'\x80\x04\x95\xc3\x02\x00\x00\x00\x00\x00\x00\x8c\x0fhtmltools._core\x94\x8c\x03Tag\x94\x93\x94)\x81\x94}\x94(\x8c\x04name\x94\x8c\x03svg\x94\x8c\x06add_ws\x94\x89\x8c\x05attrs\x94h\x00\x8c\x0bTagAttrDict\x94\x93\x94)\x81\x94(\x8c\x07viewBox\x94\x8c\x0b0 0 512 512\x94\x8c\x13preserveAspectRatio\x94\x8c\x04none\x94\x8c\x0baria-hidden\x94\x8c\x04true\x94\x8c\x04role\x94\x8c\x03img\x94\x8c\x05class\x94\x8c\x02fa\x94\x8c\x05style\x94\x8c\x88fill:currentColor;height:1em;width:1.0em;margin-left:auto;margin-right:0.2em;position:relative;vertical-align:-0.125em;overflow:visible;\x94u\x8c\x08children\x94h\x00\x8c\x07TagList\x94\x93\x94)\x81\x94h\x02)\x81\x94}\x94(h\x05\x8c\x04path\x94h\x07\x88h\x08h\n)\x81\x94\x8c\x01d\x94X\x10\x01\x00\x00M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM136 184c-13.3 0-24 10.7-24 24s10.7 24 24 24H280c13.3 0 24-10.7 24-24s-10.7-24-24-24H136z\x94sh\x18h\x1a)\x81\x94\x8c\x10prev_displayhook\x94Nubah#Nub.'
    zoom_reset_val=b'\x80\x04\x95\xbe\x02\x00\x00\x00\x00\x00\x00\x8c\x0fhtmltools._core\x94\x8c\x03Tag\x94\x93\x94)\x81\x94}\x94(\x8c\x04name\x94\x8c\x03svg\x94\x8c\x06add_ws\x94\x89\x8c\x05attrs\x94h\x00\x8c\x0bTagAttrDict\x94\x93\x94)\x81\x94(\x8c\x07viewBox\x94\x8c\x0b0 0 512 512\x94\x8c\x13preserveAspectRatio\x94\x8c\x04none\x94\x8c\x0baria-hidden\x94\x8c\x04true\x94\x8c\x04role\x94\x8c\x03img\x94\x8c\x05class\x94\x8c\x02fa\x94\x8c\x05style\x94\x8c\x88fill:currentColor;height:1em;width:1.0em;margin-left:auto;margin-right:0.2em;position:relative;vertical-align:-0.125em;overflow:visible;\x94u\x8c\x08children\x94h\x00\x8c\x07TagList\x94\x93\x94)\x81\x94h\x02)\x81\x94}\x94(h\x05\x8c\x04path\x94h\x07\x88h\x08h\n)\x81\x94\x8c\x01d\x94X\x0b\x01\x00\x00M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352c79.5 0 144-64.5 144-144s-64.5-144-144-144S64 128.5 64 208s64.5 144 144 144z\x94sh\x18h\x1a)\x81\x94\x8c\x10prev_displayhook\x94Nubah#Nub.'

    # Unpack the icons
    icon_play = pickle.loads(icon_play_val)
    icon_down = pickle.loads(icon_down_val)
    icon_zoom_in = pickle.loads(icon_zoom_in_val)
    icon_zoom_out = pickle.loads(icon_zoom_out_val)
    zoom_reset = pickle.loads(zoom_reset_val)

def generate():
    icons = [('icon_play', icon_play),
             ('icon_down', icon_down),
             ('icon_zoom_in', icon_zoom_in),
             ('icon_zoom_out', icon_zoom_out),
             ('zoom_reset', zoom_reset)]

    for name, icon in icons:
        out = pickle.dumps(icon)

        print(f'{name}={out}')
def show():
    icons = [('icon_play', icon_play),
             ('icon_down', icon_down),
             ('icon_zoom_in', icon_zoom_in),
             ('icon_zoom_out', icon_zoom_out),
             ('zoom_reset', zoom_reset)]

    for name, icon in icons:
        obj = pickle.loads(icon)
        print (name, type(obj), obj)

if __name__ == '__main__':
    #generate()
    show()
