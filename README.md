# Mobile App (React Native + Expo)

Este directorio contiene un MVP muy sencillo para tomar la foto de una factura y enviarla a un backend FastAPI.
A continuación se explica la finalidad de cada archivo principal:

| Archivo | Propósito |
| ------- | --------- |
| **App.js** | Componente principal que solicita permisos de cámara, permite tomar una foto con `expo-image-picker` y la envía al endpoint `/factura`. |
| **index.js** | Punto de entrada que registra el componente `App` con Expo. |
| **app.json** | Configuración de la aplicación Expo (nombre, iconos, etc.). |
| **assets/** | Imágenes utilizadas (iconos, splash screen…). |

## Sugerencias de organización

- Separar la lógica de red en un servicio (por ejemplo `services/api.js`) para poder reutilizarla y testearla.
- Crear una carpeta `components/` para agrupar pequeños componentes reutilizables.
- Colocar las pantallas en `screens/` si la app crece y llega a usar `react-navigation`.
- Los estilos podrían colocarse en archivos aparte cuando crezcan, o utilizar utilidades como `StyleSheet` en módulos separados.

Al ser un MVP, todo está en `App.js`, pero estas divisiones ayudan a mantener el código claro cuando se añadan nuevas funcionalidades.
