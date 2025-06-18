// App principal de Expo/React Native.
// Permite tomar una foto de una factura y enviarla a un backend.
// Se utiliza `expo-image-picker` para abrir la cámara y `fetch` para subir la imagen.
import React, { useEffect, useState } from 'react';
import { View, Button, StyleSheet, Image, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';

// Componente principal de la app.
// Muestra un botón para hacer la foto y envía la imagen al backend.
export default function App() {
  const [image, setImage] = useState(null);

  useEffect(() => {
    // Solicitamos permisos de cámara una vez al montar el componente.
    (async () => {
      const cameraPermission = await ImagePicker.requestCameraPermissionsAsync();
      if (cameraPermission.status !== 'granted') {
        Alert.alert('Permiso requerido', 'Necesitamos acceso a la cámara.');
      }
    })();
  }, []);

  // Abre la cámara y gestiona la foto devuelta por ImagePicker.
  const takePhoto = async () => {
    console.log('Botón presionado: intentando abrir cámara');
    try {
      // Abrimos la cámara con configuración básica.
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        quality: 1,
      });
  
      // Si el usuario no canceló y se obtuvo alguna imagen la subimos.
      if (!result.canceled && result.assets.length > 0) {
        console.log('Foto tomada con éxito');
        const photo = result.assets[0];
        setImage(photo.uri);
        await sendToBackend(photo);
      } else {
        console.log('La cámara fue cancelada o no devolvió imagen');
      }
    } catch (error) {
      console.log('Error al abrir la cámara o enviar:', error);
      Alert.alert('Error', 'No se pudo abrir la cámara.');
    }
  };  

  // Sube la foto al backend usando `fetch` y multipart/form-data.
  const sendToBackend = async (photo) => {
    const uri = photo.uri;
    const fileName = uri.split('/').pop();
    const fileType = 'image/jpeg';

    // Construimos el cuerpo de la petición con la imagen.
    const formData = new FormData();
    formData.append('file', {
      uri,
      name: fileName,
      type: fileType,
    });

    try {
      // Llamamos al backend FastAPI (ajustar IP/puerto en producción).
      const response = await fetch('http://192.168.1.138:8000/factura', {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const json = await response.json();
      console.log(json);
      // Mostramos al usuario la respuesta del backend.
      Alert.alert('Éxito', json.mensaje);
    } catch (error) {
      console.error(error);
      // Avisamos al usuario si falla la petición.
      Alert.alert('Error', 'No se pudo enviar la imagen al servidor.');
    }
  };

  // Renderizamos un botón y, si existe, la miniatura de la foto.
  return (
    <View style={styles.container}>
      <Button title="Subir factura" onPress={takePhoto} />
      {image && <Image source={{ uri: image }} style={styles.image} />}
    </View>
  );
}

const styles = StyleSheet.create({
  // Estilos básicos para la vista principal
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  image: {
    marginTop: 20,
    width: '100%',
    height: 300,
    resizeMode: 'contain', // Ajuste para que la foto se vea completa
  },
});
