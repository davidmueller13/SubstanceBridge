import bpy
import threading
import subprocess
import os
import SubstanceBridge


from bpy.props import StringProperty, BoolProperty
from SubstanceBridge.config.settings import SubstanceSettings

# ------------------------------------------------------------------------
# Create a class for a generic thread, else blender are block.
# ------------------------------------------------------------------------


class SubstancePainterThread(threading.Thread):

    def __init__(self, path_painter, path_project):
        threading.Thread.__init__(self)
        self.path_painter = path_painter
        self.path_project = path_project

    def run(self):
        mesh = SubstanceBridge.SubstanceVariable.tmp_mesh
        if self.path_project == "":
            popen = subprocess.call([self.path_painter, '--mesh', mesh])

        else:
            popen = subprocess.call([self.path_painter,
                                     '--mesh',
                                     mesh,
                                     self.path_project])

# ------------------------------------------------------------------------
# Function to create an Obj, and export to painter
# ------------------------------------------------------------------------


class SendToPainter(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.painter_export"
    bl_label = "Send mesh to painter export"

    project = BoolProperty(name="It's a new project.")

    painter = StringProperty(name="Path Substance Painter")

    update = BoolProperty(
        default=False,
        name="Variable de test, update or not"
        )

    path_project = StringProperty(name="Path Substance project")

    def execute(self, context):
        obj = bpy.context.active_object
        mesh = SubstanceBridge.SubstanceVariable.tmp_mesh

        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons["SubstanceBridge"].preferences
        self.painter = str(addon_prefs.painterpath)

        if obj.type == 'MESH':
            obj_mesh = bpy.data.objects[obj.name].data
            if obj_mesh.uv_textures:
                # Export du mesh selectionne
                bpy.ops.export_scene.obj(filepath=mesh,
                                         use_selection=True,
                                         path_mode='AUTO')

                # Verification si le soft est configuré dans le path
                if self.painter:
                    path_sppfile = os.path.abspath(bpy.context.scene.sppfile)
                    # Test If it's a new project.
                    if self.project is True:
                        self.path_project = path_sppfile

                    else:
                        self.path_project = ""

                    launchpainter = SubstancePainterThread(self.painter,
                                                           self.path_project)
                    launchpainter.start()
                else:
                    self.report({'WARNING'},
                                "No path configured, setup into User Pre.")
                    return {'CANCELLED'}

            else:
                self.report({'WARNING'},
                            "This object don't containt a UV layers.")
                return {'CANCELLED'}

        else:
            self.report({'WARNING'}, "This object is not a mesh.")
            return {'CANCELLED'}

        return {'FINISHED'}


# ------------------------------------------------------------------------
# Function Name Project
# ------------------------------------------------------------------------
class ProjectName(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "painter.substance_name"
    bl_label = "Create a new Substance Painter project"

    def execute(self, context):
        scn = context.scene
        slct_obj = bpy.context.selected_objects

        for obj in slct_obj:
            obj['substance_project'] = scn.project_name

        return {'FINISHED'}


# ------------------------------------------------------------------------
# Function Selected Project
# ------------------------------------------------------------------------
class SelectedProject(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "painter.selected_project"
    bl_label = "Selected mesh with this project"

    def execute(self, context):
        scn = context.scene
        all_obj = bpy.data.objects

        for obj in all_obj:
            if obj.get('substance_project') is not None:
                name_obj = bpy.data.objects[obj.name]
                name_prj = bpy.data.objects[obj.name]['substance_project']

                print("02 - If Substance project")
                print(name_obj.name, "<>", name_prj)

                if name_prj == scn.project_name:
                    # Selection object with a substance name.
                    name_obj.select = True
                    print("03 - Name = field")

                else:
                    name_obj.select = False

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SendToPainter)
    bpy.utils.register_class(ProjectName)
    bpy.utils.register_class(SelectedProject)


def unregister():
    bpy.utils.unregister_class(SendToPainter)
    bpy.utils.unregister_class(ProjectName)
    bpy.utils.unregister_class(SelectedProject)
