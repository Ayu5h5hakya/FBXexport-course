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
        



#PURPOSE        to add the attribute to the export node to store our
#                export settings
#PROCEDURE       for each attribute we want to add, check if it exists
#                if it doesn't exist, add
#PRESUMPTIONS    assume fbxExportNode is a valid object
def SIP_AddFBXNodeAttrs(fbxExportNode):
	
	if not cmds.attributeQuery("export", node=fbxExportNode, exists=True):
		cmds.addAttr(fbxExportNode, longName='export', at="bool")
	
	if not cmds.attributeQuery("moveToOrigin", node=fbxExportNode, exists=True):
		cmds.addAttr(fbxExportNode, longName='moveToOrigin', at="bool")
		
	if not cmds.attributeQuery("zeroOrigin", node=fbxExportNode, exists=True):
		cmds.addAttr(fbxExportNode, longName='zeroOrigin', at="bool")

	if not cmds.attributeQuery("exportName", node=fbxExportNode, exists=True):					   
		cmds.addAttr(fbxExportNode, longName='exportName', dt="string")
	
	if not cmds.attributeQuery("useSubRange", node=fbxExportNode, exists=True):		
		cmds.addAttr(fbxExportNode, longName='useSubRange', at="bool")
	
	if not cmds.attributeQuery("startFrame", node=fbxExportNode, exists=True):	  
		cmds.addAttr(fbxExportNode, longName='startFrame', at="float")
	
	if not cmds.attributeQuery("endFrame", node=fbxExportNode, exists=True):			  
		cmds.addAttr(fbxExportNode, longName='endFrame', at="float")
		
	if not cmds.attributeQuery("exportMeshes", node=fbxExportNode, exists=True):	
		cmds.addAttr(fbxExportNode, longName='exportMeshes', at="message")
		
	if not cmds.attributeQuery("exportNode", node=fbxExportNode, exists=True):		  
		cmds.addAttr(fbxExportNode, longName='exportNode', at="message")	
		
	if not cmds.attributeQuery("animLayers", node=fbxExportNode, exists=True):					   
		cmds.addAttr(fbxExportNode, longName='animLayers', dt="string")
		
		




#PURPOSE          create the export node to store our export settings
#PROCEDURE        create an empty transform node
#                 we will send it to SIP_AddFBXNodeAttrs to add the needed attributes
#PRESUMPTION      none
def SIP_CreateFBXExportNode(characterName):
    fbxExportNode = cmds.group(em = True, name = characterName + "FBXExportNode#")
    SIP_AddFBXNodeAttrs(fbxExportNode)
    cmds.setAttr(fbxExportNode + ".export", 1)
    return fbxExportNode


#PURPOSE      Removes all nodes taged as garbage
#PROCEDURE    List all transforms in the scene
#             Itterate through list, anything with "deleteMe" attribute
#             will be deleted
#PRESUMPTIONS The deleteMe attribute is name of the attribute signifying garbage
def SIP_ClearGarbage():
    list = cmds.ls(tr=True)
    
    for cur in list:
        if cmds.objExists(cur + ".deleteMe"):
            cmds.delete(cur)


#PURPOSE        Tag object for being garbage
#PROCEDURE      If node is valid object and attribute does not exists, add deleteMe attribute
#PRESUMPTIONS   None
def SIP_TagForGarbage(node):    
    if cmds.objExists(node)and not cmds.objExists(node + ".deleteMe"):
        cmds.addAttr(node, shortName = "del", longName = "deleteMe", at = "bool")
        cmds.setAttr(node + ".deleteMe", True)    

    
    