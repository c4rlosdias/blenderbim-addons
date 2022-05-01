bl_info = {
    "name": "Add Measure",
    "author": "Carlos Dias",
    "version": (1, 0),
    "blender": (3, 1, 2),
    "location": "View3D > Panel > My Tools",
    "description": "Adiciona medição a um elemento",
    "warning": "",
    "doc_url": "",
    "category": "User",
}

import bpy
from datetime import datetime
import ifcopenshell
import ifcopenshell.util
from ifcopenshell.util.selector import Selector
from blenderbim.bim.ifc import IfcStore


# == FUNCTIONS ==

# Adiciona medição
def add_measure(props):
    # Obtendo a data de hoje no formato adequado
    data_atual = props.data_inicio

    #Obtendo todos os objetos selecionados
    objs = bpy.context.selected_objects
    
    #Obtendo o arquivo ifc carregado
    ifc_file = IfcStore.get_file()

    #Se existem objetos selecionados
    if objs:
        #Para cada objeto selecionado
        for obj in objs:
            id = obj.BIMObjectProperties.ifc_definition_id
            if not id==0:
                ifc_obj = ifc_file.by_id(id)
                             
                data_med = props.data_medicao

                # montando as propriedades para o property set
                prop={
                    'Data da Medição' : data_med,
                    'Percentual medido' : round(props.perc_medido, 2),
                    'Pendente' : ifc_file.createIfcBoolean(props.pendente),
                    'Pendência' : ifc_file.createIfcText(props.pendencia),
        
                }
                
            
                # Inserindo pset e editando propriedade
                pset = ifcopenshell.api.run("pset.add_pset", ifc_file, product=ifc_obj, name=props.pset)
                ifcopenshell.api.run("pset.edit_pset", ifc_file, pset=pset, properties=prop)
                            
                #Colorindo o objeto
                bpy.data.objects[obj.name].color = (0.071,1,0.065, 0.5)
                
                #Ocultando o objeto
                if props.oculta:
                    obj.hide_set(True)


# Pesquisa elementos medidos    
def pesq_medidos(props):

    
    # Converte as datas de pesquisa para timestamp
    if props.data_inicio == '':
        d_ini = 0
    else:
        d_ini = int(datetime.strptime(props.data_inicio, '%d/%m/%Y').timestamp())
    
    if props.data_fim == '':
        d_fim = 95627931508 #data muito a frente
    else:
        d_fim = int(datetime.strptime(props.data_fim, '%d/%m/%Y').timestamp())
        
    #Obtendo o arquivo ifc carregado
    ifc_file = IfcStore.get_file()
    

    for obj in bpy.data.objects:
        id_ifc_obj = obj.BIMObjectProperties.ifc_definition_id
        if not id_ifc_obj == 0:
            
            ifc_obj = ifc_file.by_id(id_ifc_obj)    
            psets = ifcopenshell.util.element.get_psets(ifc_obj)

            obj.hide_set(True)
            
            if props.pset in psets:
                    
                data_med = psets[props.pset]['Data da Medição']
                dm_timestamp = int(datetime.strptime(data_med, '%d/%m/%Y').timestamp())          
                            
                if  d_ini <= dm_timestamp <= d_fim:
                    obj.hide_set(False)


# Pesquisa elementos medidos    
def pesq_nao_medidos(props):
    #Obtendo o arquivo ifc carregado
    ifc_file = IfcStore.get_file()

    for obj in bpy.data.objects:
        id_ifc_obj = obj.BIMObjectProperties.ifc_definition_id
        if not id_ifc_obj == 0:
            
            ifc_obj = ifc_file.by_id(id_ifc_obj)    
            psets = ifcopenshell.util.element.get_psets(ifc_obj)

            if props.pset in psets:
                obj.hide_set(True)
            else:
                obj.hide_set(False)
                
                   

# == GLOBAL VARIABLES

class MyProperties(bpy.types.PropertyGroup):
    pset        : bpy.props.StringProperty(name='Property Set',default='My_Pset')
    data_inicio : bpy.props.StringProperty(name='De:',default='')
    data_fim    : bpy.props.StringProperty(name='Até:', default=datetime.today().strftime("%d/%m/%Y"))
    data_medicao: bpy.props.StringProperty(name='Data da medição',default=datetime.today().strftime("%d/%m/%Y"))
    perc_medido : bpy.props.FloatProperty(name='Percentual medido', min=0, max=100, step=10, default=0.0, precision=0)
    pendente    : bpy.props.BoolProperty(name='Possui pendências?', default=False)
    pendencia   : bpy.props.StringProperty(name='Descreva', maxlen=1024, default='')
    oculta      : bpy.props.BoolProperty(name='Oculta o elemento após medir', default=False) 


# == PANELS ==

class Panel_Medicao(bpy.types.Panel):
    
    bl_label = "Aplica Medição"
    bl_idname = "VIEW3D_PT_add_measure"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "My Tools"
    
    
    def draw(self, context):
        
        props = context.scene.my_props

        layout = self.layout

        row = layout.row()
        row.prop(props, 'pset')
        row = layout.row()
        row.prop(props, 'data_medicao')
        row = layout.row()
        row.prop(props, 'perc_medido')
        row = layout.row(align=True)
        row.prop(props, 'pendente')

        if props.pendente:
            row = layout.row()
            row.prop(props, 'pendencia')

        row = layout.row()
        row.prop(props, 'oculta')
        row = layout.row()
        row.operator(Operator_Medicao.bl_idname,text="Aplicar Medição",icon='GREASEPENCIL')

class Panel_Pesquisa(bpy.types.Panel):
    
    bl_label = "Pesquisa elementos medidos"
    bl_idname = "VIEW3D_PT_search"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "My Tools"
    bl_options={'DEFAULT_CLOSED'}
    
    def draw(self, context):
        
        props = context.scene.my_props

        layout = self.layout
      
        row = layout.row()
        row.prop(props, 'data_inicio')
        row.prop(props, 'data_fim')  

        row = layout.row()    
        row.operator(Operator_Pesquisa_Medidos.bl_idname,
                     text="Pesquisa elementos medidos entre as datas",
                      icon='VIEWZOOM')
        
        row = layout.row() 
        row.separator()
        row = layout.row()    
        row.operator(Operator_Pesquisa_Nao_Medidos.bl_idname,
                     text="Pesquisa elementos NÂO medidos",
                      icon='VIEWZOOM')
                      
# == OPERATORS ==       
        
class Operator_Medicao(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "cd.operator_medicao"
    bl_label = "Realiza medição"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):

        try:
            props = context.scene.my_props
            if not props.pendente:
                props.pendencia=''
            add_measure(props)
            self.report({"INFO"}, "Medições executadas com Sucesso")
            
        except:
            self.report({"ERROR"}, "Alguma coisa saiu errada, confira as propriedades")
        return {"FINISHED"}


class Operator_Pesquisa_Medidos(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "cd.operator_pesquisa_medidos"
    bl_label = "Pesquisa itens medidos"

    def execute(self, context):
        
        props = context.scene.my_props
        pesq_medidos(props)

#        try:
#            props = context.scene.my_props
#            pesq_medidos(props)
#            self.report({"INFO"}, "Pesquisa executada com Sucesso")
#            
#        except:
#            self.report({"ERROR"}, "Alguma coisa saiu errada, confira as propriedades") 

        return {"FINISHED"}


class Operator_Pesquisa_Nao_Medidos(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "cd.operator_pesquisa_nao_medidos"
    bl_label = "Pesquisa itens não medidos"

    def execute(self, context):
        props = context.scene.my_props
        pesq_nao_medidos(props)



#        try:
#            props = context.scene.my_props
#            pesq_nao_medidos(props)
#            self.report({"INFO"}, "Pesquisa executada com Sucesso")
#            
#        except:
#            self.report({"ERROR"}, "Alguma coisa saiu errada, confira as propriedades") 

        return {"FINISHED"}

# == MAIN ROUTINE ==

CLASSES = [
    Operator_Medicao,
    Operator_Pesquisa_Medidos,
    Operator_Pesquisa_Nao_Medidos,
    Panel_Medicao,
    Panel_Pesquisa,
    MyProperties
]


def register():

    for klass in CLASSES:
        bpy.utils.register_class(klass)
    bpy.types.Scene.my_props = bpy.props.PointerProperty(type=MyProperties) 
    



def unregister():
    
    del bpy.types.Scene.my_props
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)



if __name__ == "__main__":
    register()


