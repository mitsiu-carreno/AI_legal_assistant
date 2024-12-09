# AI_legal_assistant


## Descripción del Proyecto
Este proyecto tiene como objetivo desarrollar un asistente legal basado en inteligencia artificial (IA) para responder preguntas relacionadas con la legalidad y la protección de la información. La solución integra múltiples herramientas y tecnologías para garantizar precisión, seguridad y eficiencia.

## Tecnologías Utilizadas

### Back-End
- **FastAPI**: Para crear APIs web rápidas y eficientes.
- **Docker**: Para la gestión del entorno de desarrollo y producción mediante contenedores.
- **SLM (Statistical Language Model)**: Modelo entrenado con documentos legales reales y casos ficticios.

### Front-End
- **Flutter**: Para el desarrollo de una interfaz de usuario interactiva y amigable.

### Procesamiento y Análisis de Datos
- **PDFs**: Documentos base que alimentan el modelo, incluyendo documentos reales y casos ficticios generados.
- **Integración GPT**: Uso de prompts para entrenar un modelo ajustado (fine-tuned) basado en Chat-GPT.

### Infraestructura
- **Logical Volume Management (LVM)**: Manejo eficiente de volúmenes lógicos para almacenamiento.
- **ELT (Extract, Load, Transform)**: Para procesar y transformar datos.

## Flujo del Sistema

1. Se inicia con un conjunto de **40 documentos PDF**.
2. Los PDFs son procesados junto con casos ficticios generados.
3. Los datos integrados alimentan un **modelo de lenguaje estadístico (SLM)** ajustado.
4. Se utiliza una **API GPT** para procesar las solicitudes legales en tiempo real.
5. Todo el sistema está contenido dentro de una infraestructura de **Docker en Linux**:
   - **Contenedor Back-End**: Implementa FastAPI.
   - **Contenedor Front-End**: Implementa Flutter para la interfaz.

## Diagrama del Sistema
![image](https://github.com/user-attachments/assets/0a6496ef-8d08-475c-a579-cb053fbb1c53)


## Conclusión
El proyecto combina herramientas modernas para ofrecer un asistente legal confiable y seguro. A través de la integración de tecnologías avanzadas como GPT y Docker, este sistema está diseñado para manejar grandes volúmenes de datos legales y ofrecer respuestas precisas en tiempo real.
