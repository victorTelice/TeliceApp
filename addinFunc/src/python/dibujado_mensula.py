import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import ezdxf
    import pandas as pd
    import numpy as np
    import re
    import math
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing import layout, svg
    from ezdxf.addons import Importer
    from ezdxf.enums import TextEntityAlignment

    return (
        Frontend,
        Importer,
        RenderContext,
        TextEntityAlignment,
        ezdxf,
        layout,
        math,
        mo,
        np,
        pd,
        re,
        svg,
    )


@app.function
def obtención_coordenadas(matriz, indice, distancia_mensulas):
    x = []
    y = []
    
    # Generar nombres de columnas
    

    for i in range(matriz.shape[0]):

        suma = matriz.loc[i,[f"x_{indice}"]].values + (distancia_mensulas*(indice-1))
        
        x.append(suma)
        y.append(matriz.loc[i,[f"y_{indice}"]].values)

    puntos = {
    f'punto_{j+1}': (x1,y1)
    for j, (x1,y1) in enumerate(zip(x,y))
}
    return puntos


@app.cell
def _(limpiar_num, pd):
    def cargar_matriz_coordenadas():
        dataframe_coordenadas = pd.read_csv('Coordenadas_python 1.txt',sep='\t',header=None)
        dataframe_coordenadas = dataframe_coordenadas.map(limpiar_num)

        nombres_columnas = [f"{coord}_{i+1}" for i in range(dataframe_coordenadas.shape[1]//2) for coord in ["x", "y"]]
        dataframe_coordenadas.columns = nombres_columnas

    
        for col in dataframe_coordenadas.select_dtypes(include='object').columns:
            try:
                dataframe_coordenadas[col] = pd.to_numeric(dataframe_coordenadas[col], errors='coerce')
            except Exception as e:
                print(f"No se pudo convertir la columna '{col}': {e}")
    
        # Verifica los tipos de datos después de la conversión
        print(dataframe_coordenadas.dtypes)


        return dataframe_coordenadas
    return (cargar_matriz_coordenadas,)


@app.cell
def _(Importer, ezdxf):
    def insertar_bloque(
        doc,
        msp,
        ruta_origen: str,
        nombre_bloque: str,
        punto_insercion=(0, 0),
        escala=1.0,
        rot_deg=0.0,
    ):

    
        # 1) Abrir origen
        doc_src = ezdxf.readfile(ruta_origen)


        # 3) Importar la definición del bloque (y dependencias) desde el origen:
        if nombre_bloque not in doc_src.blocks:
            raise ValueError(f"El bloque '{nombre_bloque}' no existe en el DXF de origen.")

        imp = Importer(doc_src, doc)
        imp.import_block(nombre_bloque)   # importa el BLOCK y sus recursos
        imp.finalize()                    # muy importante: aplica/purgea los recursos importados

        # 4) Insertar el bloque en el modelspace con escala y rotación
        msp.add_blockref(
            nombre_bloque,
            insert=punto_insercion,
            dxfattribs={
                "xscale": float(escala),
                "yscale": float(escala),   # para escala uniforme; puedes poner distinto valor si quieres escala no uniforme
                "rotation": float(rot_deg) # grados (CCW), alrededor del eje Z
            },
        )
    return


@app.cell
def _(
    TextEntityAlignment,
    cargar_matriz_coordenadas,
    cargar_tabla_excel,
    ezdxf,
    math,
    np,
    visualizar_dxf,
):

    def dibujar_mensula(nombre):
        claves = ['nº perfil','Fr']
        R=83
        t_b=1
        ancho_via = 1435
        carril = 72
        pi = math.pi
        distancia_mensulas = 10000

        tabla_mensulas = cargar_tabla_excel(topografía='05_Oural - Sarria.xls', hoja_calculo = 'OU_SR_05', clave = claves[0])
        tabla_fuerzas = cargar_tabla_excel(topografía='05_Oural - Sarria.xls', hoja_calculo= 'OU_SR_05', clave = claves[1])

        peralte = tabla_mensulas['Peralte (mm)'].to_list()
        FR = tabla_fuerzas['Fr'].to_list()
        brazo = tabla_mensulas['Tipo de Brazo'].to_list() 
        titulo = tabla_mensulas['nº perfil'].to_list()

    
        doc = ezdxf.new(setup=True,)
                # Add new dimension entities to the modelspace:
        msp = doc.modelspace()

        capa_1 = doc.layers.add('Mensula')
        capa_1.color = 7

        capa_2 = doc.layers.add('Via')
        capa_2.color = 1

        capa_3 = doc.layers.add('Cotas')
        capa_3.color = 3

        dimstyle = doc.dimstyles.duplicate_entry('EZDXF', 'MI_ESTILO_COTAS')

        # Configurar propiedades del estilo de cota
        dimstyle.dxf.dimscale = 1.0        # Escala general de la cota
        dimstyle.dxf.dimtxt = 200          # Altura del texto
        dimstyle.dxf.dimasz = 25          # Tamaño de las flechas
        dimstyle.dxf.dimexe = 12.5         # Extensión de líneas de referencia
        dimstyle.dxf.dimexo = 6.25        # Desplazamiento de líneas de referencia
        dimstyle.dxf.dimgap = 6.25        # Separación entre texto y línea de cota
        dimstyle.dxf.dimtad = 1

        matriz_limpia = cargar_matriz_coordenadas()

        for indice in range(len(tabla_mensulas)):
            print(indice)
            alfa = math.atan(peralte[indice]/(ancho_via+carril))    

            xvia = (ancho_via/2)*math.cos(alfa)
            yvia = (ancho_via/2)*math.sin(alfa)
    
            xeje = 6000*np.sin(alfa) + (distancia_mensulas*indice)
            yeje = 6000*np.cos(alfa)
    
            xrod =((ancho_via/2) + (carril))*np.cos(-alfa)
            yrod =((ancho_via/2) + (carril))*np.sin(-alfa)
    
            xcarril=(xvia+carril)*np.cos(alfa)
            ycarril=(yvia-carril)*np.sin(alfa) 
        
            puntos_dibujo = obtención_coordenadas(matriz_limpia, indice+1,distancia_mensulas=distancia_mensulas)

            #Brazo Atirantado
            if t_b==3:
                if FR[1]<0:
                    x_centro = puntos_dibujo['punto_50'][0] - R
                    y_centro = puntos_dibujo['punto_51'][1] - R;
                    sigma1=math.asin((puntos_dibujo['punto_50'][1]-y_centro)/R)*180/pi 
                    sigma2=(pi/2) - math.asin(( (puntos_dibujo['punto_51'][0]-x_centro)/R ))*180/pi 
    
                else:
                    x_centro = puntos_dibujo['punto_50'][0] + R
                    y_centro = puntos_dibujo['punto_51'][1] - R;
                    sigma1=180 - (math.asin((puntos_dibujo['punto_50'][1]-y_centro)/R)*180/pi) 
                    sigma2=(pi/2) - (math.asin(( (puntos_dibujo['punto_51'][0]-x_centro)/R ))*180/pi)
    
                msp.add_arc(center=(x_centro,y_centro),
                            radius=R,
                            start_angle=sigma1,
                            end_angle=sigma2,
                            dxfattribs={
                                'layer': 'Mensula'
                            })
    
            else:
                msp.add_line(puntos_dibujo['punto_50'],
                              puntos_dibujo['punto_52'],
                             dxfattribs={
                                'layer': 'Mensula'
                            })
    
            msp.add_line(puntos_dibujo['punto_51'],
                         puntos_dibujo['punto_52'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_25'],
                         puntos_dibujo['punto_23'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_26'],
                         puntos_dibujo['punto_28'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_23'],
                         puntos_dibujo['punto_36'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_28'],
                         puntos_dibujo['punto_22'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_9'],
                         puntos_dibujo['punto_35'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_37'],
                         puntos_dibujo['punto_38'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_39'],
                         puntos_dibujo['punto_40'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_4'],
                         puntos_dibujo['punto_5'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_35'],
                         puntos_dibujo['punto_11'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_11'],
                         puntos_dibujo['punto_12'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_8'],
                         puntos_dibujo['punto_13'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_13'],
                         puntos_dibujo['punto_37'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_38'],
                         puntos_dibujo['punto_16'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_16'],
                         puntos_dibujo['punto_17'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_36'],
                         puntos_dibujo['punto_19'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_19'],
                         puntos_dibujo['punto_20'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_3'],
                         puntos_dibujo['punto_21'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_29'],
                         puntos_dibujo['punto_30'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_30'],
                         puntos_dibujo['punto_39'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_34'],
                         puntos_dibujo['punto_33'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_33'],
                         puntos_dibujo['punto_40'],
                         dxfattribs={
                        'layer': 'Mensula'
            })
       
            msp.add_line(puntos_dibujo['punto_42'],
                         puntos_dibujo['punto_44'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_41'],
                         puntos_dibujo['punto_43'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_44'],
                         puntos_dibujo['punto_26'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_43'],
                         puntos_dibujo['punto_25'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_46'],
                         puntos_dibujo['punto_47'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_48'],
                         puntos_dibujo['punto_49'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_46'],
                         puntos_dibujo['punto_48'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_47'],
                         puntos_dibujo['punto_49'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_4'],
                         puntos_dibujo['punto_51'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

            msp.add_line(puntos_dibujo['punto_51'],
                         puntos_dibujo['punto_52'],
                         dxfattribs={
                        'layer': 'Mensula'
            })

        
    
            msp.add_text(titulo[indice],height=200).set_placement(
            puntos_dibujo['punto_47'],
            align=TextEntityAlignment.MIDDLE_RIGHT
        )
                                        
        
            #Vía
            msp.add_line((xrod+(distancia_mensulas*indice),yrod),(-xrod+(distancia_mensulas*indice),-yrod),dxfattribs={
                'layer': 'Via'
            })

            msp.add_line(puntos_dibujo['punto_1'],(xeje,yeje),dxfattribs={
                'layer': 'Via'
            })

            #Brazo
            msp.add_line(puntos_dibujo['punto_2'],puntos_dibujo['punto_50'],dxfattribs={
                'layer': 'Mensula'
            })
    
            # #TUBO TIRANTE
            # msp.add_aligned_dim(
            # p1=puntos_dibujo['punto_22'],           # Primer punto de medición
            # p2=puntos_dibujo['punto_28'],          # Segundo punto de medición
            # distance=100,          # Distancia de la línea de cota desde los puntos
            # dimstyle='MI_ESTILO_COTAS',
            # dxfattribs={
            #     'layer': 'COTAS',
            #     'color': 256  # Color por capa
            # }
            # ).render()

            # #TUBO MENSULA
            # msp.add_aligned_dim(
            # p1=puntos_dibujo['punto_36'],           # Primer punto de medición
            # p2=puntos_dibujo['punto_23'],          # Segundo punto de medición
            # distance=-2000,          # Distancia de la línea de cota desde los puntos
            # dimstyle='MI_ESTILO_COTAS',
            # dxfattribs={
            #     'layer': 'COTAS',
            #     'color': 256  # Color por capa
            # }
            # ).render()
    
            # #TUBO ESTABILIZADOR
            # msp.add_aligned_dim(
            # p1=puntos_dibujo['punto_9'],           # Primer punto de medición
            # p2=puntos_dibujo['punto_35'],          # Segundo punto de medición
            # distance=-900,          # Distancia de la línea de cota desde los puntos
            # dimstyle='MI_ESTILO_COTAS',
            # dxfattribs={
            #     'layer': 'COTAS',
            #     'color': 256  # Color por capa
            # }
            # ).render()
    
            # #TUBO PENDOLA
            # msp.add_aligned_dim(
            # p1=puntos_dibujo['punto_37'],           # Primer punto de medición
            # p2=puntos_dibujo['punto_38'],          # Segundo punto de medición
            # distance=100,          # Distancia de la línea de cota desde los puntos
            # dimstyle='MI_ESTILO_COTAS',
            # dxfattribs={
            #     'layer': 'COTAS',
            #     'color': 256  # Color por capa
            # }
            # ).render()
    
            # #TUBO DIAGONAL
            # msp.add_aligned_dim(
            # p1=puntos_dibujo['punto_39'],           # Primer punto de medición
            # p2=puntos_dibujo['punto_40'],          # Segundo punto de medición
            # distance=100,          # Distancia de la línea de cota desde los puntos
            # dimstyle='MI_ESTILO_COTAS',
            # dxfattribs={
            #     'layer': 'COTAS',
            #     'color': 256  # Color por capa
            # }
            # ).render()
    
            # #AISLADOR MENSULA
            # msp.add_aligned_dim(
            # p1=puntos_dibujo['punto_25'],           # Primer punto de medición
            # p2=puntos_dibujo['punto_23'],          # Segundo punto de medición
            # distance=100,          # Distancia de la línea de cota desde los puntos
            # dimstyle='MI_ESTILO_COTAS',
            # dxfattribs={
            #     'layer': 'COTAS',
            #     'color': 256  # Color por capa
            # }
            # ).render()
    
            # #AISLADOR TIRANTE
            # msp.add_aligned_dim(
            # p1=puntos_dibujo['punto_28'],           # Primer punto de medición
            # p2=puntos_dibujo['punto_26'],          # Segundo punto de medición
            # distance=100,          # Distancia de la línea de cota desde los puntos
            # dimstyle='MI_ESTILO_COTAS',
            # dxfattribs={
            #     'layer': 'COTAS',
            #     'color': 256  # Color por capa
            # }
            # ).render()
    
            visualizacion = visualizar_dxf(doc,msp)
        doc.saveas(nombre)

        return visualizacion
    return (dibujar_mensula,)


@app.cell
def _(re):

    def limpiar_num(v):
        if isinstance(v, str):
            # Elimina la parte imaginaria, incluyendo notación exponencial
            v = re.sub(r"[+-]?\d*\.?\d+(?:e[+-]?\d+)?j", "", v)

        try:
            return float(v)
        except:
            return v

    return (limpiar_num,)


@app.cell
def _(np, pd):
    def cargar_tabla_excel(topografía,hoja_calculo,clave):

        datos_topografia = pd.read_excel(topografía,sheet_name=hoja_calculo,header=None)

        coords = np.where(datos_topografia.values.astype(str) == clave)

        if coords[0].size == 0:
            raise ValueError(f"No encontré {clave} en la hoja.")

        fila0,col0 = coords[0][0],coords[1][0]

        col_final = col0
        fila_final = fila0
        while col_final +1 < datos_topografia.shape[1] and not pd.isna(datos_topografia.iat[fila0, col_final + 1]) :
            col_final+=1


        while fila_final +1 < datos_topografia.shape[0]:
            if pd.isna(datos_topografia.iat[fila_final + 1, col0]) and datos_topografia.iat[fila_final + 1, col0] != 0 :
                fila_final+=1

                break
            fila_final+=1

        header = datos_topografia.iloc[fila0, col0:col_final+1].tolist()

        tabla = datos_topografia.iloc[fila0 + 1:fila_final,col0:col_final+1].copy()
        tabla.columns = header

        tabla.reset_index(drop=True, inplace=True)



        return tabla
    return (cargar_tabla_excel,)


@app.cell
def _(mo):
    excel_topografia = mo.ui.file(label='Selecciona el Excel de Datos de Topografía', kind='area')
    nombre = mo.ui.text(label='Nombre')
    boton = mo.ui.run_button(label='Dibujar Mensula')
    guardado = mo.ui.run_button(label='Guardar DXF')
    return boton, excel_topografia, nombre


@app.cell
def _(excel_topografia):
    excel_topografia
    return


@app.cell
def _(excel_topografia, mo):
    mo.stop(excel_topografia.name(0) is None)

    excel_topografia.name(0)
    return


@app.cell
def _(nombre):
    nombre
    return


@app.cell
def _(boton, excel_topografia, mo, pd):
    mo.stop(excel_topografia.name(0) is None,mo.md("Selecciona el archivo").callout())
    try:
        hojas = pd.ExcelFile(excel_topografia.name(0)).sheet_names

    except FileNotFoundError:
        print("El archivo no se encontró.")

    except Exception as e:
        print("Ocurrió un error al leer el archivo:", e)

    opciones_hoja_calculo = mo.ui.dropdown(options=hojas)



    mo.vstack([opciones_hoja_calculo, boton])
    return


@app.cell
def _(mo):
    def guardar_DXF(doc):
        return mo.ui.file_browser()
    return


@app.cell
def _(Frontend, RenderContext, layout, mo, svg):
    def visualizar_dxf(doc,msp):

        try:

            backend = svg.SVGBackend()
            Frontend(RenderContext(doc), backend).draw_layout(msp)
            svg_string = backend.get_string(
                layout.Page(300, 120, layout.Units.mm), 
                settings=layout.Settings(0,1)
            )

            return mo.Html(svg_string)
        except Exception as e:
            print(e)
            return None

    return (visualizar_dxf,)


@app.cell
def _(boton, dibujar_mensula, mo, nombre):
    mo.stop(not boton.value,mo.md("No se activa el boton"))
    dibujar_mensula(nombre.value)
    # visualizar_dxf(nombre.value)
    return


if __name__ == "__main__":
    app.run()
