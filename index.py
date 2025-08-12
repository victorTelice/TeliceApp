import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    # mo.sidebar(
    #     [
    #         mo.md("# Navegación"),
        
            # mo.nav_menu(
            #     {
            #         "http://127.0.0.1:2718/?file=Trazado.py": f"{mo.icon('streamline-color:arrow-roadmap')} Trazados",
            #         "http://127.0.0.1:2718/?file=Proyecto.py": f"{mo.icon('streamline-color:ai-prompt-spark')} Proyecto",
            #         "http://127.0.0.1:2718/?file=Via.py": f"{mo.icon('streamline-color:ladder')} Via",
            #         "http://127.0.0.1:2718/?file=Conductores.py": f"{mo.icon('streamline-color:ai-vehicle-spark-1')} Conductores",
            #         "http://127.0.0.1:2718/?file=Viento_Hielo.py": f"{mo.icon('streamline-color:wind-flow-1')} Viento_Hielo",
            #         "http://127.0.0.1:2718/?file=Mensulas_Postes.py": f"{mo.icon('streamline-color:parking-sign')} Mensulas_Postes",
            #         "http://127.0.0.1:2718/?file=Pesos.py": f"{mo.icon('streamline-color:rock-slide')} Pesos",
            #         "http://127.0.0.1:2718/?file=Fuerzas_Extra.py": f"{mo.icon('streamline-color:button-power-1')} Fuerzas_Extra",
            #         "http://127.0.0.1:2718/?file=Cimentaciones.py": f"{mo.icon('streamline-color:inbox-tray-1')} Cimentaciones",
            #         "http://127.0.0.1:2718/?file=Coeficientes.py": f"{mo.icon('streamline-color:creative-commons')} Coeficientes",
            #         "http://127.0.0.1:2718/?file=Exportar_Datos.py": f"{mo.icon('streamline-color:expand-window-2')} Exportar_Datos",
            
                

            #     },
                #orientation="vertical",
            #),
    #          mo.md(f"{mo.icon('streamline-color:expand-window-2')} Exportar_Datos"),
    #         mo.md(f"<span style='color: #888888;'>{mo.icon('streamline-color:expand-window-2')} Exportar_Datos</span>")

    #     ]
    # )
    def trazado_view():
        return mo.md("# Página de Trazados")

    def proyecto_view():
        return mo.md("# Página de Proyecto")

    def via_view():
        return mo.md("# Página de Vía")
    def render_home():
        return mo.md("# Bienvenido a la página principal")
    # Definir las rutas
    mo.routes({
        "/Trazado": trazado_view,
        "/Proyecto": proyecto_view,
        "/Via": via_view,
        mo.routes.CATCH_ALL: render_home,
    })

    # Luego sidebar con links (puede usar nav_menu o md)
    mo.sidebar([
        mo.md("# Navegación"),
        mo.nav_menu({
            "http://127.0.0.1:2718/?file=Trazado.py": f"{mo.icon('streamline-color:arrow-roadmap')} Trazados",
            "/http://127.0.0.1:2718/?file=Proyecto.py": f"{mo.icon('streamline-color:ai-prompt-spark')} Proyecto",
            "http://127.0.0.1:2718/?file=Via.py": f"{mo.icon('streamline-color:ladder')} Via",
        }, orientation="vertical"),
    ])

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
