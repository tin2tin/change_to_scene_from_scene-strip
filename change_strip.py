# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Scene Change via Scene Strip",
    "author": "tintwotin",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "The Context Menu in the Sequencer or shortcut: Shift + Tab",
    "description": "Opens the scene from the scene strip and returns to previous scene if no Scene Stip is the active strip",
    "warning": "",
    "wiki_url": "",
    "category": "Sequencer",
}

import bpy
from bpy.types import Operator

def act_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return False

class values():
    prev_scene_change = ""

class SEQUENCER_OT_scene_change(bpy.types.Operator):
    """Change scene to active strip scene"""
    bl_idname = "sequencer.change_scene"
    bl_label = "Scene Change"
    bl_description = "Change scene to active strip scene"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if context.scene:
            return True
        else:
            return False

    def execute(self, context):
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()
        strip = act_strip(context)
        scene = bpy.context.scene
        sequence = scene.sequence_editor
        
        if strip != None:                                                               # save camera
            if strip.type == "SCENE":
                if sequence.sequences_all[strip.name].scene_input == 'CAMERA' and strip.scene_camera!=None:
                    camera = strip.scene_camera.name 
                         
        if strip == None:                                                               # no active strip
            if values.prev_scene_change !="":                                           # a previous scene - go back
                win = bpy.context.window_manager.windows[0]
                win.scene = bpy.data.scenes[values.prev_scene_change]
                return {"FINISHED"} 
            elif values.prev_scene_change =="":                                         # no previous - do nothing
                return {"FINISHED"}
            
        else:                                                                           # an active strip exists
            
            if strip.type != "SCENE" and values.prev_scene_change !="":                 # wrong strip type, but a previous scene - go back
                win = bpy.context.window_manager.windows[0]
                win.scene = bpy.data.scenes[values.prev_scene_change] 
                        
            elif strip.type == "SCENE":                                                 # correct strip type              
                strip_scene = bpy.context.scene.sequence_editor.active_strip.scene.name
                values.prev_scene_change = scene.name
                
                                                                                        # scene strip in 'Camera' and a camera is selected
                        
                if sequence.sequences_all[strip.name].scene_input == 'CAMERA' and strip.scene_camera!=None: 
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            win = bpy.context.window_manager.windows[0]
                            win.scene = bpy.data.scenes[strip_scene]
                            bpy.context.scene.camera = bpy.data.objects[camera]         # select camera as view
                            area.spaces.active.region_3d.view_perspective = 'CAMERA'    # use camera view  
                                                     
                else:                                                                   # no scene strip in 'Camera' mode or a camera may not be selected

                    strip_scene = bpy.context.scene.sequence_editor.active_strip.scene.name
                    values.prev_scene_change = scene.name
                    win = bpy.context.window_manager.windows[0]
                    win.scene = bpy.data.scenes[strip_scene] 
                                 
        return {"FINISHED"}

def menu_func(self, context):
    self.layout.operator("sequencer.change_scene")

addon_keymaps = []

def register():
    bpy.utils.register_class(SEQUENCER_OT_scene_change)  
    bpy.types.SEQUENCER_MT_context_menu.append(menu_func)
    
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Scene Change', space_type='SEQUENCE_EDITOR')
    kmi = km.keymap_items.new(SEQUENCER_OT_scene_change.bl_idname, 'TAB', 'PRESS', ctrl=False, shift=True)
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_scene_change)
    bpy.types.SEQUENCER_MT_context_menu.remove(menu_func)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear() 
#register()
#unregister()
