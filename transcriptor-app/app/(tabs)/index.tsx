import React, { useState } from 'react';
import { View, Text, Button, ActivityIndicator, StyleSheet, ScrollView } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as Clipboard from 'expo-clipboard';

export default function HomeScreen() {
  const [texto, setTexto] = useState('');
  const [cargando, setCargando] = useState(false);

  const elegirAudio = async () => {
    const resultado = await DocumentPicker.getDocumentAsync({
  type: '*/*', // Acepta cualquier tipo de archivo
  copyToCacheDirectory: true,
});

    if (resultado.canceled || !resultado.assets) return;

    const archivo = resultado.assets[0];
    setCargando(true);
    setTexto('');

    try {
      const formData = new FormData();
      formData.append('file', {
        uri: archivo.uri,
        name: archivo.name,
        type: 'audio/mpeg',
      } as any);

      const respuesta = await fetch('http://192.168.0.102:8000/transcribir/', {
        method: 'POST',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        body: formData,
      });

      const json = await respuesta.json();
      setTexto(json.transcripcion || 'No se obtuvo transcripción');
    } catch (error) {
      console.error(error);
      setTexto('Error durante la transcripción');
    } finally {
      setCargando(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.contenedor}>
      <Button title="Elegir audio y transcribir" onPress={elegirAudio} />
      {cargando && <ActivityIndicator size="large" color="#0000ff" style={{ marginTop: 20 }} />}
      {texto !== '' && (
        <ScrollView style={styles.resultadoBox}>
          <Text style={styles.transcripcion}>{texto}</Text>
        </ScrollView>
      )}
      <Button
  title="Copiar texto"
  onPress={() => Clipboard.setStringAsync(texto)}
/>
    </ScrollView> 
  );
}

const styles = StyleSheet.create({
  contenedor: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#000', // Fondo negro
  },
  resultadoBox: {
    marginTop: 20,
    maxHeight: 400,
    padding: 10,
    backgroundColor: '#fff', // Fondo blanco para el texto
    borderRadius: 8,
  },
  transcripcion: {
    fontSize: 16,
    color: '#000', // Texto negro visible
  },
});
