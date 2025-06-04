import React, { useEffect, useState } from 'react';
import { View, Button, StyleSheet, Image, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';

export default function App() {
  const [image, setImage] = useState(null);

  useEffect(() => {
    (async () => {
      const cameraPermission = await ImagePicker.requestCameraPermissionsAsync();
      if (cameraPermission.status !== 'granted') {
        Alert.alert('Permiso requerido', 'Necesitamos acceso a la cámara.');
      }
    })();
  }, []);

  const takePhoto = async () => {
    console.log('Botón presionado: intentando abrir cámara');
    try {
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        quality: 1,
      });
  
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

  const sendToBackend = async (photo) => {
    const uri = photo.uri;
    const fileName = uri.split('/').pop();
    const fileType = 'image/jpeg';

    const formData = new FormData();
    formData.append('file', {
      uri,
      name: fileName,
      type: fileType,
    });

    try {
      const response = await fetch('http://192.168.1.138:8000/factura', {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const json = await response.json();
      console.log(json);
      Alert.alert('Éxito', json.mensaje);
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'No se pudo enviar la imagen al servidor.');
    }
  };

  return (
    <View style={styles.container}>
      <Button title="Subir factura" onPress={takePhoto} />
      {image && <Image source={{ uri: image }} style={styles.image} />}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  image: {
    marginTop: 20,
    width: '100%',
    height: 300,
    resizeMode: 'contain',
  },
});
