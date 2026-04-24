/**
 * TigerEx Mobile KYC Verification
 * React Native - iOS & Android
 */
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Image, Platform } from 'react-native';
import { Camera } from 'expo-camera';

const COLORS = { primary: '#F0B90B', bg: '#0B0E11', card: '#1E2329', success: '#00C087', error: '#F6465D' };

export const KYCVerification = ({ navigation }) => {
  const [step, setStep] = useState(1);
  const [docType, setDocType] = useState('');
  const [front, setFront] = useState(null);
  const [back, setBack] = useState(null);
  const [selfie, setSelfie] = useState(null);

  const docTypes = [
    { id: 'passport', name: 'Passport', icon: '🛂' },
    { id: 'national_id', name: 'National ID', icon: '🪪' },
    { id: 'driver_license', name: "Driver's License", icon: '🚗' },
  ];

  const nextStep = () => setStep(s => s < 5 ? s + 1 : 5);
  const goBack = () => setStep(s => s > 1 ? s - 1 : 1);

  const renderStep = () => {
    switch(step) {
      case 1: return (
        <View style={styles.container}>
          <Text style={styles.title}>Select Document</Text>
          {docTypes.map(d => (
            <TouchableOpacity key={d.id} style={styles.docBtn} onPress={() => { setDocType(d.id); nextStep(); }}>
              <Text style={styles.docIcon}>{d.icon}</Text>
              <View><Text style={styles.docName}>{d.name}</Text></View>
            </TouchableOpacity>
          ))}
        </View>
      );
      case 2: return (
        <View style={styles.container}>
          <Text style={styles.title}>Front Side</Text>
          <TouchableOpacity style={styles.uploadBtn} onPress={() => Alert.alert('Upload', 'Select from gallery')}>
            <Text style={styles.uploadIcon}>📄</Text>
            <Text>Tap to upload</Text>
          </TouchableOpacity>
          <View style={styles.row}>
            <TouchableOpacity style={styles.btn} onPress={goBack}><Text>← Back</Text></TouchableOpacity>
            <TouchableOpacity style={[styles.btn, styles.primaryBtn]} onPress={nextStep}><Text>Continue →</Text></TouchableOpacity>
          </View>
        </View>
      );
      case 3: return (
        <View style={styles.container}>
          <Text style={styles.title}>Back Side</Text>
          <TouchableOpacity style={styles.uploadBtn} onPress={() => Alert.alert('Upload', 'Select from gallery')}>
            <Text style={styles.uploadIcon}>📃</Text>
            <Text>Tap to upload</Text>
          </TouchableOpacity>
          <View style={styles.row}>
            <TouchableOpacity style={styles.btn} onPress={goBack}><Text>← Back</Text></TouchableOpacity>
            <TouchableOpacity style={[styles.btn, styles.primaryBtn]} onPress={nextStep}><Text>Continue →</Text></TouchableOpacity>
          </View>
        </View>
      );
      case 4: return (
        <View style={styles.container}>
          <Text style={styles.title}>Selfie with Document</Text>
          <Text style={styles.subtitle}>Take selfie holding document next to face</Text>
          <View style={styles.cameraBox}>
            <Text style={styles.cameraPlaceholder}>📷 Camera</Text>
          </View>
          <View style={styles.row}>
            <TouchableOpacity style={styles.btn} onPress={goBack}><Text>← Back</Text></TouchableOpacity>
            <TouchableOpacity style={[styles.btn, styles.primaryBtn]} onPress={nextStep}><Text>Capture</Text></TouchableOpacity>
          </View>
        </View>
      );
      case 5: return (
        <View style={styles.container}>
          <Text style={styles.title}>Live Verification</Text>
          <Text style={styles.subtitle}>Face must match KYC. Blink slowly</Text>
          <View style={styles.cameraBox}>
            <Text style={styles.cameraPlaceholder}>🟢 Live Camera</Text>
          </View>
          <Text style={styles.success}>✓ Face verified</Text>
          <TouchableOpacity style={styles.completeBtn} onPress={() => Alert.alert('Complete', 'KYC submitted!')}>
            <Text style={styles.completeText}>Complete →</Text>
          </TouchableOpacity>
        </View>
      );
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>🐯 TigerEx</Text>
      <Text style={styles.stepText}>Step {step} of 5</Text>
      <View style={styles.progress}><View style={[styles.progressFill, { width: step * 20 + '%' }]} /></View>
      {renderStep()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, background: COLORS.bg, padding: 20 },
  logo: { fontSize: 32, fontWeight: 'bold', color: COLORS.primary, textAlign: 'center', marginBottom: 8 },
  stepText: { textAlign: 'center', color: '#848E9C' },
  progress: { height: 6, background: '#2B3139', borderRadius: 3, marginBottom: 20 },
  progressFill: { height: '100%', background: COLORS.primary, borderRadius: 3 },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 20, textAlign: 'center' },
  subtitle: { color: '#848E9C', textAlign: 'center', marginBottom: 16 },
  docBtn: { flexDirection: 'row', alignItems: 'center', background: COLORS.card, padding: 16, borderRadius: 12, marginBottom: 12 },
  docIcon: { fontSize: 32, marginRight: 16 },
  docName: { fontSize: 18, fontWeight: '600' },
  uploadBtn: { background: COLORS.card, padding: 40, borderRadius: 12, alignItems: 'center', borderWidth: 2, borderStyle: 'dashed', borderColor: '#2B3139' },
  uploadIcon: { fontSize: 48, marginBottom: 8 },
  cameraBox: { background: '#000', aspectRatio: 4/3, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginBottom: 20 },
  cameraPlaceholder: { color: '#fff', fontSize: 24 },
  row: { flexDirection: 'row', gap: 12, marginTop: 20 },
  btn: { flex: 1, padding: 16, background: COLORS.card, borderRadius: 8, alignItems: 'center' },
  primaryBtn: { background: COLORS.primary },
  success: { color: COLORS.success, textAlign: 'center', fontSize: 18, fontWeight: 'bold' },
  completeBtn: { background: COLORS.primary, padding: 16, borderRadius: 8, marginTop: 20 },
  completeText: { color: '#000', fontWeight: 'bold', textAlign: 'center', fontSize: 18 },
});

export default KYCVerification;
