import maya.cmds as cmds
import maya.mel as mel
import string

mel.eval("source SIP_FBXAnimationExporter_FBXOptions.mel")

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

    


#PURPOSE        Record the animLayer settings used in animation and store in 
#               the exportNode as a string
#PROCEDURE      List all the animLayers. Query their mute and solo attributes.
#               List them in one single string
#               Uses ; as sentinal value to split seperate animLayers
#               Uses , as sentinal value to split seperate fields for animLayer
#               Uses = as sentinal value to split seperate attrs from thier values in field
#PRESUMPTION    None
def SIP_SetAnimLayerSettings(exportNode):
 
    if not cmds.attributeQuery("animLayers", node=exportNode, exists=True):					   
        SIP_AddFBXNodeAttrs(exportNode)	
    
    animLayers = cmds.ls(type = "animLayer")
    
    animLayerCommandStr = ""
    
    for curLayer in animLayer:
        mute = cmds.animLayer(curLayer, query = True, mute = True)
        solo = cmds.animLayer(curLayer, query = True, solo = True)
        animLayerCommandStr += (curLayer + ", mute = " + str(mute) + ", solo = " + str(solo) + ";")
        
    cmds.setAttr(exportNode + ".animLayers", animLayerCommandStr, type = "string")    
    




#PURPOSE        Set the animLayers based on the string value in the exportNode
#PROCEDURE      Use pre-defined sentinal values to split the string for seperate animLayers
#               And parse out the attributes and their values, then set
#PRESUMPTION    Uses ; as sentinal value to split seperate animLayers
#               Uses , as sentinal value to split seperate fields for animLayer
#               Uses = as sentinal value to split seperate attrs from thier values in field
#               order is Layer, mute, solo
def SIP_SetAnimLayersFromSettings(exportNode):
    
    if cmds.objExists(exportNode)and cmds.objExists(exportNode + ".animLayers"):
        animLayersRootString = cmds.getAttr(exportNode + ".animLayers", asString = True)
        
        if animLayersRootString:
            animLayerEntries = animLayersRootString.split(";")
            
            for curEntry in animLayerEntries:
                if curEntry:
                    fields = curEntry.split(",")
                    
                    animLayerField = fields[0]
                    curMuteField = fields[1]
                    curSoloField = fields[2]
                    
                    muteFieldStr = curMuteField.split(" = ")
                    soloFieldStr = curMuteField.split(" = ")
                    
                    #convert strings to bool values
                    muteFieldBool = True
                    soloFieldBool = True
                    
                    if muteFieldStr[1] != "True":
                        muteFieldBool = False                                        
    
                    if soloFieldStr[1] != "True":
                        soloFieldBool = False
                        
                    cmds.animLayer(animLayerField, edit = True, mute = muteFieldBool, solo = soloFieldBool)      
    
    




    
def SIP_ClearAnimLayerSettings(exportNode):
    cmds.setAttr(exportNode + ".animLayers", "", type = "string")



def SIP_ExportFBX(exportNode):
    curWorkspace = cmds.workspace(q=True, rd=True)
    fileName = cmds.getAttr(exportNode + ".exportName")
    
    if fileName:
        newFBX = curWorkspace + fileName
        cmds.file(newFBX, force = True, type = 'FBX export', pr=True, es=True)
    else:
        cmds.warning("No Valid Export Filename for Export Node " + exportNode + "\n")











def SIP_ExportFBXAnimation(characterName, exportNode):

    SIP_ClearGarbage()
    characters = []
    
    if characterName:
        characters.append(characterName)
    else:
        reference = cmd.file(reference=1, query = True)
        for curRef in references:
            characters.append(cmds.file(curRef, namespace = 1, query = True))
            
    for curCharacter in characters:
        
        #get meshes with blendshapes
        meshes = SIP_FindMeshesWithBlendshapes(curCharacter)
        
        #get origin
        origin = SIP_ReturnOrigin(curCharacter)
        
        exportNodes = []
        
        if exportNode:
            exportNodes.append(exportNode)
        else:
            exportNodes = SIP_ReturnFBXExportNodes(origin)
            
        
        for curExportNode in exportNodes:
            if cmds.getAttr(curExportNode + ".export") and origin != "Error":
                exportRig = SIP_CopyAndConnectSkeleton(origin)
                
                startFrame = cmds.playbackOptions(query=True, minTime=1)
                endFrame = cmds.playbackOptions(query=True, maxTime=1)

                subAnimCheck = cmds.getAttr(curExportNode + ".useSubRange")
                
                if subAnimCheck:
                    startFrame = cmds.getAttr(curExportNode + ".startFrame")
                    endFrame = cmds.getAttr(curExportNode + ".endFrame")
                    
                if cmds.getAttr(curExportNode + ".moveToOrigin"):
                    newOrigin = cmds.listConnections(origin + ".translateX", source = False, d = True)
                    zeroOriginFlag = cmds.getAttr(curExportNode + ".zerOrigin")
                    SIP_TransformToOrigin(newOrigin[0], startFrame, endFrame, zeroOriginFlag)

                cmds.select(clear = True)
                cmds.select(exportRig, add=True)
                cmds.select(meshes, add=True)
                
                SIP_SetAnimLayersFromSettings(curExportNode)
                
                mel.eval("SIP_SetFBXExportOptions_animation(" + str(startFrame) + "," + str(endFrame) + ")")
                
                SIP_ExportFBX(curExportNode)
                
            SIP_ClearGarbage()


def SIP_ExportFBXCharacter(exportNode):
    origin = SIP_ReturnOrigin("")
    
    exportNodes = []

    if exportNode:
        exportNodes.append(exportNode)
    else:
        exportNodes = SIP_ReturnFBXExportNodes(origin)
        
    parentNode = cmds.listRelatives(origin, parent=True, fullPath = True)
    
    if parentNode:
        cmds.parent(origin, world = True)
        
    for curExportNode in exportNodes:
        if cmds.getAttr(curExportNode + ".export"):
            mel.eval("SIP_SetFBXExportOptions_model()")
            
            cmds.select(clear = True)
            
            meshes = SIP_ReturnConnectedMeshes(exportNode)
            cmds.select(origin, add = True)
            cmds.select(meshes, add = True)
            
            SIP_ExportFbx(curExportNode)
            
        if parentNode:
            cmds.parent(origin, parentNode[0])

    
#PURPOSE        Populate the root joints panel in the model tab
#PROCEDURE      it will search for the origin. if none found, list all joints in the scene
#PRESUMPTION    origin is going to be a joint, rigs are not referenced in
def SIP_FBXExporterUI_PopulateModelRootJointsPanel():
    
    cmds.textScrollList("sip_FBXExporter_window_modelsOriginTextScrollList", edit = True, removeAll = True)
    
    origin = SIP_ReturnOrigin("")
    
    if origin != "Error":
        cmds.textScrollList("sip_FBXExporter_window_modelsOriginTextScrollList", edit = True, ebg = False, append = origin)
    else:
        joints = cmds.ls(type = "joint")
        for curJoint in joints:
            cmds.textScrollList("sip_FBXExporter_window_modelsOriginTextScrollList", edit = True, bgc = [1, 0.1, 0.1], append = curJoint)



#PURPOSE        To populate the actor panel in the UI
#PROCEDURE      get list of all references in the scene
#               for each reference, get the namespace
#               call SIP_ReturnOrigin for each namespace.
#               if not "Error", add namespace to textScrollList
#PRESUMPTION    single-layered referencing, references have namespace
def SIP_FBXExporterUI_PopulateAniamtionActorPanel():
    
    cmds.textScrollList("sip_FBXExporter_window_animationActorsTextScrollList", edit = True, removeAll = True)
    
    references = cmds.file(query = True, reference = True)
    
    for curRef in references:
        if not cmds.file(curRef, query = True, deferReference = True):
            ns = cmds.file(curRef, query = True, namespace = True)
            origin = SIP_ReturnOrigin(ns)
            
            if origin != "Error":
                cmds.textScrollList("sip_FBXExporter_window_animationActorsTextScrollList", edit = True, append = ns)              


def SIP_FBXExporter_AnimationHelpWindow():
    if cmds.window("sip_FBXExporter_animationHelpWindow", exists = True):
        cmds.deleteUI("sip_FBXExporter_animationHelpWindow")
        
    cmds.window("sip_FBXExporter_animationHelpWindow", s = True, width = 500, height = 500, menuBar = True, title = "Help on Animation Export")
    cmds.paneLayout(configuration = 'horizontal4')
    cmds.scrollField(editable = False, wordWrap = True, text = "Animation Export: \nAnimation export assumes single-level referencing with proper namesapce.\n\nActors: \nAll referenced characters with a origin joint tagged with the origin attribute will be listed in the Actor's field by their namespace. Please see the modeling help window for how to tage a character's origin with the origin attribute.\n\nExport Nodes:\nThe Export Nodes panel will fill in with export nodes connected to the origin of the selected actor from the Actor's field. Clicking on the New Export Node will create a new node. Each export node represents a seperate animation.\n\nExport:\nThe Export flag means the current export ndoe will be available for export. All nodes wihtout this checked will not be exported.\n\nMove to origin:\nNot yet supported\n\nSub Range:\nTurn this on to enable the sub-range option for the selected node. This will enable the Start Frame and End Frame fields where you can set the range for the specified animation. Otherwise, the animation will use the frame range of the file.\n\nExport File Name:\nClick on the Browse button to browse to where you want the file to go. The path will be project relative.\n\nExport Selected Animation:\nClick this button to export the animation selected in Export Nodes\n\nExport All Animations For Selected Character:\nClick this button to export all animations for the selected actor in the Actors filed. This flag will ignore what is selected in Export Nodes and export from all found nodes for the character\n\nExport All Animations:\nClick this button to export all animations for all characters. All selections will be ignored" )		
    
    cmds.showWindow("sip_FBXExporter_animationHelpWindow")





def SIP_FBXExporter_ModelHelpWindow():
    if cmds.window("sip_FBXExporter_modelHelpWindow", exists = True):
        cmds.deleteUI("sip_FBXExporter_modelHelpWindow")
        
    cmds.window("sip_FBXExporter_modelHelpWindow", s = True, width = 500, height = 500, menuBar = True, title = "Help on Model Export")
    cmds.paneLayout(configuration = 'horizontal4')
    cmds.scrollField(editable = False, wordWrap = True, text = "Model Export: \nModel exporter assumes one skeleton for export. Referencing for model export is not supported\n\nRoot Joints: \nPanel will list all the joints tagged with the \"origin\" attribute. If no joint is tagged with the attribute, it will list all joints in the scene and turn red. Select the root joint and click the Tag as Origin button.\n\nExport Nodes:\nThe Export Nodes panel will fill in with export nodes connected to the origin of the selected actor from the Actor's field. Clicking on the New Export Node will create a new node. Each export node represents a seperate character export (for example, seperate LOD's).\n\nMeshes:\nThe Meshes panel shows all the geometry associated with the selected export node. This can be used if you have mesh variations skinned to the same rig or LOD's.\n\nExport File Name:\nClick on the Browse button to browse to where you want the file to go. The path will be project relative.\n\nExport Selected Character:\nClick this button to export the character selected in Export Nodes\n\nExport All Characters:\nClick this button to export all character definitions for the skeleton. All selections will be ignored" )
	
    cmds.showWindow("sip_FBXExporter_modelHelpWindow")




