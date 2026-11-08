import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  Modal,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useTheme } from '../../theme';
import {
  useFinanceCategories,
  useCreateCategory,
  useDeleteCategory,
} from '../../hooks/useFinance';
import { FinancialCategory, TransactionType } from '../../types/finance';
import {
  SafeAreaContainer,
  GlassCard,
  Heading,
  BodyText,
  Caption,
  SkeletonLoader,
} from '../../components';

export const FinanceSettingsScreen: React.FC = () => {
  const { theme } = useTheme();
  const navigation = useNavigation();

  const [activeTab, setActiveTab] = useState<TransactionType>('expense');
  const [modalVisible, setModalVisible] = useState(false);
  const [catName, setCatName] = useState('');
  const [catColor, setCatColor] = useState('#6C63FF');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { data: categories, isLoading, refetch } = useFinanceCategories(activeTab);
  const createCatMutation = useCreateCategory();
  const deleteCatMutation = useDeleteCategory();

  const handleCreateCategory = async () => {
    if (!catName.trim()) {
      setErrorMessage('Category name cannot be empty.');
      return;
    }

    try {
      await createCatMutation.mutateAsync({
        name: catName.trim(),
        category_type: activeTab,
        color_hex: catColor,
      });
      setCatName('');
      setModalVisible(false);
    } catch (err: any) {
      setErrorMessage(err?.response?.data?.message || err?.message || 'Failed to create category.');
    }
  };

  const handleDeleteCategory = (cat: FinancialCategory) => {
    if (cat.is_system) {
      Alert.alert('System Category', 'Default system categories cannot be deleted.');
      return;
    }

    Alert.alert('Delete Category', `Are you sure you want to delete "${cat.name}"?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await deleteCatMutation.mutateAsync(cat.id);
          } catch (err: any) {
            Alert.alert(
              'Cannot Delete',
              err?.response?.data?.message || err?.message || 'Failed to delete category.'
            );
          }
        },
      },
    ]);
  };

  const renderCategoryItem = ({ item }: { item: FinancialCategory }) => {
    return (
      <GlassCard style={styles.catCard}>
        <View style={styles.catRow}>
          <View style={[styles.catColorCircle, { backgroundColor: item.color_hex || theme.colors.primary }]} />
          <View style={{ flex: 1, marginLeft: 10 }}>
            <BodyText weight="semiBold">{item.name}</BodyText>
            <Caption color={theme.colors.textMuted}>
              {item.is_system ? 'Built-in Category' : 'Custom Category'}
            </Caption>
          </View>
          {!item.is_system && (
            <TouchableOpacity onPress={() => handleDeleteCategory(item)}>
              <Ionicons name="trash-outline" size={18} color={theme.colors.error} />
            </TouchableOpacity>
          )}
        </View>
      </GlassCard>
    );
  };

  return (
    <SafeAreaContainer>
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.headerRow}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={[styles.iconButton, { backgroundColor: theme.colors.surfaceSubtle }]}
          >
            <Ionicons name="arrow-back" size={20} color={theme.colors.textPrimary} />
          </TouchableOpacity>
          <Heading level={2}>Finance Settings</Heading>
          <TouchableOpacity
            onPress={() => {
              setCatName('');
              setErrorMessage(null);
              setModalVisible(true);
            }}
            style={[styles.iconButton, { backgroundColor: theme.colors.primary }]}
          >
            <Ionicons name="add" size={22} color="#FFFFFF" />
          </TouchableOpacity>
        </View>

        {/* Currency & Privacy Info Card */}
        <GlassCard style={styles.infoCard}>
          <View style={styles.infoRow}>
            <Ionicons name="shield-checkmark-outline" size={20} color={theme.colors.primary} />
            <View style={{ marginLeft: 10, flex: 1 }}>
              <BodyText weight="bold" size="sm">Local & Private Architecture</BodyText>
              <Caption color={theme.colors.textMuted}>
                Currency: USD ($). All arithmetic calculations use exact decimal precision. AI insights run locally on device/server without external APIs.
              </Caption>
            </View>
          </View>
        </GlassCard>

        {/* Tabs for Income / Expense Categories */}
        <View style={styles.tabsRow}>
          <TouchableOpacity
            style={[
              styles.tabBtn,
              activeTab === 'expense' && { borderBottomColor: theme.colors.primary, borderBottomWidth: 2 },
            ]}
            onPress={() => setActiveTab('expense')}
          >
            <BodyText
              weight="bold"
              color={activeTab === 'expense' ? theme.colors.primary : theme.colors.textMuted}
            >
              Expense Categories
            </BodyText>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.tabBtn,
              activeTab === 'income' && { borderBottomColor: theme.colors.primary, borderBottomWidth: 2 },
            ]}
            onPress={() => setActiveTab('income')}
          >
            <BodyText
              weight="bold"
              color={activeTab === 'income' ? theme.colors.primary : theme.colors.textMuted}
            >
              Income Categories
            </BodyText>
          </TouchableOpacity>
        </View>

        {isLoading ? (
          <View style={{ gap: 8, marginTop: 10 }}>
            <SkeletonLoader width="100%" height={60} borderRadius={14} />
            <SkeletonLoader width="100%" height={60} borderRadius={14} />
          </View>
        ) : (
          <FlatList
            data={categories || []}
            keyExtractor={(item) => item.id}
            renderItem={renderCategoryItem}
            contentContainerStyle={styles.listContent}
          />
        )}

        {/* Add Category Modal */}
        <Modal
          visible={modalVisible}
          animationType="slide"
          transparent
          onRequestClose={() => setModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={[styles.modalCard, { backgroundColor: theme.colors.surface }]}>
              <View style={styles.modalHeader}>
                <Heading level={3}>New {activeTab === 'expense' ? 'Expense' : 'Income'} Category</Heading>
                <TouchableOpacity onPress={() => setModalVisible(false)}>
                  <Ionicons name="close" size={22} color={theme.colors.textPrimary} />
                </TouchableOpacity>
              </View>

              {errorMessage && (
                <Caption color={theme.colors.error} style={{ marginBottom: 10 }}>
                  {errorMessage}
                </Caption>
              )}

              <Caption color={theme.colors.textMuted} style={{ marginBottom: 4 }}>
                CATEGORY NAME
              </Caption>
              <TextInput
                style={[styles.input, { borderColor: theme.colors.border, color: theme.colors.textPrimary }]}
                placeholder="e.g. Subscriptions, Consulting"
                placeholderTextColor={theme.colors.textMuted}
                value={catName}
                onChangeText={setCatName}
                autoFocus
              />

              <Caption color={theme.colors.textMuted} style={{ marginTop: 12, marginBottom: 6 }}>
                COLOR PICKER
              </Caption>
              <View style={styles.colorPalette}>
                {['#6C63FF', '#48BB78', '#ED8936', '#E53E3E', '#319795', '#D69E2E', '#805AD5', '#38B2AC'].map(
                  (c) => (
                    <TouchableOpacity
                      key={c}
                      onPress={() => setCatColor(c)}
                      style={[
                        styles.colorChoice,
                        { backgroundColor: c },
                        catColor === c && styles.selectedColorChoice,
                      ]}
                    />
                  )
                )}
              </View>

              <TouchableOpacity
                style={[styles.saveBtn, { backgroundColor: theme.colors.primary }]}
                onPress={handleCreateCategory}
                disabled={createCatMutation.isPending}
              >
                {createCatMutation.isPending ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <BodyText weight="bold" color="#FFFFFF">
                    Add Category
                  </BodyText>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
      </View>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  infoCard: {
    padding: 14,
    borderRadius: 14,
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  tabsRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    marginBottom: 12,
  },
  tabBtn: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
  },
  listContent: {
    paddingBottom: 24,
  },
  catCard: {
    padding: 12,
    borderRadius: 14,
    marginBottom: 8,
  },
  catRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  catColorCircle: {
    width: 24,
    height: 24,
    borderRadius: 12,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    padding: 20,
  },
  modalCard: {
    borderRadius: 20,
    padding: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
  },
  colorPalette: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 20,
  },
  colorChoice: {
    width: 28,
    height: 28,
    borderRadius: 14,
  },
  selectedColorChoice: {
    borderWidth: 3,
    borderColor: '#FFFFFF',
    elevation: 4,
  },
  saveBtn: {
    paddingVertical: 14,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

