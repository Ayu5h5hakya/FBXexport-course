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

    
#PURPOSE          Return the meshes connected to blendshape nodes
#PROCEDURE        Get a list of blendshape nodes
#                 Follow those connections to the mesh shape node
#                 Traverse up the hierarchy to find parent transform node
#PRESUMPTIONS     character has a valid namespace, namespace does not have colon
#                 only exporting polygonal meshes
def SIP_FindMeshesWithBlendshapes(ns):
    
    returnArray = []
    
    blendshapes = cmds.ls((ns + ":*" ), type = "blendShape")
    
    for curBlendShape in blendshapes:
        downstreamNodes = cmds.listHistory(curBlendShape, future = True)
        for curNode in downstreamNodes:
            if cmds.objectType(curNode, isType = "mesh"):
                parents = cmds.listRelatives(curNode, parent = True)
                returnArray.append(parents[0])
    
    return returnArray

#PURPOSE        Connect the fbx export node to the origin
#PROCEDURE      check if attribute exist and nodes are valid
#               if they are, connect attributes
#PRESUMPTIONS   none
def SIP_ConnectFBXExportNodeToOrigin(exportNode, origin):

    if cmds.objExists(origin) and cmds.objExists(exportNode):
        
        if not cmds.objExists(origin + ".exportNode"):
            SIP_TagForExportNode(origin)
            
        if not cmds.objExists(exportNode + ".exportNode"):
            SIP_AddFBXNodeAttrs(fbxExportNode)
            
        cmds.connectAttr(origin + ".exportNode", exportNode + ".exportNode")    
            


#PURPOSE      To connect meshes to the export node so the exporter can find them          
#PROCEDURE    check to make sure meshes and exportNode is valid, check for attribute "exportMeshes"
#             if no attribute, add it. then connect attributes
#PRESUMPTION  exportNode is a exportNode, and meshes is a list of transform nodes for polygon meshes
def SIP_ConnectFBXExportNodeToMeshes(exportNode, meshes):

    if cmds.objExists(exportNode):
        if not cmds.objExists(exportNode + ".exportMeshes"):
            SIP_AddFBXNodeAttrs(exportNode)
        for curMesh in meshes:
		    if cmds.objExists(curMesh):
				if not cmds.objExists(curMesh + ".exportMeshes"):
					SIP_TagForMeshExport(curMesh)
				cmds.connectAttr(exportNode + ".exportMeshes", curMesh + ".exportMeshes", force = True)
            






#PURPOSE      to disconnect the message attribute between export node and mesh          
#PROCEDURE    iterate through list of meshes and if mesh exists, disconnect
#PRESUMPTION  that node and mesh are connected via exportMeshes message attr
def SIP_DisconnectFBXExportNodeToMeshes(exportNode, meshes):
    
    if cmds.objExists(exportNode):
        for curMesh in meshes:
            if cmds.objExists(curMesh):
                cmds.disconnectAttr(exportNode + ".exportMeshes", curMesh + ".exportMeshes")
                



                
                

#PURPOSE        return a list of all meshes connected to the export node
#PROCEDURE      listConnections to exportMeshes attribute
#PRESUMPTION    exportMeshes attribute is used to connect to export meshes, exportMeshes is valid
def SIP_ReturnConnectedMeshes(exportNode):
    meshes = cmds.listConnections((exportNode + ".exportMeshes"), source = False, destination = True)
    return meshes        


#PURPOSE        
#PROCEDURE
#PRESUMPTIONS
def SIP_UnlockJointTransforms(root):
    hierarchy = cmds.listRelatives(root, ad=True, f=True)
    
    hierarchy.append(root)
    
    for cur in hierarchy:
		cmds.setAttr( (cur + '.translateX'), lock=False )
		cmds.setAttr( (cur + '.translateY'), lock=False )
		cmds.setAttr( (cur + '.translateZ'), lock=False )
		cmds.setAttr( (cur + '.rotateX'), lock=False )
		cmds.setAttr( (cur + '.rotateY'), lock=False )
		cmds.setAttr( (cur + '.rotateZ'), lock=False )
		cmds.setAttr( (cur + '.scaleX'), lock=False )
		cmds.setAttr( (cur + '.scaleY'), lock=False )
		cmds.setAttr( (cur + '.scaleZ'), lock=False )





#PURPOSE        to connect given node to other given node via specified transform
#PROCEDURE      call connectAttr
#PRESUMPTIONS   assume two nodes exist and transform type is valid
def SIP_ConnectAttrs(sourceNode, destNode, transform):
    cmds.connectAttr(sourceNode + "." + transform + "X", destNode + "." + transform + "X")
    cmds.connectAttr(sourceNode + "." + transform + "Y", destNode + "." + transform + "Y")
    cmds.connectAttr(sourceNode + "." + transform + "Z", destNode + "." + transform + "Z")







#PURPOSE        To copy the bind skeleton and connect the copy to the original bind
#PROCEDURE      duplicate hierarchy
#               delete everything that is not a joint
#               unlock all the joints
#               connect the translates, rotates, and scales
#               parent copy to the world 
#               add deleteMe attr 
#PRESUMPTIONS   No joints are children of anything but other joints
def SIP_CopyAndConnectSkeleton(origin):
    newHierarchy=[]
    
    if origin != "Error" and cmds.objExists(origin):
        dupHierarchy = cmds.duplicate(origin)
        tempHierarchy = cmds.listRelatives(dupHierarchy[0], allDescendents=True, f=True)

        for cur in tempHierarchy:
            if cmds.objExists(cur):
                if cmds.objectType(cur) != "joint":
                    cmds.delete(cur)

        SIP_UnlockJointTransforms(dupHierarchy[0])
  
       
        origHierarchy = cmds.listRelatives(origin, ad=True, type = "joint")
        newHierarchy = cmds.listRelatives(dupHierarchy[0], ad=True, type = "joint")

        
        origHierarchy.append(origin)
        newHierarchy.append(dupHierarchy[0])
        

        
        for index in range(len(origHierarchy)):
        	SIP_ConnectAttrs(origHierarchy[index], newHierarchy[index], "translate")
        	SIP_ConnectAttrs(origHierarchy[index], newHierarchy[index], "rotate")
        	SIP_ConnectAttrs(origHierarchy[index], newHierarchy[index], "scale")
        	
        cmds.parent(dupHierarchy[0], world = True)
        SIP_TagForGarbage(dupHierarchy[0])
        
    return newHierarchy





#PURPOSE        Translate export skeleton to origin. May or may not kill origin animation depending on input
#PROCEDURE      bake the animation onto our origin
#               create an animLayer
#               animLayer will either be additive or overrride depending on parameter we pass
#               add deleteMe attr to animLayer
#               move to origin
#PRESUMPTIONS   origin is valid, end frame is greater than start frame, zeroOrigin is boolean
def SIP_TransformToOrigin(origin, startFrame, endFrame, zeroOrigin):
    cmds.bakeResults(origin, t = (startFrame, endFrame), at= ["rx","ry","rz","tx","ty","tz","sx","sy","sz"], hi="none")
    
    cmds.select(clear = True)
    cmds.select(origin)
    
    newNaimLayer = ""
    
    if zeroOrigin:
        #kills origin animation 
        newAnimLayer = cmds.animLayer(aso=True, mute = False, solo = False, override = True, passthrough = True, lock = False)
        cmds.setAttr (newAnimLayer + ".rotationAccumulationMode", 0)
        cmds.setAttr (newAnimLayer + ".scaleAccumulationMode", 1)
    else:
        #shifts origin animation 
        newAnimLayer = cmds.animLayer(aso=True, mute = False, solo = False, override = False, passthrough = False, lock = False)
        
    SIP_TagForGarbage(newAnimLayer)
    
    #turn anim layer on
    cmds.animLayer(newAnimLayer, edit = True, weight = 1)
    cmds.setKeyframe(newAnimLayer + ".weight")
    
    #move origin animation to world origin
    cmds.setAttr(origin + ".translate", 0,0,0)
    cmds.setAttr(origin + ".rotate", 0,0,0)
    cmds.setKeyframe(origin, al=newAnimLayer, t=startFrame)    

    






