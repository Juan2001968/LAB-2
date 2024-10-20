import pandas as pd
import math
import heapq
import networkx as nx
import folium 

def mostrar_mapa_aeropuertos(grafo):
    
    latitudes = [data['latitude'] for _, data in grafo.nodes(data=True)]
    longitudes = [data['longitude'] for _, data in grafo.nodes(data=True)]
    
    mapa = folium.Map(location=[sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)], zoom_start=2)

    
    for nodo, datos in grafo.nodes(data=True):
        folium.Marker(
            location=[datos['latitude'], datos['longitude']],
            popup=f"{datos['name']} ({nodo})<br>Ciudad: {datos['city']}<br>País: {datos['country']}",
            icon=folium.Icon(color='blue', icon='plane')
        ).add_to(mapa)

    
    mapa.save('mapa_aeropuertos.html')
    print("Mapa guardado como 'mapa_aeropuertos.html'")


def cargar_datos_y_construir_grafo(archivo):
    df = pd.read_csv(archivo)
    grafo = nx.Graph()

    for _, row in df.iterrows():
        origen = row['Source Airport Code']
        destino = row['Destination Airport Code']

        
        grafo.add_node(origen, name=row['Source Airport Name'], city=row['Source Airport City'], 
                       country=row['Source Airport Country'], latitude=row['Source Airport Latitude'], 
                       longitude=row['Source Airport Longitude'])

        grafo.add_node(destino, name=row['Destination Airport Name'], city=row['Destination Airport City'], 
                       country=row['Destination Airport Country'], latitude=row['Destination Airport Latitude'], 
                       longitude=row['Destination Airport Longitude'])

        
        distancia = calcular_distancia_haversine(row['Source Airport Latitude'], row['Source Airport Longitude'], 
                                                 row['Destination Airport Latitude'], row['Destination Airport Longitude'])
        grafo.add_edge(origen, destino, weight=distancia)

    return grafo


def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distancia = R * c
    return distancia

def verificar_conexidad(grafo):
    if nx.is_connected(grafo):
        print("El grafo es conexo.")
    else:
        componentes = list(nx.connected_components(grafo))
        print(f"El grafo no es conexo. Tiene {len(componentes)} componentes:")
        for i, componente in enumerate(componentes):
            print(f"Componente {i+1} tiene {len(componente)} vértices.")


def encontrar(sets, i):
    if sets[i] == i:
        return i
    else:
        sets[i] = encontrar(sets, sets[i])
        return sets[i]


def unir(sets, rank, u, v):
    uroot = encontrar(sets, u)
    vroot = encontrar(sets, v)
    
    if rank[uroot] < rank[vroot]:
        sets[uroot] = vroot
    elif rank[uroot] > rank[vroot]:
        sets[vroot] = uroot
    else:
        sets[vroot] = uroot
        rank[uroot] += 1


def kruskal_mst_por_componente(grafo):
    componentes = list(nx.connected_components(grafo))
    mst_total = 0

    for i, componente in enumerate(componentes):
        subgrafo = grafo.subgraph(componente)
        edges = []
        
        for nodo in subgrafo:
            for vecino, datos in subgrafo[nodo].items():
                peso = datos['weight']  
                if (vecino, nodo, peso) not in edges:  
                    edges.append((nodo, vecino, peso))
        
        
        edges.sort(key=lambda x: x[2])
        
        
        sets = {nodo: nodo for nodo in subgrafo}
        rank = {nodo: 0 for nodo in subgrafo}
        
        mst_peso_total = 0
        mst_edges = []
        
        
        for u, v, peso in edges:
            uroot = encontrar(sets, u)
            vroot = encontrar(sets, v)
            
            if uroot != vroot:
                unir(sets, rank, uroot, vroot)
                mst_edges.append((u, v, peso))
                mst_peso_total += peso
        
        
        print(f"Componente {i+1} - Peso total del Árbol de Expansión Mínima (MST): {mst_peso_total:.2f} km")
        mst_total += mst_peso_total

    
    print(f"Peso total de los MSTs de todas las componentes: {mst_total:.2f} km")



def dijkstra(grafo, inicio):
    distancias = {nodo: float('inf') for nodo in grafo}
    distancias[inicio] = 0
    prev = {nodo: None for nodo in grafo}
    cola_prioridad = [(0, inicio)]

    while cola_prioridad:
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)

        if distancia_actual > distancias[nodo_actual]:
            continue

        for vecino, datos in grafo[nodo_actual].items():
            peso = datos['weight']

            nueva_distancia = distancia_actual + peso

            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                prev[vecino] = nodo_actual
                heapq.heappush(cola_prioridad, (nueva_distancia, vecino))


    return distancias, prev


def mostrar_informacion_aeropuerto(grafo, codigo_aeropuerto):
    if codigo_aeropuerto in grafo.nodes:
        datos = grafo.nodes[codigo_aeropuerto]
        print(f"Código: {codigo_aeropuerto}")
        print(f"Nombre: {datos['name']}")
        print(f"Ciudad: {datos['city']}")
        print(f"País: {datos['country']}")
        print(f"Latitud: {datos['latitude']}")
        print(f"Longitud: {datos['longitude']}")
    else:
        print("El aeropuerto no se encuentra en el grafo.")


def mostrar_aeropuertos_mas_alejados(grafo, codigo_aeropuerto):
    distances, _ = dijkstra(grafo, codigo_aeropuerto)
   
    aeropuertos_mas_alejados = [(codigo, distancia) for codigo, distancia in distances.items() if distancia != float('inf')]
   
    aeropuertos_mas_alejados = sorted(aeropuertos_mas_alejados, key=lambda x: -x[1])[:10]

    print(f"Los 10 aeropuertos más alejados desde {codigo_aeropuerto} son:")
    for codigo, distancia in aeropuertos_mas_alejados:
        datos = grafo.nodes[codigo]
        print(f"{datos['name']} ({codigo}) - Ciudad: {datos['city']}, País: {datos['country']}, Distancia: {distancia:.2f} km")


def mostrar_camino_minimo(grafo, aeropuerto_origen, aeropuerto_destino):
    _, prev = dijkstra(grafo, aeropuerto_origen)
    path = []
    current = aeropuerto_destino

    while current is not None:
        path.append(current)
        current = prev[current]

    if path[-1] != aeropuerto_origen:
        print("No hay un camino disponible entre los aeropuertos especificados.")
        return []  
    else:
        path = path[::-1] 
        print(f"Camino mínimo desde {aeropuerto_origen} hasta {aeropuerto_destino}:")
        for codigo in path:
            datos = grafo.nodes[codigo]
            print(f"{datos['name']} ({codigo}) - Ciudad: {datos['city']}, País: {datos['country']}, Latitud: {datos['latitude']}, Longitud: {datos['longitude']}")
        return path  


def mostrar_mapa_camino(grafo, camino):
    if not camino:
        print("No hay camino para mostrar en el mapa.")
        return

    
    latitudes = [grafo.nodes[codigo]['latitude'] for codigo in camino]
    longitudes = [grafo.nodes[codigo]['longitude'] for codigo in camino]

    mapa = folium.Map(location=[latitudes[0], longitudes[0]], zoom_start=5)

    
    for i, codigo in enumerate(camino):
        datos = grafo.nodes[codigo]
        folium.Marker(
            location=[datos['latitude'], datos['longitude']],
            popup=f"{datos['name']} ({codigo})<br>Ciudad: {datos['city']}<br>País: {datos['country']}",
            icon=folium.Icon(color='red', icon='plane')
        ).add_to(mapa)

        
        if i < len(camino) - 1:
            next_lat = grafo.nodes[camino[i + 1]]['latitude']
            next_lon = grafo.nodes[camino[i + 1]]['longitude']
            folium.PolyLine(
                locations=[(datos['latitude'], datos['longitude']), (next_lat, next_lon)],
                color='blue',
                weight=2.5,
                opacity=1
            ).add_to(mapa)

    
    mapa.save('mapa_camino_aeropuertos.html')
    print("Mapa guardado como 'mapa_camino_aeropuertos.html'")


def menu(grafo):
    while True:
        print("\nMenú de opciones:")
        print("1. Verificar si el grafo es conexo")
        print("2. Calcular el Árbol de Expansión Mínima")
        print("3. Mostrar información de un aeropuerto")
        print("4. Mostrar los 10 aeropuertos más alejados desde un aeropuerto dado")
        print("5. Mostrar el camino mínimo entre dos aeropuertos")
        print("6. Mostrar el mapa de aeropuertos")
        print("7. Salir")
        
        opcion = input("Seleccione una opción (1-7): ")

        if opcion == "1":
            verificar_conexidad(grafo)
        elif opcion == "2":
            kruskal_mst_por_componente(grafo)
        elif opcion == "3":
            codigo_aeropuerto = input("Ingrese el código del aeropuerto: ").strip().upper()
            mostrar_informacion_aeropuerto(grafo, codigo_aeropuerto)
        elif opcion == "4":
            codigo_aeropuerto = input("Ingrese el código del aeropuerto: ").strip().upper()
            mostrar_aeropuertos_mas_alejados(grafo, codigo_aeropuerto)
        elif opcion == "5":
            aeropuerto_origen = input("Ingrese el código del aeropuerto origen: ").strip().upper()
            aeropuerto_destino = input("Ingrese el código del aeropuerto destino: ").strip().upper()
            camino = mostrar_camino_minimo(grafo, aeropuerto_origen, aeropuerto_destino)
            mostrar_mapa_camino(grafo, camino)
        elif opcion == "6":
            mostrar_mapa_aeropuertos(grafo)
        elif opcion == "7":
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción del 1 al 7.")


if __name__ == "__main__":
    archivo = 'flights_final.csv'  
    grafo = cargar_datos_y_construir_grafo(archivo)
    menu(grafo)
