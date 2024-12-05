# Ejecutar
```
pip install -r requirements.txt
streamlit run main.py
```

If new data is added (or run for the first time), run "Actualizar embedings".      

And ask a question like "¿Cuales son los 10 principios mencionados?"

![demo](./assets/demo.png)

# Formatting
```
pip install black
black main.py
```


# Pending tasks
- [x] Quitar tematica de Pokemon 
- [x] Agregar documentos en /data
- [x] Función actualizar_embeddings debe leer todos los archivos en /data
- [x] Fine tuning en RecursiveCharacterTextSplitter
- [ ] Fine tuning en ChatOpenAI
- [ ] Fine tuning en vectordb.similarity_search
- [x] Contenerizar
- [x] Adaptar a API y crear contenedor de UI (con logo de universidad y textarea)
- [x] Actualizar embedings automaticamente (quitar botón)
