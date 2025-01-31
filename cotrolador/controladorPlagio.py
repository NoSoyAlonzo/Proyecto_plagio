
from flask import Flask, render_template, request, jsonify
from googlesearch import search

app = Flask(__name__)

# Función para dividir el texto en grupos de palabras (4-gramas)
def obtener_grupos(texto, n=4):
    palabras = texto.split()
    return [' '.join(palabras[i:i+n]) for i in range(len(palabras)-n+1)]

# Función para buscar coincidencias en Google
def buscar_en_google(frase, num_resultados=5):
    try:
        resultados = list(search(f'"{frase}"', num_results=num_resultados, lang="es"))
        return resultados
    except Exception as e:
        return []

# Ruta para mostrar la página principal
@app.route('/')
def index():
    return render_template('index.html')  # Carga el archivo desde templates/

# Ruta para verificar plagio
@app.route('/verificar', methods=['POST'])
def verificar_plagio():
    data = request.json
    texto = data.get("texto", "")
    
    if not texto:
        return jsonify({"error": "No se recibió ningún texto"}), 400
    
    grupos = obtener_grupos(texto)
    coincidencias = {}

    for grupo in grupos:
        urls = buscar_en_google(grupo)
        if urls:
            coincidencias[grupo] = urls
    
    porcentaje_plagio = (len(coincidencias) / len(grupos)) * 100 if grupos else 0

    return jsonify({
        "porcentaje_plagio": round(porcentaje_plagio, 2),
        "coincidencias": coincidencias
    })

if __name__ == '__main__':
    app.run(debug=True)
