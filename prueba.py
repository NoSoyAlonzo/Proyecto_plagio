import requests

query = "prueba de búsqueda"
url = f"https://html.duckduckgo.com/html/?q={query}"

response = requests.get(url)

if response.status_code == 200:
    print("DuckDuckGo responde correctamente.")
    print(response.text[:500])  # Muestra parte de la respuesta HTML
else:
    print(f"Error: {response.status_code}")
