import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Switch,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  useDashboardPreferences,
  useUpdateDashboardPreferences,
  useResetPreferences,
} from '../../hooks/usePersonalization';
import { DashboardWidgetItem } from '../../types/personalization';

interface DashboardCustomizationScreenProps {
  navigation: any;
}

export function DashboardCustomizationScreen({ navigation }: DashboardCustomizationScreenProps) {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();

  const { data: dashboardPrefs, isLoading } = useDashboardPreferences();
  const updateMutation = useUpdateDashboardPreferences();
  const resetMutation = useResetPreferences();

  const [saving, setSaving] = useState(false);

  if (isLoading || !dashboardPrefs) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  const widgets = dashboardPrefs.dashboard_widgets || [];
  const density = dashboardPrefs.dashboard_density || 'comfortable';

  const handleToggleWidget = (id: string, currentVisible: boolean) => {
    const updated = widgets.map((w) =>
      w.id === id ? { ...w, visible: !currentVisible } : w
    );
    saveWidgets(updated);
  };

  const handleMoveUp = (index: number) => {
    if (index <= 0) return;
    const sorted = [...widgets].sort((a, b) => a.order - b.order);
    const temp = sorted[index].order;
    sorted[index].order = sorted[index - 1].order;
    sorted[index - 1].order = temp;
    saveWidgets(sorted);
  };

  const handleMoveDown = (index: number) => {
    const sorted = [...widgets].sort((a, b) => a.order - b.order);
    if (index >= sorted.length - 1) return;
    const temp = sorted[index].order;
    sorted[index].order = sorted[index + 1].order;
    sorted[index + 1].order = temp;
    saveWidgets(sorted);
  };

  const saveWidgets = (newWidgets: DashboardWidgetItem[]) => {
    setSaving(true);
    updateMutation.mutate(
      { dashboard_widgets: newWidgets },
      { onSettled: () => setSaving(false) }
    );
  };

  const handleSetDensity = (newDensity: 'compact' | 'comfortable') => {
    setSaving(true);
    updateMutation.mutate(
      { dashboard_density: newDensity },
      { onSettled: () => setSaving(false) }
    );
  };

  const handleResetToDefault = () => {
    Alert.alert(
      'Reset Dashboard Layout',
      'Restore all dashboard cards to their default order and visibility?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            resetMutation.mutate('dashboard');
          },
        },
      ]
    );
  };

  const sortedWidgets = [...widgets].sort((a, b) => a.order - b.order);

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background, paddingTop: insets.top }]}>
      {/* Header */}
      <View style={[styles.header, { borderBottomColor: theme.colors.border }]}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Ionicons name="arrow-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerTitleContainer}>
          <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Dashboard Layout</Text>
          <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>
            Show, hide, and reorder home screen cards
          </Text>
        </View>
        <TouchableOpacity
          onPress={handleResetToDefault}
          disabled={resetMutation.isPending}
          style={styles.resetButton}
        >
          <Ionicons name="refresh-outline" size={20} color={theme.colors.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Layout Density */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Layout Density</Text>
          <View style={[styles.densityRow, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            <TouchableOpacity
              onPress={() => handleSetDensity('comfortable')}
              style={[
                styles.densityOption,
                density === 'comfortable' && { backgroundColor: `${theme.colors.primary}20` },
              ]}
            >
              <Ionicons
                name="grid-outline"
                size={18}
                color={density === 'comfortable' ? theme.colors.primary : theme.colors.textSecondary}
              />
              <Text
                style={[
                  styles.densityText,
                  { color: density === 'comfortable' ? theme.colors.primary : theme.colors.textPrimary },
                ]}
              >
                Comfortable
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => handleSetDensity('compact')}
              style={[
                styles.densityOption,
                density === 'compact' && { backgroundColor: `${theme.colors.primary}20` },
              ]}
            >
              <Ionicons
                name="list-outline"
                size={18}
                color={density === 'compact' ? theme.colors.primary : theme.colors.textSecondary}
              />
              <Text
                style={[
                  styles.densityText,
                  { color: density === 'compact' ? theme.colors.primary : theme.colors.textPrimary },
                ]}
              >
                Compact
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Widgets Reordering & Visibility */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Dashboard Cards</Text>
            {saving && <ActivityIndicator size="small" color={theme.colors.primary} />}
          </View>
          <Text style={[styles.sectionSubtitle, { color: theme.colors.textSecondary }]}>
            Toggle switches to show or hide cards. Use arrow buttons to move cards up or down.
          </Text>

          <View style={[styles.cardList, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
            {sortedWidgets.map((item, index) => (
              <View
                key={item.id}
                style={[
                  styles.widgetRow,
                  { borderBottomColor: theme.colors.border },
                  index === sortedWidgets.length - 1 && { borderBottomWidth: 0 },
                ]}
              >
                {/* Arrow Reorder Controls */}
                <View style={styles.reorderControls}>
                  <TouchableOpacity
                    onPress={() => handleMoveUp(index)}
                    disabled={index === 0}
                    style={[styles.arrowButton, index === 0 && { opacity: 0.25 }]}
                  >
                    <Ionicons name="chevron-up" size={18} color={theme.colors.textPrimary} />
                  </TouchableOpacity>
                  <TouchableOpacity
                    onPress={() => handleMoveDown(index)}
                    disabled={index === sortedWidgets.length - 1}
                    style={[
                      styles.arrowButton,
                      index === sortedWidgets.length - 1 && { opacity: 0.25 },
                    ]}
                  >
                    <Ionicons name="chevron-down" size={18} color={theme.colors.textPrimary} />
                  </TouchableOpacity>
                </View>

                {/* Title */}
                <View style={styles.widgetInfo}>
                  <Text
                    style={[
                      styles.widgetTitle,
                      { color: item.visible ? theme.colors.textPrimary : theme.colors.textSecondary },
                    ]}
                  >
                    {item.title}
                  </Text>
                  <Text style={[styles.widgetStatus, { color: theme.colors.textSecondary }]}>
                    {item.visible ? `Position #${index + 1}` : 'Hidden from home'}
                  </Text>
                </View>

                {/* Visibility Switch */}
                <Switch
                  value={item.visible}
                  onValueChange={() => handleToggleWidget(item.id, item.visible)}
                  trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
                />
              </View>
            ))}
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  backButton: {
    marginRight: 12,
  },
  headerTitleContainer: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  headerSubtitle: {
    fontSize: 12,
    marginTop: 2,
  },
  resetButton: {
    padding: 6,
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
  },
  sectionSubtitle: {
    fontSize: 13,
    marginBottom: 12,
  },
  densityRow: {
    flexDirection: 'row',
    borderRadius: 12,
    borderWidth: StyleSheet.hairlineWidth,
    overflow: 'hidden',
    padding: 4,
  },
  densityOption: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 10,
    borderRadius: 8,
  },
  densityText: {
    fontSize: 14,
    fontWeight: '600',
  },
  cardList: {
    borderRadius: 14,
    borderWidth: StyleSheet.hairlineWidth,
    overflow: 'hidden',
  },
  widgetRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  reorderControls: {
    flexDirection: 'column',
    alignItems: 'center',
    marginRight: 12,
  },
  arrowButton: {
    padding: 2,
  },
  widgetInfo: {
    flex: 1,
  },
  widgetTitle: {
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 2,
  },
  widgetStatus: {
    fontSize: 12,
  },
});
