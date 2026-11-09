import React, { useState } from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../../theme';
import {
  SafeAreaContainer,
  Heading,
  BodyText,
  Caption,
  GlassCard,
  PrimaryButton,
} from '../../components';
import { useContacts } from '../../hooks/useExtensions';
import { ContactItem } from '../../types/extensions';

export const ContactsScreen: React.FC = () => {
  const { theme } = useTheme();
  const [search, setSearch] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');

  const { data: contacts, isLoading, createContact, deleteContact } = useContacts({
    search: search || undefined,
  });

  const handleSave = async () => {
    if (!name.trim()) return;
    await createContact.mutateAsync({
      name: name.trim(),
      phone: phone.trim() || undefined,
      email: email.trim() || undefined,
      company: company.trim() || undefined,
    });
    setName('');
    setPhone('');
    setEmail('');
    setCompany('');
    setShowCreate(false);
  };

  const renderContact = ({ item }: { item: ContactItem }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardHeader}>
        <View style={styles.avatar}>
          <Heading level={3} style={{ color: theme.colors.primary }}>
            {item.name.charAt(0).toUpperCase()}
          </Heading>
        </View>
        <View style={styles.info}>
          <Heading level={3}>{item.name}</Heading>
          {item.company && <Caption color="secondary">{item.company}</Caption>}
          {item.phone && <Caption color="muted">{item.phone}</Caption>}
        </View>
        <TouchableOpacity onPress={() => deleteContact.mutate(item.id)}>
          <Ionicons name="trash-outline" size={18} color={theme.colors.error || '#FF5252'} />
        </TouchableOpacity>
      </View>
    </GlassCard>
  );

  return (
    <SafeAreaContainer edges={['top']}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Heading level={1}>Contacts</Heading>
          <TouchableOpacity
            style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => setShowCreate(!showCreate)}
          >
            <Ionicons name={showCreate ? 'close' : 'add'} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        <TextInput
          style={[styles.searchInput, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
          placeholder="Search contacts..."
          placeholderTextColor={theme.colors.textMuted}
          value={search}
          onChangeText={setSearch}
        />

        {showCreate && (
          <GlassCard style={styles.createCard}>
            <Heading level={3}>New Contact</Heading>
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Full Name"
              placeholderTextColor={theme.colors.textMuted}
              value={name}
              onChangeText={setName}
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Phone"
              placeholderTextColor={theme.colors.textMuted}
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Email"
              placeholderTextColor={theme.colors.textMuted}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
            />
            <TextInput
              style={[styles.input, { backgroundColor: theme.colors.surface, color: theme.colors.textPrimary }]}
              placeholder="Company"
              placeholderTextColor={theme.colors.textMuted}
              value={company}
              onChangeText={setCompany}
            />
            <PrimaryButton label="Save Contact" onPress={handleSave} loading={createContact.isPending} />
          </GlassCard>
        )}

        <FlatList
          data={contacts || []}
          keyExtractor={(item) => item.id}
          renderItem={renderContact}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            !isLoading ? (
              <View style={styles.empty}>
                <Ionicons name="people-outline" size={48} color={theme.colors.textMuted} />
                <BodyText color="secondary" style={styles.emptyText}>No contacts found</BodyText>
              </View>
            ) : undefined
          }
        />
      </View>
    </SafeAreaContainer>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, paddingHorizontal: 16 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginVertical: 12 },
  addButton: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  searchInput: { padding: 12, borderRadius: 10, marginBottom: 12 },
  createCard: { padding: 16, marginBottom: 12 },
  input: { padding: 10, borderRadius: 8, marginVertical: 4 },
  list: { paddingBottom: 100 },
  card: { padding: 12, marginBottom: 10 },
  cardHeader: { flexDirection: 'row', alignItems: 'center' },
  avatar: { width: 42, height: 42, borderRadius: 21, backgroundColor: '#6C63FF22', justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  info: { flex: 1 },
  empty: { alignItems: 'center', marginTop: 40 },
  emptyText: { marginTop: 8 },
});
