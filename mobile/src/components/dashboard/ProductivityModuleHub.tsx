import React from 'react';
import { View, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import { GlassCard, Caption, BodyText } from '../../components';

interface ModuleHubProps {
  onNavigate: (route: string) => void;
}

export const ProductivityModuleHub: React.FC<ModuleHubProps> = ({ onNavigate }) => {
  const { theme } = useTheme();

  const modules = [
    { title: 'Notes', icon: 'document-text-outline', route: 'Notes', color: '#6C63FF' },
    { title: 'Contacts', icon: 'people-outline', route: 'Contacts', color: '#00C853' },
    { title: 'Subs', icon: 'card-outline', route: 'Subscriptions', color: '#FF9100' },
    { title: 'Learning', icon: 'school-outline', route: 'Learning', color: '#00B0FF' },
    { title: 'Travel', icon: 'airplane-outline', route: 'Travel', color: '#E040FB' },
    { title: 'Fitness', icon: 'barbell-outline', route: 'Fitness', color: '#FF5252' },
    { title: 'Assets', icon: 'cube-outline', route: 'Assets', color: '#7C4DFF' },
    { title: 'Bills', icon: 'receipt-outline', route: 'Bills', color: '#00E676' },
    { title: 'Assigned', icon: 'clipboard-outline', route: 'AssignedTasks', color: '#FF4081' },
    { title: 'Money', icon: 'cash-outline', route: 'MoneyTracking', color: '#FFD600' },
    { title: 'Item Lend', icon: 'swap-horizontal-outline', route: 'ItemLending', color: '#00B0FF' },
  ];

  return (
    <GlassCard style={styles.card}>
      <Caption color="secondary" weight="600" style={styles.header}>PRODUCTIVITY MODULES</Caption>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.scroll}>
        {modules.map((m) => (
          <TouchableOpacity
            key={m.route}
            style={styles.moduleItem}
            onPress={() => onNavigate(m.route)}
          >
            <View style={[styles.iconCircle, { backgroundColor: m.color + '22' }]}>
              <Ionicons name={m.icon as any} size={22} color={m.color} />
            </View>
            <Caption weight="600" style={{ marginTop: 4 }}>{m.title}</Caption>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </GlassCard>
  );
};

const styles = StyleSheet.create({
  card: { padding: 14, marginVertical: 8 },
  header: { marginBottom: 10, letterSpacing: 0.5 },
  scroll: { flexDirection: 'row', alignItems: 'center' },
  moduleItem: { alignItems: 'center', marginRight: 16, width: 56 },
  iconCircle: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center' },
});

