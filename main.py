import maya.cmds as cmds
import maya.mel as mel
import string



#PURPOSE     Tag the given node with the
#            origin attribute and set to true
#PROCEDURE    if the object exists, and the attribute
#            does not exist, add the origin bool attribute and
#            set to true
#PRESUMPTION none
def SIP_TagForOrigin(node):
    if cmds.objExists(node)and not cmds.objExists(node + ".origin"):
        cmds.addAttr(node, shortName = "org", longName = "origin", at = "bool")
        cmds.setAttr(node + ".origin", True)

#PURPOSE        add attributes to the mesh so exporter can find them
#PROCEDURE        if object exists, and the attribute does not, add
#                exportMeshes message attribute
#PRESUMPTION    none
def SIP_TagForMeshExport(mesh):
    if cmds.objExists(mesh) and not cmds.objExists(mesh + ".exportMeshes"):
        cmds.addAttr(mesh, shortName = "xms", longName = "exportMeshes", at = "message")
        




#PURPOSE     add attribute to the node so exporter can find export definitions
#PROCEDURE    if the object exists, and the attribute
#            does not exist, add the exportNode message attribute
#PRESUMPTION none
def SIP_TagForExportNode(node):
    if cmds.objExists(node) and not cmds.objExists(node + ".exportNode"):
        cmds.addAttr(node, shortName = "xnd", longName = "exportNode", at = "message")
        

        

#PURPOSE         Return the origin of the given namespace
#PROCEDURE       If ns is not empty string, list all joints with
#                the matching namespace, else list all joints
#                for list of joints, look for origin attribute and if
#                it is set to true. If found, return name of joint, else
#                return "Error"
#PRESUMPTIONS    Origin attribute it on a joint
#                "Error" is not a valid joint name
#                namespace does not include colon
def SIP_ReturnOrigin(ns):
    
    joints = []
    
    if ns:
        joints = cmds.ls((ns + ":*"), type = "joint")
    else:
        joints = cmds.ls(type = "joint")
        
    if len(joints):
        for curJoint in joints:
            if cmds.objExists(curJoint + ".origin") and cmds.getAttr(curJoint + ".origin"):
                return curJoint
                
    return "Error"

#PRUPOSE        delete given export node
#PROCEDURE      if object exists, delete  
#PRESUMPTIONS   node
def SIP_DeleteFBXExportNode(exportNode):             
    if cmds.objExists(exportNode):
        cmds.delete
        




