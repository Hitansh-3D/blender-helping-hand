# Blender Addon: Helping Hand
# This addon provides tools to quickly link object data, manage collections, and batch rename objects.

bl_info = {
    "name": "Helping Hand",
    "author": "HITANSH3D",
    "version": (0, 2, 3), # Patch fix: Updater logic and text cleanup
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Helping Hand",
    "description": "Tools for instancing, sorting, and batch renaming objects.",
    "warning": "",
    "doc_url": "https://github.com/Hitansh-3D/blender-helping-hand", # (Original doc link)
    "category": "Object",
}

import bpy
import re 
import json
import urllib.request
import addon_utils
from bpy.props import PointerProperty, EnumProperty, BoolProperty, StringProperty, IntProperty

# --- Constants ---
GITHUB_REPO_URL = "https://api.github.com/repos/Hitansh-3D/blender-helping-hand/releases/latest"
RELEASES_PAGE_URL = "https://github.com/Hitansh-3D/blender-helping-hand/releases"


# ------------------------------------------------------------------
# Caching System (for Instancing)
# ------------------------------------------------------------------
_name_cache = {}
_topo_cache = {}
_cached_obj_count = -1 

def invalidate_cache():
    global _name_cache, _topo_cache, _cached_obj_count
    _name_cache.clear()
    _topo_cache.clear()
    _cached_obj_count = -1
    print("Helping Hand: Cache invalidated.")

# ------------------------------------------------------------------
# Updater Logic (runs in the background)
# ------------------------------------------------------------------
def check_for_updates_callback():
    """
    This function runs in a timer, safely checking for updates in the background.
    It then calls an operator to update the UI, avoiding context errors.
    """
    try:
        with urllib.request.urlopen(GITHUB_REPO_URL, timeout=10) as url:
            data = json.loads(url.read().decode())
            
            latest_version_str = data['tag_name'].lstrip('v')
            latest_version_tuple = tuple(map(int, latest_version_str.split('.')))
            
            # Get the currently installed version from bl_info
            current_version_tuple = bl_info['version']

            if latest_version_tuple > current_version_tuple:
                bpy.ops.object.update_prefs_panel('INVOKE_DEFAULT', 
                    message="A new version is available!", # <-- Cleaned up message
                    latest_version=latest_version_str, 
                    show_button=True)
            else:
                bpy.ops.object.update_prefs_panel('INVOKE_DEFAULT', 
                    message="You have the latest version.", # <-- Cleaned up message
                    latest_version=latest_version_str, 
                    show_button=False)

    except Exception as e:
        error_message = f"Error: {e}. Check console."
        print(f"Helping Hand Update Error: {e}")
        bpy.ops.object.update_prefs_panel('INVOKE_DEFAULT', 
            message=error_message, 
            latest_version="Error", 
            show_button=False)
        
    return None

# ------------------------------------------------------------------
# Addon Preferences (for Updater)
# ------------------------------------------------------------------
class MyAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    latest_version: StringProperty(
        name="Latest Version", # <-- Cleaned up name
        default="Not Checked"
    )
    
    update_message: StringProperty(
        name="Update Message",
        default="Check for new updates."
    )
    
    show_update_button: BoolProperty(
        name="Show Update Button",
        default=False
    )
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        
        row = box.row()
        row.label(text=f"Current Addon: Helping Hand v{'.'.join(map(str, bl_info['version']))}")
        row = box.row()
        row.label(text=f"Latest Version: {self.latest_version}") # <-- Cleaned up label
        
        box.separator()
        
        row = box.row()
        row.operator("object.check_for_updates", text="Check for Updates", icon='WORLD')
        
        if self.show_update_button:
            box.operator("object.update_addon", text=f"Go to Download Page (v{self.latest_version})", icon='URL')
        
        box.label(text=self.update_message)
        
        box.separator()
        
        box.label(text="Need a previous version?")
        box.operator("object.rollback_update", text="Go to Releases Page", icon='RECOVER_LAST')

# ------------------------------------------------------------------
# Updater Operators
# ------------------------------------------------------------------
class MY_OT_UpdatePrefsPanel(bpy.types.Operator):
    """INTERNAL: Safely updates the addon preferences UI from a timer."""
    bl_idname = "object.update_prefs_panel"
    bl_label = "Update Preferences Panel"
    bl_options = {'INTERNAL'}

    message: StringProperty()
    latest_version: StringProperty()
    show_button: BoolProperty()

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        prefs.update_message = self.message
        prefs.latest_version = self.latest_version
        prefs.show_update_button = self.show_button
        return {'FINISHED'}

class MY_OT_CheckForUpdates(bpy.types.Operator):
    """Checks GitHub for the latest addon version"""
    bl_idname = "object.check_for_updates"
    bl_label = "Check for Updates"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        prefs.update_message = "Checking..."
        prefs.show_update_button = False
        bpy.app.timers.register(check_for_updates_callback)
        return {'FINISHED'}

class MY_OT_RollbackUpdate(bpy.types.Operator):
    """Opens the GitHub releases page to allow manual download of any version"""
    bl_idname = "object.rollback_update"
    bl_label = "Go to Releases Page"
    
    def execute(self, context):
        bpy.ops.wm.url_open(url=RELEASES_PAGE_URL)
        return {'FINISHED'}

class MY_OT_UpdateAddon(bpy.types.Operator):
    """Opens the GitHub releases page to download the latest version"""
    bl_idname = "object.update_addon"
    bl_label = "Go to Download Page"

    def execute(self, context):
        bpy.ops.wm.url_open(url=RELEASES_PAGE_URL)
        self.report({'INFO'}, "Opening GitHub releases page...")
        return {'FINISHED'}


# ------------------------------------------------------------------
# Core Addon Properties
# ------------------------------------------------------------------
class MyAddonProperties(bpy.types.PropertyGroup):
    # --- Instancing Properties ---
    target_collection: PointerProperty(name="Target Collection", type=bpy.types.Collection)
    selection_method: EnumProperty(
        name="Select by",
        items=[('NAME', "Name", "Select by base name"), ('TOPOLOGY', "Topology", "Select by mesh data")],
        default='NAME',
    )
    case_sensitive: BoolProperty(name="Case-Sensitive", default=False)
    
    # --- Renaming Properties ---
    rename_prefix: StringProperty(
        name="Prefix",
        description="Text to add to the beginning of the name",
        default="SM_"
    )
    rename_base_name: StringProperty(
        name="Base Name",
        description="The main part of the new name",
        default="Object"
    )
    rename_start_index: IntProperty(
        name="Start",
        description="The number to start counting from",
        default=1,
        min=0
    )
    rename_padding: IntProperty(
        name="Padding",
        description="Number of digits for the suffix (e.g., 2 for 01, 3 for 001)",
        default=2,
        min=1,
        max=4
    )

# ------------------------------------------------------------------
# Instancing Operators
# ------------------------------------------------------------------
class MY_OT_SelectSimilar(bpy.types.Operator):
    """Selects objects similar to the active one using a high-performance cache"""
    bl_idname = "object.select_similar"
    bl_label = "Select Similar Objects"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        global _name_cache, _topo_cache, _cached_obj_count
        if context.active_object and context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
            
        props = context.scene.my_addon_props
        active_obj = context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        
        view_layer_objects = context.view_layer.objects
        current_obj_count = len(view_layer_objects)
        
        if current_obj_count != _cached_obj_count:
            invalidate_cache()
            _cached_obj_count = current_obj_count
            
        mesh_objects = [obj for obj in view_layer_objects if obj.type == 'MESH']
        objects_to_select = []
        
        if props.selection_method == 'NAME':
            if not _name_cache:
                for obj in mesh_objects:
                    match = re.match(r"(.+?)(?:[\._-]\d+)?$", obj.name)
                    if match:
                        base_name = match.group(1).lower()
                        if base_name not in _name_cache: _name_cache[base_name] = []
                        _name_cache[base_name].append(obj)
            active_match = re.match(r"(.+?)(?:[\._-]\d+)?$", active_obj.name)
            if active_match:
                active_base_name = active_match.group(1)
                lookup_name = active_base_name if props.case_sensitive else active_base_name.lower()
                if props.case_sensitive:
                    potential_matches = _name_cache.get(lookup_name.lower(), [])
                    objects_to_select = [obj for obj in potential_matches if re.match(r"(.+?)(?:[\._-]\d+)?$", obj.name).group(1) == lookup_name]
                else:
                    objects_to_select = _name_cache.get(lookup_name, [])
        
        elif props.selection_method == 'TOPOLOGY':
            if not active_obj.data: return {'CANCELLED'}
            if not _topo_cache:
                for obj in mesh_objects:
                    if obj.data:
                        sig = (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons))
                        if sig not in _topo_cache: _topo_cache[sig] = []
                        _topo_cache[sig].append(obj)
            active_sig = (len(active_obj.data.vertices), len(active_obj.data.edges), len(active_obj.data.polygons))
            objects_to_select = _topo_cache.get(active_sig, [])
            
        if objects_to_select:
            for obj in objects_to_select: obj.select_set(True)
            
        context.view_layer.objects.active = active_obj
        self.report({'INFO'}, f"Selected {len(context.selected_objects)} similar objects.")
        return {'FINISHED'}

class MY_OT_LinkData(bpy.types.Operator):
    """Links the Object Data of all selected objects to the active one"""
    bl_idname = "object.link_data_custom"
    bl_label = "Link Selected Data"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context): return len(context.selected_objects) > 1
    
    def execute(self, context):
        bpy.ops.object.make_links_data(type='OBDATA')
        self.report({'INFO'}, f"Linked data for {len(context.selected_objects)} objects.")
        return {'FINISHED'}

class MY_OT_MoveToCollection(bpy.types.Operator):
    """Moves all selected objects to the target collection"""
    bl_idname = "object.move_to_collection_custom"
    bl_label = "Move to Collection"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        props = context.scene.my_addon_props
        return context.selected_objects and props.target_collection is not None
        
    def execute(self, context):
        props = context.scene.my_addon_props
        target_collection = props.target_collection
        selected_count = len(context.selected_objects)
        invalidate_cache()
        for obj in context.selected_objects:
            for coll in obj.users_collection: coll.objects.unlink(obj)
            target_collection.objects.link(obj)
        self.report({'INFO'}, f"Moved {selected_count} objects to '{target_collection.name}'.")
        return {'FINISHED'}

# ------------------------------------------------------------------
# Renaming Operator
# ------------------------------------------------------------------
class MY_OT_BatchRename(bpy.types.Operator):
    """Renames all selected objects using the specified format"""
    bl_idname = "object.batch_rename_custom"
    bl_label = "Batch Rename Selected"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.mode == 'OBJECT'
        
    def execute(self, context):
        props = context.scene.my_addon_props
        
        # Get selected objects and sort them by name to ensure predictable order
        selected_objs = sorted(context.selected_objects, key=lambda obj: obj.name)
        
        start_index = props.rename_start_index
        padding = props.rename_padding
        prefix = props.rename_prefix
        base_name = props.rename_base_name
        
        renamed_count = 0
        
        # --- First Pass: Rename to temporary names ---
        # This avoids conflicts where renaming A to B fails because B already exists.
        temp_name_prefix = "__HELPING_HAND_TEMP_RENAME_"
        for i, obj in enumerate(selected_objs):
            try:
                obj.name = f"{temp_name_prefix}{i}"
            except Exception as e:
                # This might happen if the object is weirdly linked or protected
                self.report({'WARNING'}, f"Could not rename '{obj.name}' to temp name. Skipping. Error: {e}")
        
        # --- Second Pass: Rename to final names ---
        # Now we iterate over the same list of objects (which have temp names)
        # and assign the final, correct names. No conflicts will occur.
        for i, obj in enumerate(selected_objs):
            # Only rename objects that we successfully renamed in the first pass
            if obj.name.startswith(temp_name_prefix):
                current_number = start_index + i
                suffix = f"_{current_number:0{padding}d}"
                new_name = f"{prefix}{base_name}{suffix}"
                
                # Set the new name
                obj.name = new_name
                renamed_count += 1
            
        self.report({'INFO'}, f"Renamed {renamed_count} objects.")
        return {'FINISHED'}

# ------------------------------------------------------------------
# Panels
# ------------------------------------------------------------------
class MY_PT_InstancingPanel(bpy.types.Panel):
    bl_label = "Instancing Tools"
    bl_idname = "MY_PT_instancing_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Helping Hand'
    bl_order = 0 # This panel comes first

    def draw(self, context):
        layout = self.layout
        props = context.scene.my_addon_props
        box = layout.box()
        box.label(text="1. Choose Target Collection:")
        box.prop(props, "target_collection", text="")
        box.separator()
        box.label(text="2. Auto-Select Objects:")
        row = box.row(align=True)
        row.prop(props, "selection_method", text="")
        row.operator(MY_OT_SelectSimilar.bl_idname, text="Select")
        if props.selection_method == 'NAME':
            box.prop(props, "case_sensitive")
        box.separator()
        box.label(text="3. Perform Actions (Confirm):")
        box.operator(MY_OT_LinkData.bl_idname)
        box.operator(MY_OT_MoveToCollection.bl_idname)

class MY_PT_RenamingPanel(bpy.types.Panel):
    bl_label = "Batch Renaming Tools"
    bl_idname = "MY_PT_renaming_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Helping Hand' # Same category to appear in the same tab
    bl_order = 1 # This panel comes second

    def draw(self, context):
        layout = self.layout
        props = context.scene.my_addon_props
        
        box = layout.box()
        box.label(text="1. Define New Name Format:")
        
        # Input for Prefix and Base Name
        row = box.row()
        row.prop(props, "rename_prefix", text="Prefix")
        row = box.row()
        row.prop(props, "rename_base_name", text="Base Name")
        
        # Input for Start Number and Padding
        row = box.row(align=True)
        row.prop(props, "rename_start_index", text="Start")
        row.prop(props, "rename_padding", text="Padding")
        
        box.separator()
        box.label(text="2. Run on Selected Objects:")
        
        # Example display
        example_num = f"{props.rename_start_index:0{props.rename_padding}d}"
        example_name = f"{props.rename_prefix}{props.rename_base_name}_{example_num}"
        layout.label(text=f"Example: {example_name}")
        
        # The button to execute the rename
        layout.operator(MY_OT_BatchRename.bl_idname, icon='SORTALPHA')

# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------
classes = (
    MyAddonProperties,
    MyAddonPreferences,
    MY_OT_UpdatePrefsPanel,
    MY_OT_CheckForUpdates,
    MY_OT_UpdateAddon,
    MY_OT_RollbackUpdate,
    MY_OT_SelectSimilar,
    MY_OT_LinkData,
    MY_OT_MoveToCollection,
    MY_OT_BatchRename,
    MY_PT_InstancingPanel,
    MY_PT_RenamingPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_addon_props = PointerProperty(type=MyAddonProperties)

def unregister():
    invalidate_cache()
    if bpy.app.timers.is_registered(check_for_updates_callback):
        bpy.app.timers.unregister(check_for_updates_callback)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_addon_props

if __name__ == "__main__":
    register()