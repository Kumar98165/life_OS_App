import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import { useAutomationTemplates, useExecuteAutomation } from '../../hooks/useAutomations';
import { AutomationTemplate } from '../../types/automation';

export const AutomationTemplatesScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation<any>();
  const { data: templates = [], isLoading } = useAutomationTemplates();
  const executeMutation = useExecuteAutomation();

  const handleLaunchTemplate = async (template: AutomationTemplate) => {
    // Navigate to execution view or run
    try {
      navigation.navigate('AutomationDashboard');
    } catch (e) {
      //
    }
  };

  const renderTemplateCard = ({ item }: { item: AutomationTemplate }) => (
    <View style={[styles.card, { backgroundColor: '#FFFFFF', borderColor: theme.colors.border }]}>
      <View style={styles.badgeRow}>
        <View style={[styles.categoryBadge, { backgroundColor: `${theme.colors.primary}15` }]}>
          <Text style={[styles.categoryText, { color: theme.colors.primary }]}>
            {item.category.toUpperCase()}
          </Text>
        </View>
        <Text style={[styles.triggerText, { color: theme.colors.textSecondary }]}>
          {item.trigger_type === 'scheduled' ? `Auto: ${item.scheduled_days || 'Daily'}` : 'Manual'}
        </Text>
      </View>

      <Text style={[styles.cardTitle, { color: theme.colors.textPrimary }]}>{item.title}</Text>
      <Text style={[styles.cardDesc, { color: theme.colors.textSecondary }]}>
        {item.description}
      </Text>

      <TouchableOpacity
        style={[styles.launchBtn, { backgroundColor: theme.colors.primary }]}
        onPress={() => handleLaunchTemplate(item)}
      >
        <Ionicons name="sparkles" size={14} color="#FFFFFF" />
        <Text style={styles.launchBtnText}>Select Template</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={[styles.header, { borderBottomColor: theme.colors.border }]}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={theme.colors.textPrimary} />
        </TouchableOpacity>
        <View>
          <Text style={[styles.title, { color: theme.colors.textPrimary }]}>Automation Templates</Text>
          <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
            Pre-engineered AI autonomous workflows
          </Text>
        </View>
      </View>

      <FlatList
        data={templates}
        keyExtractor={(item) => item.slug}
        renderItem={renderTemplateCard}
        contentContainerStyle={styles.listContent}
        initialNumToRender={8}
        maxToRenderPerBatch={6}
        windowSize={5}
        removeClippedSubviews={Platform.OS !== 'web'}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
  },
  backBtn: {
    padding: 4,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
  },
  subtitle: {
    fontSize: 12,
    marginTop: 2,
  },
  listContent: {
    padding: 16,
    gap: 14,
  },
  card: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  badgeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  categoryText: {
    fontSize: 10,
    fontWeight: '700',
  },
  triggerText: {
    fontSize: 12,
    fontWeight: '500',
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: '700',
    marginBottom: 6,
  },
  cardDesc: {
    fontSize: 13,
    lineHeight: 18,
    marginBottom: 16,
  },
  launchBtn: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 10,
    borderRadius: 10,
  },
  launchBtnText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 13,
  },
});
