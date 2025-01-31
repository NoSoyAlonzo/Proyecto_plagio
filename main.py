from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import difflib

app = Flask(__name__)

# Función para generar n-gramas de un texto
def obtener_ngramas(texto, n=4):
    palabras = texto.split()
    return [' '.join(palabras[i:i+n]) for i in range(len(palabras)-n+1)]

# Función para buscar en DuckDuckGo (SIN API)
def buscar_en_duckduckgo(consulta, num_resultados=5):
    url = f"https://html.duckduckgo.com/html/?q={consulta}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    
    response = requests.get(url, headers=headers)
    print("Respuesta DuckDuckGo:", response.status_code)  # DEBUG
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        resultados = []

        for enlace in soup.find_all("a", class_="result__a", limit=num_resultados):
            link = enlace["href"]
            if not link.startswith("http"):
                continue  
            resultados.append(link)

        print("Resultados DuckDuckGo:", resultados)  # DEBUG
        return resultados
    else:
        print(f"Error en la búsqueda: {response.status_code}")
        return []

# Función para obtener el texto de una página web
def obtener_texto_pagina(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        print(f"Accediendo a {url}: Código {response.status_code}")  # DEBUG

        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")
        texto = " ".join(p.text for p in soup.find_all("p") if len(p.text) > 30)
        print(f"Texto extraído de {url}:", texto[:200], "...")  # Solo muestra 200 caracteres
        return texto
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener {url}: {str(e)}")
        return ""

# Función para calcular similitud
def calcular_similitud(texto1, texto2):
    seq = difflib.SequenceMatcher(None, texto1, texto2)
    return round(seq.ratio() * 100, 2)

# Ruta para la verificación de plagio
@app.route("/verificar", methods=["POST"])
def verificar_plagio():
    data = request.get_json()
    texto_usuario = data.get("texto", "")

    print("Texto recibido:", texto_usuario)  # DEBUG
    
    if not texto_usuario.strip():
        return jsonify({"error": "El texto está vacío"}), 400

    # Generar n-gramas de 10 palabras
    ngramas = obtener_ngramas(texto_usuario, n=10)
    print("N-gramas generados:", ngramas[:3])  # DEBUG

    coincidencias = []
    
    for ngrama in ngramas[:3]:  
        urls = buscar_en_duckduckgo(f'"{ngrama}"', num_resultados=3)
        print("URLs encontradas:", urls)  # DEBUG

        for url in urls:
            texto_pagina = obtener_texto_pagina(url)
            if texto_pagina:
                porcentaje = calcular_similitud(texto_usuario, texto_pagina)
                print(f"Comparando con {url}: {porcentaje}%")  # DEBUG
                coincidencias.append({"url": url, "coincidencia": porcentaje})

    coincidencias = sorted(coincidencias, key=lambda x: x["coincidencia"], reverse=True)
    print("Resultados finales:", coincidencias)  # DEBUG

    return jsonify({"resultados": coincidencias})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
